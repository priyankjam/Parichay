from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from browser_support import chromium_executable
out=Path('tmp/qa/spotlight');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 page=b.new_page(viewport={'width':1440,'height':900});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:5050/create')
 page.locator('#use-demo').click();page.locator('#confirm-action').click()
 page.locator('[data-step="9"]').click();page.locator('[data-template="figma-ganesha-festive"]').click()
 expect(page.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
 page.locator('#spotlight-toggle').click()
 expect(page.locator('#spotlight-stage #preview-panel')).to_be_visible()
 expect(page.locator('#spotlight-next-page')).to_be_visible()
 expect(page.locator('.design-card')).to_have_count(19)
 assert page.locator('.design-grid').evaluate('(e)=>e.scrollWidth>e.clientWidth')
 assert page.locator('[data-template][aria-pressed=true]').count()==1
 for template in ('figma-ganesha-rose','figma-ganesha-maroon'):
  expect(page.locator(f'[data-thumbnail="{template}"]')).to_have_attribute('data-state','ready',timeout=65000)
 page.screenshot(path=str(out/'desktop.png'))
 page.locator('#expand-preview').click();expect(page.locator('#preview-dialog')).to_be_visible()
 expect(page.locator('#spotlight-next-page')).to_be_hidden()
 page.keyboard.press('Escape');expect(page.locator('#spotlight-stage #preview-panel')).to_be_visible()
 page.locator('[data-template="editorial"]').click()
 expect(page.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
 expect(page.locator('#template-name')).to_have_text('Minimal Editorial')
 page.locator('[data-template="editorial"]').press('ArrowRight');page.keyboard.press('Enter')
 expect(page.locator('[data-template="professional"]')).to_have_attribute('aria-pressed','true')
 for width,height in [(390,844),(768,1024),(1920,1080)]:
  page.set_viewport_size({'width':width,'height':height})
  expect(page.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  box=page.locator('#document-preview').bounding_box();assert box['height']>120 and abs(box['width']/box['height']-210/297)<.002
  if width==390:
   page.locator('#spotlight-toggle').click()
   expect(page.locator('.workspace>#preview-panel')).to_be_hidden()
   page.locator('#spotlight-toggle').click()
   expect(page.locator('#spotlight-stage #preview-panel')).to_be_visible()
  page.screenshot(path=str(out/f'view-{width}.png'))
 page.locator('#spotlight-toggle').click()
 assert page.locator('.workspace>#preview-panel').count()==1
 expect(page.locator('[data-template="professional"]')).to_have_attribute('aria-pressed','true')
 page.locator('[data-step="3"]').click();expect(page.get_by_label('Full name',exact=True)).to_have_value('Aarav Mehta')
 assert not errors,errors
 b.close()
print('Spotlight layout, selection, keyboard, modal return and responsive checks passed')
