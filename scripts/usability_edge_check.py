"""Observed edge behavior, separate from inferred persona reactions."""
import json,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from browser_support import chromium_executable
MODE=sys.argv[1] if len(sys.argv)>1 else 'before';OUT=Path('tmp/qa/usability')/MODE;OUT.mkdir(parents=True,exist_ok=True)
report={}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 context=b.new_context(viewport={'width':390,'height':844},accept_downloads=True);page=context.new_page()
 page.goto('http://127.0.0.1:5050/create');page.get_by_role('button',name='Start with my details',exact=True).click()
 page.get_by_label('Full name',exact=True).fill('Ananya Rao');page.get_by_label('Age',exact=True).fill('28');page.wait_for_timeout(600)
 # Preview browser-back behavior: make a second editor step, then open popup.
 page.get_by_role('button',name='Continue',exact=True).filter(visible=True).click()
 previous=page.url;page.get_by_role('button',name='Preview',exact=True).click();page.go_back()
 report['preview_browser_back']={'before':previous,'after':page.url,'dialog_open':page.get_by_role('dialog').filter(visible=True).count()}
 page.keyboard.press('Escape');page.goto('http://127.0.0.1:5050/create#section-3');page.get_by_label('Full name',exact=True).wait_for()
 # Five immediate refreshes, without a test-only debounce delay.
 restores=[]
 for i in range(5):
  value=f'Immediate save {i}';page.get_by_label('Full name',exact=True).fill(value);page.reload();page.get_by_label('Full name',exact=True).wait_for();restores.append({'typed':value,'restored':page.get_by_label('Full name',exact=True).input_value()})
 report['immediate_refresh']=restores
 # Actual Chromium pinch/page scale, not a fabricated keyboard event.
 cdp=context.new_cdp_session(page);cdp.send('Emulation.setPageScaleFactor',{'pageScaleFactor':2});page.wait_for_timeout(200)
 report['pinch_zoom']={'scale':page.evaluate('visualViewport.scale'),'dock_visible':page.get_by_role('button',name='Continue',exact=True).filter(visible=True).count()>0,'keyboard_class':page.locator('body').get_attribute('class')}
 cdp.send('Emulation.setPageScaleFactor',{'pageScaleFactor':1})
 page.get_by_label('Full name',exact=True).focus();page.keyboard.press('Enter')
 report['input_enter']={'focused_label':page.evaluate('document.activeElement.labels?.[0]?.textContent'),'enterkeyhint':page.get_by_label('Full name',exact=True).get_attribute('enterkeyhint')}
 # Visible actions under 200% text sizing, desktop layout and all target sizes.
 page.set_viewport_size({'width':1440,'height':900});page.add_style_tag(content='html{font-size:200%}')
 last=page.get_by_role('button',name=__import__('re').compile('Export & share|Download & share')).bounding_box() if MODE=='before' else page.get_by_label('Go to section').bounding_box()
 report['text_200']={'last_section':last,'viewport_height':900,'compact':page.locator('body').get_attribute('class'),'jump_visible':page.get_by_label('Go to section').is_visible(),'body_overflow':page.evaluate('document.documentElement.scrollHeight>innerHeight')}
 page.screenshot(path=str(OUT/'text-200.png'),animations='disabled')
 # Wrong image and successful recovery using the visible photo workflow.
 page.goto('http://127.0.0.1:5050/create#section-8');page.get_by_role('button',name=__import__('re').compile('Choose a photo')).wait_for()
 chooser=page.locator('input[type=file][accept="image/jpeg,image/png,image/webp"]')
 chooser.set_input_files({'name':'notes.txt','mimeType':'text/plain','buffer':b'not a photo'});page.wait_for_timeout(150)
 error=page.locator('#form-error');report['wrong_photo']={'text':error.inner_text(),'rect':error.bounding_box(),'height':page.viewport_size['height']}
 # Low-resolution warning lifetime after opening the crop.
 from PIL import Image
 import io
 photo=io.BytesIO();Image.new('RGB',(100,125),'#bda').save(photo,'JPEG')
 chooser.set_input_files({'name':'small.jpg','mimeType':'image/jpeg','buffer':photo.getvalue()});page.get_by_role('dialog').filter(visible=True).wait_for()
 report['small_photo_warning']={'quality_visible':page.locator('#crop-quality').is_visible() if MODE=='after' else False,'toast_visible':page.locator('#toast').is_visible(),'crop_copy':page.get_by_role('dialog').filter(visible=True).inner_text()}
 page.keyboard.press('Escape')
 # Observe real viewport geometry at every requested size.
 report['sizes']=[]
 for w,h in [(320,568),(360,800),(390,844),(412,915),(768,1024),(1024,1366),(1280,800),(1440,900),(1920,1080),(844,390)]:
  page.set_viewport_size({'width':w,'height':h});report['sizes'].append({'width':w,'height':h,'overflow':page.evaluate('document.documentElement.scrollWidth>innerWidth')})
 context.close()
 # Slow cold start and local input response on a separate browser context.
 slow=b.new_context(viewport={'width':320,'height':568});page=slow.new_page();cdp=slow.new_cdp_session(page)
 cdp.send('Network.enable');cdp.send('Network.emulateNetworkConditions',{'offline':False,'latency':300,'downloadThroughput':50000,'uploadThroughput':25000,'connectionType':'cellular3g'});cdp.send('Emulation.setCPUThrottlingRate',{'rate':4})
 started=time.monotonic();page.goto('http://127.0.0.1:5050/');page.get_by_role('link',name='Create your biodata',exact=True).first.click();page.get_by_role('button',name='Start with my details',exact=True).click();ready=time.monotonic()-started
 started=time.monotonic();page.get_by_label('Full name',exact=True).fill('Slow network test');page.wait_for_timeout(400);latency=time.monotonic()-started
 report['slow_network']={'cold_landing_to_form_seconds':round(ready,2),'input_plus_400ms_wait_seconds':round(latency,2),'network':'300ms latency, 400kbps down, 200kbps up; 4x CPU slowdown'}
 b.close()
if MODE=='after':
 assert all(x['typed']==x['restored'] for x in report['immediate_refresh']),report['immediate_refresh']
 assert report['preview_browser_back']['dialog_open']==0 and report['preview_browser_back']['before']==report['preview_browser_back']['after']
 assert report['pinch_zoom']['dock_visible']
 assert report['text_200']['jump_visible']
 assert report['small_photo_warning']['quality_visible']
 assert report['input_enter']['focused_label']=='Age'
 assert not any(x['overflow'] for x in report['sizes']),report['sizes']
(OUT/'edges.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
