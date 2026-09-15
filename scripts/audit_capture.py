"""Read-only baseline inspection; writes measurements/screenshots, never edits profiles on disk."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_support import chromium_executable
OUT=Path('tmp/qa/audit');OUT.mkdir(parents=True,exist_ok=True)
SIZES=[(320,568),(360,800),(375,812),(390,844),(412,915),(430,932),(768,1024),(820,1180),(1024,1366),(1280,800),(1440,900),(1600,900),(1920,1080),(844,390)]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 rows=[]
 for w,h in SIZES:
  page.set_viewport_size({'width':w,'height':h});page.goto('http://127.0.0.1:5050/create');page.wait_for_selector('#section-jump option',state='attached');page.evaluate('document.fonts.ready')
  for step in [0,3,4,6,7,8,10]:
   page.evaluate('(i)=>{const el=document.querySelector("#section-jump");el.value=i;el.dispatchEvent(new Event("change"))}',str(step))
   row=page.evaluate('''()=>({step:document.querySelector('#step-count').textContent,overflow:document.documentElement.scrollWidth>innerWidth,formHeight:document.querySelector('#editor-main').scrollHeight,fields:[...document.querySelectorAll('[data-field]')].filter(e=>e.getClientRects().length).length,nextVisible:document.querySelector('#next').getBoundingClientRect().bottom<=innerHeight,smallTargets:[...document.querySelectorAll('button,select,summary')].filter(e=>e.getClientRects().length&&e.getBoundingClientRect().height<44).length})''');rows.append({'width':w,'height':h,**row})
   if (w,h) in [(320,568),(768,1024),(1440,900)] and step in [3,6,7]:page.screenshot(path=str(OUT/f'before-{w}-{step}.png'))
 page.goto('http://127.0.0.1:5050/');page.locator('.hero-start').click();page.wait_for_selector('#section-jump option',state='attached');page.evaluate('()=>{const e=document.querySelector("#section-jump");e.value=0;e.dispatchEvent(new Event("change"))}');page.locator('#next').click();page.go_back();back=page.url
 (OUT/'baseline.json').write_text(json.dumps({'measurements':rows,'browserBackFromStyle':back,'browserErrors':errors},indent=2))
 b.close();print(json.dumps({'screens':len(rows),'overflow':sum(x['overflow'] for x in rows),'continueBelowViewport':sum(not x['nextVisible'] for x in rows),'backFromStyle':back,'errors':errors}))
