"""Recovery, hidden-data transmission, generation races and Hindi accessibility."""
import json,re
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from browser_support import chromium_executable
OUT=Path('tmp/qa/studio');OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 page=b.new_page(viewport={'width':390,'height':844});errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:requests.append(r.post_data_json) if r.url.endswith('/api/preview') else None)
 page.goto('http://127.0.0.1:5050/create');page.get_by_role('button',name='Start with my details').click();page.get_by_label('Full name',exact=True).fill('Private Preview Test')
 page.locator('#section-jump').select_option('5');page.get_by_label('Father',exact=True).fill('NEVER TRANSMIT THIS');page.locator('[data-field-visibility="family.0.father"]').click()
 # Server failure leaves selected design and local data intact, with explicit retry.
 page.route('**/api/preview',lambda route:route.fulfill(status=503,content_type='application/json',body='{"error":"busy"}'))
 page.locator('#section-jump').select_option('9');page.locator('#mobile-preview').click();expect(page.locator('#document-preview')).to_have_attribute('data-state','error');expect(page.locator('#preview-retry')).to_be_visible()
 page.screenshot(path=str(OUT/'preview-error-mobile.png'));page.unroute('**/api/preview');page.locator('#preview-retry').click();expect(page.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
 assert 'Private Preview Test' in page.locator('#preview-text').inner_text()
 assert all('NEVER TRANSMIT THIS' not in json.dumps(r) for r in requests)
 page.go_back();expect(page.locator('#preview-dialog')).not_to_be_visible();assert page.url.endswith('#section-9')
 # Update data while an older full render is in flight; its result cannot replace the new generation.
 cdp=page.context.new_cdp_session(page);cdp.send('Network.enable');cdp.send('Network.emulateNetworkConditions',{'offline':False,'latency':600,'downloadThroughput':-1,'uploadThroughput':-1})
 page.locator('#section-jump').select_option('3');page.get_by_label('Full name',exact=True).fill('Superseded Draft')
 page.locator('#section-jump').select_option('9');page.wait_for_timeout(80)
 page.locator('#section-jump').select_option('3');page.get_by_label('Full name',exact=True).fill('Latest Draft Only')
 page.locator('#section-jump').select_option('9');page.locator('#mobile-preview').click()
 expect(page.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000);expect(page.locator('#preview-text')).to_contain_text('Latest Draft Only');assert 'Superseded Draft' not in page.locator('#preview-text').inner_text()
 cdp.send('Network.emulateNetworkConditions',{'offline':False,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1});page.keyboard.press('Escape');expect(page.locator('#preview-dialog')).not_to_be_visible()
 # Hindi keeps all controls named, selection announced and categories on one row.
 page.locator('#language').select_option('hi');page.locator('#section-jump').select_option('3');page.get_by_label('पूरा नाम',exact=True).fill('अनन्या शर्मा');page.locator('#section-jump').select_option('9');page.locator('[data-design-filter="modern"]').click();page.locator('[data-template="professional"]').press('Enter');expect(page.locator('[data-template="professional"]')).to_have_attribute('aria-pressed','true')
 page.locator('#mobile-preview').click();expect(page.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000);expect(page.locator('#preview-text')).to_contain_text('अनन्या शर्मा');assert page.locator('#preview-next').get_attribute('aria-label')=='अगला पन्ना'
 page.screenshot(path=str(OUT/'hindi-full.png'));page.keyboard.press('Escape');expect(page.locator('#preview-dialog')).not_to_be_visible()
 for width,height in [(360,800),(390,844),(768,1024),(1024,1366),(1280,800),(1440,900),(1920,1080)]:
  page.set_viewport_size({'width':width,'height':height});page.add_style_tag(content='html{font-size:200%}');page.wait_for_timeout(100)
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  assert page.locator('#section-jump').is_visible()
  boxes=[x.bounding_box() for x in page.locator('.design-filter').all()];assert max(x['y'] for x in boxes)-min(x['y'] for x in boxes)<2
 page.emulate_media(reduced_motion='reduce');assert page.locator('.design-thumbnail').first.evaluate('(e)=>getComputedStyle(e).animationName')=='none'
 assert not errors,errors
 (OUT/'state.json').write_text(json.dumps({'requests':len(requests),'hiddenFieldsTransmitted':False,'raceProtection':True,'Hindi':True,'enlargedTextViews':7,'errors':errors},indent=2))
 b.close()
print('Recovery, privacy, stale-response protection and Hindi accessibility passed')
