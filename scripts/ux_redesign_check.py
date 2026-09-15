"""Responsive expert-review matrix and behavior regression checks for the redesign."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_support import chromium_executable
OUT=Path('tmp/qa/redesign');OUT.mkdir(parents=True,exist_ok=True)
SIZES=[(320,568),(360,800),(375,812),(390,844),(412,915),(430,932),(768,1024),(820,1180),(1024,1366),(1280,800),(1440,900),(1600,900),(1920,1080),(844,390)]
URL=os.getenv('APP_URL','http://127.0.0.1:5050')
def jump(page,n):
 page.evaluate('(n)=>{const e=document.querySelector("#section-jump");e.value=n;e.dispatchEvent(new Event("change"))}',str(n))
def reveal(page,selector):
 page.locator(selector).evaluate('(e)=>{for(let p=e.parentElement;p;p=p.parentElement)if(p.tagName==="DETAILS")p.open=true}')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 context=browser.new_context(viewport={'width':390,'height':844},accept_downloads=True)
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(URL);page.locator('.hero-start').click();page.wait_for_selector('[data-for]');page.evaluate('document.fonts.ready')
 rows=[]
 for language in ['en','hi']:
  page.locator('#language').select_option(language)
  for w,h in SIZES:
   page.set_viewport_size({'width':w,'height':h})
   for step in range(11):
    jump(page,step)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(language,w,h,step,'overflow')
    mobile=w<1100 or h<700
    if mobile:
     rect=page.locator('#mobile-next').bounding_box();assert rect and rect['y']>=0 and rect['y']+rect['height']<=h+1,(w,h,step,rect)
     assert not page.locator('.workspace>.preview-panel').is_visible()
    else:
     assert page.evaluate('document.documentElement.scrollHeight<=innerHeight'),(w,h,step,'page scroll')
     last=page.locator('.step-link').last.bounding_box();assert last['y']+last['height']<=h,(language,w,h,last)
    fields=page.locator('[data-field]:visible').count()
    if step==6:assert fields==0,(language,w,'culture not disclosed')
    if step==7:assert fields==2,(language,w,'About contains unrelated fields')
    rows.append({'lang':language,'width':w,'height':h,'step':step,'visibleFields':fields})
    if (w,h) in [(320,568),(390,844),(768,1024),(1024,1366),(1440,900),(1920,1080)] and step in [3,6,7,10]:
     page.screenshot(path=str(OUT/f'{language}-{w}-{step}.png'))
   # Popup stays inset, traps focus, and restores the current step.
   page.locator('#mobile-preview' if mobile else '#expand-preview').click()
   assert page.locator('#preview-dialog').evaluate('(e)=>e.open')
   assert page.locator('#expand-preview').bounding_box()['height']>=44
   page.keyboard.press('Escape');assert not page.locator('#preview-dialog').evaluate('(e)=>e.open')
 page.set_viewport_size({'width':390,'height':844});page.locator('#language').select_option('en')
 jump(page,3);page.locator('[data-field="personal.0.name"]').fill('Ananya Rao')
 page.locator('[data-field="personal.0.age"]').fill('17');page.locator('#mobile-next').click()
 assert page.locator('[data-field="personal.0.age"]').get_attribute('aria-invalid')=='true'
 assert page.locator('[id="personal.0.age-error"]').is_visible()
 page.locator('[data-field="personal.0.age"]').fill('28');page.locator('#mobile-next').click()
 assert page.url.endswith('#section-4');page.go_back();assert page.url.endswith('#section-3')
 assert page.locator('[data-field="personal.0.name"]').input_value()=='Ananya Rao'
 page.go_forward();page.wait_for_selector('[data-field="education.0.degree"]')
 page.locator('[data-field="education.0.degree"]').fill('M.Des')
 
 page.locator('[data-field-visibility="education.0.degree"]').click()
 page.locator('[data-add-entry="education"]').click();page.locator('[data-field="education.1.degree"]').fill('B.Arch')
 page.locator('[data-move-entry="education:1:-1"]').click()
 assert page.locator('[data-field="education.0.degree"]').input_value()=='B.Arch'
 assert page.locator('[data-field-visibility="education.0.degree"]').inner_text()=='Remove'
 reveal(page,'[data-field="education.1.degree"]')
 assert page.locator('[data-field-visibility="education.1.degree"]').inner_text()=='Add back'
 page.locator('[data-remove-entry="education:1"]').click();page.locator('#confirm-cancel').click()
 assert page.locator('[data-field="education.1.degree"]').input_value()=='M.Des'
 page.locator('[data-remove-entry="education:1"]').click();page.locator('#confirm-action').click();page.wait_for_selector('#info-dialog',state='hidden')
 assert page.locator('[data-entry]').count()==2 # education + career
 page.locator('[data-field="career.0.role"]').fill('Designer')
 page.locator('[data-add-entry="career"]').click();page.locator('[data-field="career.1.role"]').fill('Intern')
 jump(page,7);page.locator('[data-field="about.0.introduction"]').fill('I enjoy books and travel. '*100)
 jump(page,3);reveal(page,'[data-field="contact.0.email"]');page.locator('[data-field="contact.0.email"]').fill('invalid@host')
 jump(page,10);page.locator('#export-consent').check();page.locator('#mobile-next').click()
 assert page.url.endswith('#section-3');assert page.locator('[data-field="contact.0.email"]').get_attribute('aria-invalid')=='true'
 page.locator('[data-field="contact.0.email"]').fill('ananya@example.com');page.wait_for_timeout(600);page.reload()
 assert page.locator('[data-field="personal.0.name"]').input_value()=='Ananya Rao'
 assert page.locator('[data-field="contact.0.email"]').input_value()=='ananya@example.com'
 jump(page,9);page.locator('[data-disclosure="custom"]>summary').click();page.locator('#add-custom').click()
 page.locator('[data-custom-title]').fill('Languages');page.locator('[data-custom$=":label"]').fill('Languages spoken');page.locator('[data-custom$=":value"]').fill('English, हिन्दी')
 page.locator('[data-template="ivory"]').first.click();page.locator('[data-open-preview]').click();page.locator('#preview-zoom').click()
 assert page.locator('#preview-scale').bounding_box()['width']>=679
 page.screenshot(path=str(OUT/'mobile-readable-preview.png'));page.keyboard.press('Escape')
 jump(page,10);page.locator('#export-consent').check()
 with page.expect_download() as download:page.locator('#mobile-next').click()
 download.value.save_as(OUT/'journey.pdf');assert (OUT/'journey.pdf').read_bytes().startswith(b'%PDF')
 page.wait_for_selector('#export-result:not([hidden])')
 page.set_viewport_size({'width':1440,'height':900});jump(page,4)
 before=[page.locator(s).bounding_box() for s in ['.app-header','.sidebar','.workspace>.preview-panel']]
 page.locator('#editor-main').evaluate('(e)=>e.scrollTop=500')
 assert before==[page.locator(s).bounding_box() for s in ['.app-header','.sidebar','.workspace>.preview-panel']]
 page.keyboard.press('Tab')
 assert not errors,errors
 (OUT/'results.json').write_text(json.dumps({'screenChecks':len(rows),'errors':errors,'measurements':rows},indent=2))
 browser.close();print(json.dumps({'screenChecks':len(rows),'result':'Responsive matrix, history, validation, safe ordering/removal, draft recovery, preview and PDF passed','errors':errors}))
