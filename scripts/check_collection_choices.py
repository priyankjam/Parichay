"""Standalone variant discovery and migration from the former design controls."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.browser_support import chromium_executable
from playwright.sync_api import sync_playwright,expect
from app.models.collection import VARIANTS
out=Path('output/template-collection/browser');out.mkdir(parents=True,exist_ok=True);errors=[];checks=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 for width,height in [(390,844),(1440,900)]:
  c=b.new_context(viewport={'width':width,'height':height},is_mobile=width<768,has_touch=width<768,reduced_motion='reduce');p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:5050/create#section-9')
  expect(p.locator('.design-card')).to_have_count(49);expect(p.locator('.collection-options,[data-presentation],#design-options')).to_have_count(0)
  for variant in VARIANTS:
   button=p.locator(f'[data-template="{variant["id"]}"]');expect(button).to_have_count(1)
  p.locator('[data-template=craft-cathedral-cross]').click();expect(p.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000);p.reload();expect(p.locator('[data-template=craft-cathedral-cross]')).to_have_attribute('aria-pressed','true');expect(p.locator('.collection-options,[data-presentation],#design-options')).to_have_count(0)
  p.evaluate("window.scrollTo({top:0,behavior:'instant'});document.querySelector('.editor-panel')?.scrollTo({top:0,behavior:'instant'})");p.screenshot(path=str(out/f'standalone-designs-{width}.png'),animations='disabled')
  if width>768:
   p.locator('[data-step="1"]').click();expect(p.locator('.design-card')).to_have_count(49);expect(p.locator('.collection-options,[data-presentation],#design-options')).to_have_count(0)
  checks.append({'viewport':[width,height],'cards':49,'controls_removed':True,'selection_restored':True})
  c.close()
 # Saved drafts retain their previous visual choice through one-time migration.
 c=b.new_context(viewport={'width':1440,'height':900});p=c.new_page();p.goto('http://127.0.0.1:5050/create#section-9');expect(p.locator('.design-card')).to_have_count(49)
 for old,art,heading,new in [('craft-ganesha-ivory','none',False,'craft-ivory-saffron'),('craft-sikh-phulkari','khanda',False,'craft-phulkari-khanda'),('craft-ambedkarite-blue','none',True,'craft-equality-jai-bhim')]:
  p.evaluate('''async ({old,art,heading})=>{const cfg=JSON.parse(document.getElementById('app-config').textContent),profile=structuredClone(cfg.demo);profile.template=old;profile.presentation={sacred_art:art,direction:'rtl',salutation:heading};const {openDraftStore}=await import('/static/js/storage.js');const store=await openDraftStore();await store.put({profile,step:9,visited:[9]})}''',{'old':old,'art':art,'heading':heading})
  p.reload();expect(p.locator(f'[data-template="{new}"]')).to_have_attribute('aria-pressed','true');expect(p.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000);checks.append({'legacy':old,'migrated':new})
 b.close();assert not errors,errors
(out/'standalone-choices.json').write_text(json.dumps({'checks':checks,'errors':errors},indent=2));print('PASS standalone choices and old-draft migration')
