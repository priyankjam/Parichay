"""Information-step live updates, including uninterrupted typing and compact layouts."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from browser_support import chromium_executable
out=Path('tmp/qa/live-preview');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 page=browser.new_page(viewport={'width':1440,'height':900})
 errors=[];calls=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:calls.append(r.post_data_json) if r.url.endswith('/api/preview') else None)
 page.goto('http://127.0.0.1:5050/create')
 page.get_by_role('button',name='Start with my details').click()
 name=page.get_by_label('Full name',exact=True)
 name.fill('Live Preview First')
 expect(page.locator('#preview-text')).to_contain_text('Live Preview First',timeout=65000)
 original=page.locator('#preview-page-image').get_attribute('src')
 name.fill('Live Preview Updated')
 expect(page.locator('#preview-text')).to_contain_text('Live Preview Updated',timeout=65000)
 assert page.locator('#preview-page-image').get_attribute('src')!=original
 # A narrower layout must keep the latest page ready without visiting Design.
 page.set_viewport_size({'width':390,'height':844})
 name.fill('Mobile Updated Information')
 expect(page.locator('#preview-text')).to_contain_text('Mobile Updated Information',timeout=15000)
 page.locator('#mobile-preview').click()
 expect(page.locator('#document-preview')).to_have_attribute('data-state','ready')
 page.keyboard.press('Escape')
 # Continuous typing must not indefinitely defer every preview request.
 calls.clear();name.fill('')
 name.press_sequentially('A long name entered continuously without pausing',delay=90)
 assert any(r['profile']['sections']['personal']['name'] not in ('','A long name entered continuously without pausing') for r in calls), 'No update during uninterrupted typing'
 expect(page.locator('#preview-text')).to_contain_text('A long name entered continuously without pausing',timeout=65000)
 page.set_viewport_size({'width':1440,'height':900})
 # Edits must not send someone reading a later page back to the first sheet.
 page.locator('[data-step="7"]').click()
 intro=page.get_by_label('Your introduction',exact=True)
 intro.fill('I enjoy learning, travelling and spending time with family. '*95)
 expect(page.locator('#document-preview')).to_have_attribute('data-state','loading')
 expect(page.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
 expect(page.locator('#preview-next')).to_be_enabled()
 page.locator('#preview-next').click()
 second=page.locator('#preview-page-image').get_attribute('src')
 intro.fill('UPDATED INTRODUCTION. '+'I enjoy learning, travelling and spending time with family. '*95)
 expect(page.locator('#preview-text')).to_contain_text('UPDATED INTRODUCTION.',timeout=65000)
 expect(page.locator('#preview-page-number')).to_contain_text('Page 2 of')
 assert page.locator('#preview-page-image').get_attribute('src')!=second
 page.screenshot(path=str(out/'information-live.png'))
 assert not errors,errors
 (out/'result.json').write_text(json.dumps({'imageChanged':True,'compactLiveUpdates':True,'continuousTyping':True,'laterPagePreserved':True,'errors':errors},indent=2))
 browser.close()
print('Live preview images update on desktop, compact layouts and continuous typing')
