"""All-template switching, privacy, responsive gallery and export regression."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from browser_support import chromium_executable
OUT=Path('tmp/qa/figma/browser');OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 context=b.new_context(viewport={'width':1440,'height':900},accept_downloads=True);page=context.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:5050/create?design=figma-peach-floral');page.wait_for_selector('[data-for]')
 assert page.locator('#document-preview .doc-portrait').count()==1
 assert 'design=' not in page.url
 def jump(i):page.evaluate('(i)=>{const e=document.querySelector("#section-jump");e.value=i;e.dispatchEvent(new Event("change"))}',str(i))
 jump(3);page.locator('[data-field="personal.0.name"]').fill('Ananya Rao');page.locator('[data-field="personal.0.city"]').fill('Pune')
 expect(page.locator('#document-preview h1')).to_have_text('Ananya Rao')
 assert page.locator('#document-preview .doc-portrait').count()==0, 'Demo photo must not enter a user draft'
 jump(8);page.locator('#photo-input').set_input_files('app/static/artwork/demo-portrait.jpg')
 page.wait_for_selector('#crop-dialog[open]');page.locator('#apply-crop').click()
 jump(5);page.locator('[data-field="family.0.father"]').fill('PRIVATE FATHER');page.locator('[data-visibility-section="family"]').click();page.locator('[data-visible="family.0.father"]').uncheck()
 jump(9);assert page.locator('.design-card').count()==19
 page.locator('[data-design-filter="Ganesha"]').click();assert page.locator('.design-card').count()==4
 page.locator('[data-template="figma-ganesha-maroon"]').first.click();page.locator('[data-open-preview]').click()
 for option in page.locator('#preview-template option').all():
  id=option.get_attribute('value');page.locator('#preview-template').select_option(id)
  assert page.locator('#document-preview h1').inner_text()=='Ananya Rao'
  assert page.locator('#document-preview .doc-portrait').count()==1
  assert 'PRIVATE FATHER' not in page.locator('#document-preview').inner_text()
  assert page.locator('#preview-dialog').evaluate('(e)=>e.open')
 page.locator('#preview-template').select_option('figma-ganesha-rose');page.keyboard.press('Escape')
 for w,h in [(320,568),(390,844),(768,1024),(1024,1366),(1440,900),(1920,1080)]:
  page.set_viewport_size({'width':w,'height':h});page.locator('[data-design-filter="all"]').click()
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.wait_for_timeout(300);page.screenshot(path=str(OUT/f'gallery-{w}.png'))
  page.locator('#mobile-preview' if w<1100 else '#expand-preview').click()
  assert page.locator('#preview-template').bounding_box()['height']>=44
  assert page.locator('#preview-template').bounding_box()['x']>=0
  page.wait_for_timeout(300);page.screenshot(path=str(OUT/f'preview-{w}.png'));page.keyboard.press('Escape')
 page.set_viewport_size({'width':390,'height':844});jump(3);page.locator('#language').select_option('hi');page.locator('[data-field="personal.0.name"]').fill('अनन्या राव');page.wait_for_timeout(600);page.reload()
 assert page.locator('[data-field="personal.0.name"]').input_value()=='अनन्या राव'
 page.locator('#mobile-preview').click();assert page.locator('#preview-template').input_value()=='figma-ganesha-rose'
 page.locator('#preview-template').select_option('figma-peach-floral');page.keyboard.press('Escape')
 jump(10);page.locator('#export-consent').check()
 with page.expect_download(timeout=65000) as d:page.locator('#mobile-next').click()
 d.value.save_as(OUT/'download.pdf');assert (OUT/'download.pdf').read_bytes().startswith(b'%PDF')
 assert not errors,errors
 b.close();print(json.dumps({'result':'19 templates, filters, all-template modal switching, hidden data, six viewport sizes, Hindi reload and PDF passed','errors':errors}))
