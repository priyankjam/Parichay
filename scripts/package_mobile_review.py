"""Build a browsable offline screenshot gallery and ZIP from the capture manifest."""
import html
import json
import math
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/mobile-ux-review'
data=json.loads((OUT/'manifest.json').read_text())
screens=data['screens']
cards=[]
for n,s in enumerate(screens):
    files=s['files'];full=files.get('full',files['viewport'])
    title=html.escape(s['title']);note=html.escape(s['note'])
    cards.append(f'''<article data-lang="{s['language']}" data-group="{s['group']}" data-full="{full}" data-viewport="{files['viewport']}">
      <div class="label"><span>{s['language'].upper()} · {s['group']}</span><h2>{title}</h2></div>
      <button class="shot" aria-label="Open {title}"><img src="{full}" loading="lazy" alt="{title} — mobile screenshot"></button>
      <div class="card-bottom"><p>{note or 'Captured from the working app.'}</p><a href="{full}" target="_blank">Open PNG ↗</a></div></article>''')
template='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Parichay · Mobile UX review</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f2efeb;color:#332932;font:15px/1.55 system-ui,sans-serif}header{padding:48px max(24px,5vw) 24px;border-bottom:1px solid #d9cfce;background:#faf7f3}header small{color:#775264;text-transform:uppercase;letter-spacing:.18em;font-size:11px}h1{font:normal clamp(32px,5vw,52px)/1.12 Georgia,serif;margin:14px 0}header p{max-width:850px;color:#695d63}.tools{display:flex;gap:24px;flex-wrap:wrap;position:sticky;top:0;z-index:2;background:#faf7f3ee;padding:16px max(24px,5vw);border-bottom:1px solid #d9cfce;backdrop-filter:blur(12px)}label{display:flex;gap:10px;align-items:center;font-size:13px}select{padding:10px;border:1px solid #b6a8af;border-radius:8px;background:white;color:#44273a;font:inherit}#count{margin-left:auto;align-self:center;color:#76636d}.grid{padding:28px max(24px,5vw) 64px;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:24px;align-items:start}article{border:1px solid #d9cfce;background:white;border-radius:12px;overflow:hidden;max-width:440px}article[hidden]{display:none}.label{padding:18px;min-height:104px}.label span{font-size:10px;letter-spacing:.1em;color:#816d77;text-transform:uppercase}h2{font-size:16px;line-height:1.4;font-weight:600;margin:8px 0 0}.shot{display:block;width:100%;height:480px;overflow:auto;border:0;border-top:1px solid #e4dbda;border-bottom:1px solid #e4dbda;background:#eee9e4;padding:0;cursor:zoom-in;text-align:left;scrollbar-width:thin}.shot img{display:block;width:100%;height:auto}.card-bottom{padding:16px;font-size:12px}.card-bottom p{min-height:38px;color:#786971;margin:0 0 8px}a{color:#733c57}dialog{border:1px solid #c2b0b8;border-radius:12px;background:#f5f0ed;padding:0;width:min(90vw,540px);max-height:94vh}dialog::backdrop{background:#21171de0}.viewer-head{position:sticky;top:0;display:flex;align-items:center;justify-content:space-between;gap:12px;background:#faf7f3;padding:12px 20px;z-index:1}.viewer-head h2{margin:0;font-size:14px}#close{border:1px solid #c2b0b8;border-radius:8px;background:white;min-height:40px;padding:8px 12px;cursor:pointer}.viewer-image{display:block;width:min(390px,100%);margin:auto}.viewer-foot{padding:12px 20px;text-align:center;font-size:12px}@media(max-width:600px){.tools{gap:10px}.grid{grid-template-columns:1fr}article{max-width:none}.shot{height:520px}#count{display:none}}
</style><header><small>Parichay · Review collection · 15 September 2026</small><h1>The complete mobile journey.</h1><p>SCREEN_COUNT screens and states · FILE_COUNT PNGs · 390 × 844 CSS pixels · English only. Captured in a separate touch-enabled Chrome session using fictional sample information. Your existing draft was not changed.</p><p><strong>Full page:</strong> all scrollable page content; fixed bottom actions are composited once at the bottom so fields stay visible. <strong>First screen:</strong> the unaltered viewport, including sticky controls. Popups use their actual viewport, with lower-content captures where needed. Browser/OS pickers, the native keyboard and native share sheets are outside this collection.</p></header>
<div class="tools"><label>Language <select id="language"><option value="en">English</option></select></label><label>Screens <select id="group"><option value="all">All screens & states</option><option value="Journey">Main journey</option><option value="Dialogs and states">Dialogs & states</option></select></label><label>View <select id="view"><option value="full">Full page</option><option value="viewport">First screen</option></select></label><span id="count"></span></div>
<main class="grid">CARDS</main><dialog id="viewer"><div class="viewer-head"><h2 id="viewer-title"></h2><button id="close">Close ✕</button></div><img id="viewer-image" class="viewer-image" alt=""><div class="viewer-foot"><a id="original" target="_blank">Open original PNG ↗</a></div></dialog>
<script>
const cards=[...document.querySelectorAll('article')],lang=document.querySelector('#language'),group=document.querySelector('#group'),view=document.querySelector('#view'),viewer=document.querySelector('#viewer');
function update(){let count=0;cards.forEach(card=>{card.hidden=!(lang.value==='all'||card.dataset.lang===lang.value)||!(group.value==='all'||card.dataset.group===group.value);if(!card.hidden)count++;const source=card.dataset[view.value];card.querySelector('img').src=source;card.querySelector('a').href=source;card.querySelector('.shot').scrollTop=0;});document.querySelector('#count').textContent=count+' screens';}
[lang,group,view].forEach(el=>el.addEventListener('change',update));cards.forEach(card=>card.querySelector('.shot').addEventListener('click',()=>{const title=card.querySelector('h2').textContent;document.querySelector('#viewer-title').textContent=title;document.querySelector('#viewer-image').src=card.dataset[view.value];document.querySelector('#viewer-image').alt=title;document.querySelector('#original').href=card.dataset[view.value];viewer.showModal();viewer.scrollTop=0;}));document.querySelector('#close').onclick=()=>viewer.close();viewer.addEventListener('click',e=>{if(e.target===viewer&&e.clientX<viewer.getBoundingClientRect().left)viewer.close();});update();
</script></html>'''
count=sum(len(s['files']) for s in screens)
(OUT/'index.html').write_text(template.replace('SCREEN_COUNT',str(len(screens))).replace('FILE_COUNT',str(count)).replace('CARDS','\n'.join(cards)))

journey=[s for s in screens if s['language']=='en' and s['group']=='Journey']
cols=4;tilew=234;tileh=576;gap=24;margin=36
overview=Image.new('RGB',(margin*2+cols*tilew+(cols-1)*gap,130+math.ceil(len(journey)/cols)*(tileh+gap)), '#eee9e5')
draw=ImageDraw.Draw(overview)
fontpath='/System/Library/Fonts/Supplemental/Arial.ttf'
font=ImageFont.truetype(fontpath,16);titlefont=ImageFont.truetype(fontpath,30)
draw.text((36,25),'Parichay · Mobile UX review',font=titlefont,fill='#513247')
draw.text((36,72),'Landing + all 10 steps  /  390 × 844  /  Open index.html for full pages and all states',font=font,fill='#76636d')
for i,s in enumerate(journey):
    x=margin+(i%cols)*(tilew+gap);y=130+(i//cols)*(tileh+gap)
    shot=Image.open(OUT/s['files']['viewport']).convert('RGB').resize((tilew,506),Image.Resampling.LANCZOS)
    overview.paste(shot,(x,y+50));title=s['title']
    if len(title)>27:
        cut=title.rfind(' ',0,27);title=title[:cut]+'\n'+title[cut+1:]
    draw.text((x,y),title,font=font,fill='#513247')
overview.save(OUT/'overview.png')
(OUT/'README.txt').write_text(f'''PARICHAY — MOBILE UX REVIEW
Captured 15 September 2026 at 390 × 844 CSS pixels in mobile Chrome emulation.
{len(screens)} screens/states; {count} screen PNGs, plus overview.png.

Open index.html in a browser to browse, filter, enlarge and download images.
Includes the landing page, all 10 steps, Spotlight and full preview.
English adds empty forms, optional groups, field/section hiding, custom sections,
photo cropping, draft/confirmation/privacy dialogs and download/share states.

*-viewport.png: unaltered first-screen or dialog screenshot.
*-full.png: all page content. The sticky bottom dock is composited once at the
bottom from actual screen pixels so it does not cover fields midway down the page.
Popups with scrolling have a second lower-content screenshot where needed.
Fictional sample information is used in editor captures. No personal draft touched.

Native OS file pickers, keyboard and system share sheets are not emulated.
These are captures of the current implementation, not redesign mockups or a UX audit.
''')
archive=OUT.parent/'parichay-mobile-ux-review.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for file in OUT.rglob('*'):
        if file.is_file():z.write(file,Path('mobile-ux-review')/file.relative_to(OUT))
print(json.dumps({'screens':len(screens),'pngs':count,'zip':str(archive),'zipMB':round(archive.stat().st_size/1048576,2),'errors':data['browserErrors']},indent=2))
