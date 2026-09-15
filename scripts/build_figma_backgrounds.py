"""Render the inspected Figma background layers using their original bitmap assets.
No profile text, example portraits or user draft content is part of this pipeline.
"""
import io,json
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
from browser_support import chromium_executable
root=Path(__file__).resolve().parents[1]
def background_html(d):
 layers=[]
 for l in d['layers']:
  x,y,w,h=l['box'];left,top,iw,ih=l['image']
  import base64
  src='data:image/webp;base64,'+base64.b64encode((root/'app/static/artwork'/f"{l['asset']}.webp").read_bytes()).decode()
  layers.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;overflow:hidden;transform:{"scaleY(-1)" if l["flip"] else "none"}"><img src="{src}" style="position:absolute;max-width:none;left:{left}%;top:{top}%;width:{iw}%;height:{ih}%"></div>')
 if d.get('border'):layers.append(f'<div style="position:absolute;inset:10px;border:2px solid {d["border"]};border-radius:5px"></div>')
 if d.get('stripe'):layers.append(f'<div style="position:absolute;inset:0 0 auto;height:8px;background:{d["stripe"]}"></div>')
 return f'<html><body style="margin:0;background:{d["paper"]};overflow:hidden">'+''.join(layers)+'</body></html>'
if __name__=='__main__':
 out=root/'app/static/artwork/templates';out.mkdir(exist_ok=True)
 designs=json.loads((root/'app/biodata_templates/figma.json').read_text())
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
  for d in designs:
   page=browser.new_page(viewport={'width':595,'height':d.get('height',842)},device_scale_factor=2)
   page.set_content(background_html(d),wait_until='load')
   png=page.screenshot();page.close()
   with Image.open(io.BytesIO(png)) as im:
    rgb=im.convert('RGB');rgb.save(out/(d['id']+'.webp'),'WEBP',quality=92,method=6)
    rgb.save(out/(d['id']+'.jpg'),'JPEG',quality=92,optimize=True)
  browser.close()
 print('Rendered',len(designs),'backgrounds from original Figma artwork')
