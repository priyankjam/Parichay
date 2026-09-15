from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from browser_support import chromium_executable
out=Path('tmp/qa/sticky-filters');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 page=b.new_page(viewport={'width':1440,'height':900})
 page.goto('http://127.0.0.1:5050/create')
 for width,height in [(1440,900),(390,844)]:
  page.set_viewport_size({'width':width,'height':height})
  for step in ('1','9'):
   if width>=1280:page.locator(f'[data-step="{step}"]').click()
   else:page.locator('#section-jump').select_option(step)
   page.locator('.editor-main').evaluate('(e)=>e.scrollTop=600') if width>=1280 else page.evaluate('window.scrollTo(0,600)')
   page.wait_for_timeout(200)
   first=page.locator('.design-filters').bounding_box()
   page.locator('.editor-main').evaluate('(e)=>e.scrollTop+=100') if width>=1280 else page.evaluate('window.scrollBy(0,100)')
   page.wait_for_timeout(100)
   second=page.locator('.design-filters').bounding_box()
   assert abs(first['y']-second['y'])<2,(width,step,first,second)
   barrier=page.locator('.editor-main' if width>=1280 else '.mobile-step-navigation').bounding_box()
   if width>=1280:assert abs(second['y']-barrier['y'])<2,(second,barrier)
   assert second['y']>= (barrier['y'] if width>=1280 else barrier['y']+barrier['height'])-1
   page.screenshot(path=str(out/f'{width}-step-{step}.png'))
   page.locator('[data-design-filter="traditional"]').click()
   expect(page.locator('[data-design-filter="traditional"]')).to_have_attribute('aria-pressed','true')
   page.locator('[data-design-filter="all"]').click()
 b.close()
print('Both galleries keep filters pinned on desktop and mobile')
