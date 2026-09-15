"""Content-heavy mobile/tablet/desktop QA, photo errors and accessible recovery."""
import json
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
from browser_support import chromium_executable
OUT=Path('tmp/qa/redesign');OUT.mkdir(parents=True,exist_ok=True)
SIZES=[(320,568),(360,800),(390,844),(430,932),(768,1024),(1024,1366),(1280,800),(1440,900),(1920,1080),(844,390)]
def jump(page,n):
 page.evaluate('(n)=>{const e=document.querySelector("#section-jump");e.value=n;e.dispatchEvent(new Event("change"))}',str(n))
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 ctx=b.new_context(viewport={'width':390,'height':844},accept_downloads=True);page=ctx.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:5050/create');page.wait_for_selector('[data-for]')
 jump(page,8)
 for payload in [dict(name='too-large.jpg',mimeType='image/jpeg',buffer=b'x'*(8*1024*1024+1)),dict(name='unsupported.heic',mimeType='image/heic',buffer=b'invalid')]:
  page.locator('#photo-input').set_input_files(payload);assert page.locator('#form-error').is_visible();assert not page.locator('#crop-dialog').evaluate('(e)=>e.open')
 Image.new('RGB',(5000,5000),'#98786f').save(OUT/'over-pixel-limit.jpg')
 page.locator('#photo-input').set_input_files(OUT/'over-pixel-limit.jpg')
 page.wait_for_function("()=>document.querySelector('#form-error').textContent.includes('24 megapixels')")
 assert not page.locator('#crop-dialog').evaluate('(e)=>e.open')
 Image.new('RGB',(3600,4000),'#75866d').save(OUT/'large-valid.jpg')
 for _ in range(3):
  with page.expect_file_chooser() as chooser:page.locator('#add-photo').click()
  chooser.value.set_files(OUT/'large-valid.jpg');page.wait_for_selector('#crop-dialog[open]')
  page.locator('#apply-crop').click();page.wait_for_selector('#crop-dialog',state='hidden')
 assert page.locator('.photo-card').count()==3
 page.locator('[data-main-photo="2"]').click();page.locator('[data-remove-photo="1"]').click();page.locator('#confirm-cancel').click()
 assert page.locator('.photo-card').count()==3
 jump(page,3);page.locator('[data-field="personal.0.name"]').fill('अनन्या राव');page.locator('#language').select_option('hi')
 jump(page,4)
 for key,field in [('education','degree'),('career','role')]:
  for i in range(4):
   if i:page.locator(f'[data-add-entry="{key}"]').click()
   page.locator(f'[data-field="{key}.{i}.{field}"]').fill('दीर्घ विवरण — विश्वविद्यालय और संस्थान '+str(i))
 jump(page,7);page.locator('[data-field="about.0.introduction"]').fill('मुझे किताबें पढ़ना और यात्रा करना पसंद है। '*90)
 for w,h in SIZES:
  page.set_viewport_size({'width':w,'height':h})
  for step in [4,7,8,9,10]:
   jump(page,step)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(w,step)
   if step==8:assert page.locator('.photo-card').count()==3
   if step==4:
    assert page.locator('[data-entry]').count()==8
    assert page.locator('[data-entry] summary').first.bounding_box()['height']>=44
   for el in page.locator('button:visible,summary:visible,select:visible').all():
    assert el.bounding_box()['height']>=43,(w,step,el.inner_text(),'small target')
  mobile=w<1100 or h<700
  page.locator('#mobile-preview' if mobile else '#expand-preview').click()
  assert 'अनन्या' in page.locator('#document-preview').inner_text()
  for _ in range(16):
   page.keyboard.press('Tab');assert page.evaluate("document.querySelector('#preview-dialog').contains(document.activeElement)")
  if w in [320,768,1440]:page.screenshot(path=str(OUT/f'long-hindi-popup-{w}.png'))
  page.keyboard.press('Escape')
 # Check landing at all widths after the shared-token updates.
 for w,h in SIZES:
  page.set_viewport_size({'width':w,'height':h});page.goto('http://127.0.0.1:5050/?lang=hi')
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),('landing',w)
 # Storage denial must expose a working backup action and keyboard-accessible restore.
 denied=b.new_context(viewport={'width':320,'height':568},accept_downloads=True)
 denied.add_init_script("Object.defineProperty(window,'indexedDB',{get(){throw new Error('denied')}})")
 d=denied.new_page();d.goto('http://127.0.0.1:5050/create');d.wait_for_selector('#storage-warning:not([hidden])')
 with d.expect_download() as download:d.locator('#storage-backup').click()
 assert download.value.suggested_filename.endswith('.json')
 d.locator('#more-button').click();d.locator('#import-button').focus();assert d.locator('#import-button').evaluate('(e)=>e===document.activeElement')
 d.keyboard.press('Escape');assert d.locator('#more-button').get_attribute('aria-expanded')=='false'
 assert not errors,errors
 b.close();print(json.dumps({'result':'Long Hindi/repeated entries/three large photos at ten viewports, image rejection, keyboard modal and backup recovery passed','errors':errors}))
