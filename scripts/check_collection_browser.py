"""Real browser discovery, optional artwork, autosave, English mobile previews."""
from pathlib import Path
import json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright,expect
from scripts.browser_support import chromium_executable
from app.models.collection import COLLECTION
out=Path('output/template-collection/browser');out.mkdir(exist_ok=True);errors=[];checks=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce',accept_downloads=True)
 p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:5050/create#section-9')
 expect(p.locator('.design-card')).to_have_count(39)
 for d in COLLECTION:
  p.locator('[data-design-filter=all]').click();p.locator(f'[data-template="{d["id"]}"]').click()
  expect(p.locator(f'[data-template="{d["id"]}"]')).to_have_attribute('aria-pressed','true')
  expect(p.locator('#template-name')).to_have_text(d['name'])
  expect(p.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
  p.locator('#m-preview-action').click();expect(p.locator('#preview-dialog')).to_be_visible()
  assert p.locator('#preview-page-image').evaluate('(im)=>im.complete&&im.naturalWidth>0')
  p.screenshot(path=str(out/(d['slug']+'-mobile.png')),animations='disabled')
  p.go_back();expect(p.locator('#preview-dialog')).not_to_be_visible();checks.append({'template':d['id'],'mobile_preview':True})
 # Every cultural category is visible regardless of identity; symbols remain explicit.
 p.locator('[data-template=craft-sikh-phulkari]').click();p.locator('.collection-options summary').click()
 expect(p.locator('[data-presentation=sacred_art]')).to_have_value('none')
 p.locator('[data-presentation=sacred_art]').select_option('ik-onkar');expect(p.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
 p.reload();expect(p.locator('[data-template=craft-sikh-phulkari]')).to_have_attribute('aria-pressed','true');p.locator('.collection-options summary').click();expect(p.locator('[data-presentation=sacred_art]')).to_have_value('ik-onkar')
 p.locator('[data-presentation=sacred_art]').select_option('none');expect(p.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
 p.locator('[data-presentation=direction]').select_option('rtl');p.reload();p.locator('.collection-options summary').click();expect(p.locator('[data-presentation=direction]')).to_have_value('rtl')
 p.screenshot(path=str(out/'mobile-design-options.png'),full_page=True,animations='disabled');c.close()
 # Breakpoint QA keeps real routing and controls. Start with a short fictional draft.
 for width,height in [(320,568),(360,800),(390,844),(430,932),(768,1024),(1024,1366),(1280,800),(1440,900),(1920,1080)]:
  c=b.new_context(viewport={'width':width,'height':height},is_mobile=width<768,has_touch=width<768,reduced_motion='reduce');p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:5050/create#section-9')
  expect(p.locator('.design-card').first).to_be_visible();p.locator('[data-design-filter=regional]').click();expect(p.locator('.design-card')).to_have_count(5)
  assert p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,height)
  p.locator('[data-design-filter=cultural]').click();expect(p.locator('.design-card')).to_have_count(9)
  expect(p.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
  p.screenshot(path=str(out/f'designs-{width}x{height}.png'),full_page=True,animations='disabled');checks.append({'viewport':[width,height],'categories':True,'no_horizontal_page_overflow':True});c.close()
 # Keyboard use and actual user details auto-refresh in the chosen new template.
 c=b.new_context(viewport={'width':1440,'height':900});p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:5050/create#section-3')
 p.locator('[data-field="personal.0.name"]').fill('Private Collection Review');expect(p.locator('#preview-text')).to_contain_text('Private Collection Review',timeout=65000)
 p.locator('[data-step="9"]').click();p.locator('[data-template=craft-ganesha-ivory]').focus();p.keyboard.press('Enter');expect(p.locator('[data-template=craft-ganesha-ivory]')).to_have_attribute('aria-pressed','true');p.locator('.collection-options summary').click();p.locator('[data-presentation=sacred_art]').select_option('none');expect(p.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
 p.locator('[data-step="3"]').click();p.locator('[data-field="personal.0.name"]').fill('Updated Private Review');expect(p.locator('#preview-text')).to_contain_text('Updated Private Review',timeout=65000);expect(p.locator('#preview-text')).not_to_contain_text('Private Collection Review')
 checks.append({'keyboard_selection':True,'live_update':True,'explicit_none':True,'autosave_options':True});c.close();b.close()
 assert not errors,errors
 (out/'report.json').write_text(json.dumps({'checks':checks,'errors':errors},indent=2));print('PASS browser',len(checks),'checks')
