import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.browser_support import chromium_executable
from playwright.sync_api import sync_playwright,expect
out=Path('output/template-collection/browser');errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True);c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce');p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:5050/create#section-9')
 p.locator('[data-template=craft-ganesha-ivory]').click();p.locator('.collection-options summary').click();p.locator('[data-presentation=sacred_art]').select_option('none')
 for template in ['craft-ganesha-ivory','craft-editorial-ivory','craft-braj-krishna','craft-rama-heritage']:
  p.locator(f'[data-template={template}]').click()
  if not p.locator('.collection-options').get_attribute('open'):p.locator('.collection-options summary').click()
  if template!='craft-editorial-ivory':expect(p.locator('[data-presentation=sacred_art]')).to_have_value('none')
 p.reload();p.locator('.collection-options summary').click();expect(p.locator('[data-presentation=sacred_art]')).to_have_value('none')
 p.locator('[data-presentation=sacred_art]').select_option('rama');p.locator('[data-template=craft-nikah-nocturne]').click();expect(p.locator('[data-presentation=sacred_art]')).to_have_count(0)
 assert not errors,errors
 b.close()
(out/'choice-persistence.json').write_text(json.dumps({'explicit_none_across_designs':True,'same_card_preserves_none':True,'reload_preserves_none':True,'incompatible_art_does_not_transfer':True,'errors':errors},indent=2));print('PASS four artwork preference checks')
