"""Interactive document-studio checks using the real private rendering endpoint."""
import base64,json,re,time
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from browser_support import chromium_executable
OUT=Path('tmp/qa/studio');OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 context=b.new_context(viewport={'width':1440,'height':900},accept_downloads=True);page=context.new_page();errors=[];calls=[];renders=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('response',lambda r:renders.append(r.json()) if r.url.endswith('/api/preview') and r.status==200 else None)
 page.on('request',lambda r:calls.append(r.post_data_json) if r.url.endswith('/api/preview') else None)
 page.goto('http://127.0.0.1:5050/create');page.get_by_role('button',name='Try it with a sample biodata').click();page.locator('#confirm-action').click();expect(page.locator('#info-dialog')).not_to_be_visible()
 calls.clear()
 page.get_by_label('Full name',exact=True).fill('Ananya Design Test')
 # Information edits update the visible pane without opening a modal or Design.
 expect(page.locator('#preview-text')).to_contain_text('Ananya Design Test',timeout=65000)
 expect(page.locator('#document-preview')).to_have_attribute('data-state','ready')
 expect(page.locator('#preview-dialog')).not_to_be_visible()
 page.get_by_role('button',name=re.compile('Family')).click()
 page.get_by_label('Father',exact=True).fill('Updated family introduction')
 expect(page.locator('#preview-text')).to_contain_text('Updated family introduction',timeout=65000)
 
 page.locator('[data-field-visibility="family.0.father"]').click()
 expect(page.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
 expect(page.locator('#preview-text')).not_to_contain_text('Updated family introduction')
 page.get_by_role('button',name=re.compile('Design & preview')).click();expect(page.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
 assert page.locator('#preview-template,#template-strip,[data-open-preview]').count()==0
 assert page.locator('.app-header').bounding_box()['height']<=64
 assert page.locator('.brand-caption').count()==0 and page.locator('#skip').is_hidden()
 assert page.locator('.design-filter').count()==5
 expect(page.locator('.design-thumbnail[data-state=ready]')).not_to_have_count(0,timeout=60000)
 page.screenshot(path=str(OUT/'desktop-initial.png'))
 page.locator('[data-design-filter="traditional"]').click();assert page.locator('.design-card').count()==5
 page.locator('[data-template="figma-ganesha-festive"]').click();expect(page.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
 page.screenshot(path=str(OUT/'desktop-traditional.png'))
 assert page.locator('.selected-label:visible').inner_text().endswith('Selected')
 count=int(re.search(r'·\s*(\d+)',page.locator('#page-count').inner_text()).group(1));assert count>0
 for width,height in [(360,800),(390,844),(768,1024),(1024,1366),(1280,800),(1440,900),(1920,1080)]:
  page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(100)
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,'overflow')
  if width>=1280:
   assert page.locator('.workspace>.preview-panel').is_visible()
   assert page.evaluate('document.documentElement.scrollHeight<=innerHeight')
  else:assert page.locator('#mobile-preview').is_visible()
  page.locator('.editor-main').evaluate('(e)=>e.scrollTop=0');page.evaluate('scrollTo(0,0)')
  visible=page.locator('[data-thumbnail]').filter(visible=True)
  for card in visible.all()[:2]:expect(card).to_have_attribute('data-state','ready',timeout=65000)
  page.screenshot(path=str(OUT/f'design-{width}.png'))
  page.locator('#expand-preview' if width>=1280 else '#mobile-preview').click();expect(page.locator('#preview-dialog')).to_be_visible()
  r=page.locator('#document-preview').bounding_box();assert abs(r['width']/r['height']-210/297)<.005
  page.locator('#preview-zoom').click();assert page.locator('#document-preview').bounding_box()['width']==794
  if count>1:
   page.locator('#preview-next').click();expect(page.locator('#preview-page-number')).to_contain_text('2');page.locator('#preview-previous').click()
  page.screenshot(path=str(OUT/f'full-{width}.png'))
  page.keyboard.press('Escape');expect(page.locator('#preview-dialog')).not_to_be_visible()
 page.set_viewport_size({'width':390,'height':844});page.locator('#section-jump').select_option('10');page.locator('#export-consent').check()
 with page.expect_download(timeout=60000) as d:page.locator('#mobile-next').click()
 d.value.save_as(OUT/'selected.pdf')
 assert (OUT/'selected.pdf').read_bytes() in [base64.b64decode(r['pdf']) for r in renders if 'pdf' in r]
 assert all('Ananya Design Test'==r['profile']['sections']['personal']['name'] for r in calls)
 assert not errors,errors
 (OUT/'browser.json').write_text(json.dumps({'pageCount':count,'previewRequests':len(calls),'errors':errors},indent=2))
 b.close()
print('Studio responsive and PDF flow passed')
