"""Responsive and interaction checks for the landing-only paper-craft hero."""
import json,io
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright,expect
from browser_support import chromium_executable
OUT=Path('tmp/qa/hero-craft');OUT.mkdir(parents=True,exist_ok=True)
SIZES=[(320,568),(360,800),(390,844),(430,932),(768,1024),(1024,1366),(1280,800),(1440,900),(1920,1080)]
results=[];errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 for w,h in SIZES:
  context=b.new_context(viewport={'width':w,'height':h},is_mobile=w<=1024,has_touch=w<=1024,device_scale_factor=1)
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:5050/',wait_until='networkidle');page.evaluate('document.fonts.ready');page.wait_for_timeout(1700)
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(w,'overflow')
  assert page.locator('.hero-sheet img').evaluate_all('(els)=>els.every(i=>i.complete&&i.naturalWidth>=800)')
  for image in page.locator('.hero-sheet img').all():
   assert abs(image.evaluate('(e)=>e.clientWidth/e.clientHeight')-210/297)<.012
  paper=page.locator('.primary-position').bounding_box();caption=page.locator('.hero-collection figcaption').bounding_box()
  assert paper['y']+paper['height']<caption['y']-8,(w,'paper overlaps selectors')
  rect=page.locator('.editorial-hero').bounding_box()
  full=Image.open(io.BytesIO(page.screenshot(full_page=True,animations='disabled')))
  full.crop((0,0,w,int(rect['y']+rect['height']))).save(OUT/f'hero-{w}.png')
  page.screenshot(path=str(OUT/f'viewport-{w}.png'),animations='disabled')
  assert page.locator('.hero-copy .button').get_attribute('href').startswith('/create?lang=en')
  assert page.locator('.hero-copy .text-link').get_attribute('href')=='#designs'
  if w<=1024:
   page.locator('[data-hero-style=editorial]').tap()
   expect(page.locator('#hero-primary-image')).to_have_attribute('src', 'http://127.0.0.1:5050/static/artwork/hero-craft-editorial-en.webp')
   assert page.locator('.craft-cursor').count()==0
   assert page.locator('.editorial-hero').evaluate('(e)=>getComputedStyle(e).getPropertyValue("--px").trim()')=='0'
  results.append({'width':w,'height':h,'overflow':False,'touch':w<=1024})
  context.close()
 page=b.new_page(viewport={'width':1440,'height':900});page.goto('http://127.0.0.1:5050/',wait_until='networkidle');page.wait_for_timeout(1700)
 for variant in ('botanical','architectural','textile'):
  page.locator('.editorial-hero').evaluate('(e,v)=>e.dataset.artVariant=v',variant)
  page.screenshot(path=str(OUT/f'variant-{variant}.png'))
 page.locator('.editorial-hero').evaluate('(e)=>{e.dataset.artVariant="architectural";e.dataset.decoration="rich"}')
 page.screenshot(path=str(OUT/'variant-rich.png'))
 page.locator('.editorial-hero').evaluate('(e)=>delete e.dataset.decoration')
 # Pointer, hover and keyboard affordances, with actual routing verification.
 page.mouse.move(500,200);page.wait_for_timeout(250)
 expect(page.locator('.craft-cursor')).to_have_count(1)
 assert abs(float(page.locator('.editorial-hero').evaluate('(e)=>e.style.getPropertyValue("--px")')))<=1
 page.locator('#hero-primary-design').hover();page.wait_for_timeout(400)
 expect(page.locator('.craft-label')).to_have_text('View design ↗')
 assert page.locator('#hero-primary-design').evaluate('(e)=>getComputedStyle(e).transform').startswith('matrix(1, 0, 0, 1, 0, -5)')
 page.screenshot(path=str(OUT/'mouse-document-hover.png'))
 page.keyboard.press('Tab');expect(page.locator('.craft-cursor')).to_have_count(0)
 page.locator('[data-hero-style=traditional]').focus();page.keyboard.press('Enter')
 expect(page.locator('[data-hero-style=traditional]')).to_have_attribute('aria-pressed','true')
 expect(page.locator('#hero-primary-design')).to_have_attribute('href', 'http://127.0.0.1:5050/create?lang=en&design=traditional')
 assert page.locator('[data-hero-style=traditional]').evaluate('(e)=>getComputedStyle(e).outlineStyle')!='none'
 page.screenshot(path=str(OUT/'keyboard-classic.png'))
 # Wheel events model mouse-wheel / trackpad scroll behavior, not a physical device.
 page.mouse.move(300,200);page.mouse.wheel(0,700);page.wait_for_timeout(300)
 expect(page.locator('.craft-cursor')).to_have_count(0)
 page.evaluate('scrollTo(0,0)');page.emulate_media(reduced_motion='reduce');page.wait_for_timeout(400);page.mouse.move(601,201);page.mouse.move(600,200);page.wait_for_timeout(100)
 assert page.locator('.paper-position').first.evaluate('(e)=>getComputedStyle(e).transform')=='none'
 assert page.locator('.hero-sheet').first.evaluate('(e)=>getComputedStyle(e).animationName')=='none'
 assert page.locator('.craft-cursor').evaluate('(e)=>getComputedStyle(e).transform')=='matrix(1, 0, 0, 1, 600, 200)'
 page.screenshot(path=str(OUT/'reduced-motion.png'))
 page.locator('#hero-primary-design').click();expect(page).to_have_url('http://127.0.0.1:5050/create#section-0');expect(page.locator('#template-name')).to_have_text('Elegant Traditional')
 b.close()
assert not errors,errors
before=(OUT/'landing-before.html').read_text().split('<div class="trust-strip">',1)[1]
after=Path('app/templates/landing.html').read_text().split('<div class="trust-strip">',1)[1]
assert before==after,'Content below the hero changed'
(OUT/'results.json').write_text(json.dumps({'viewports':results,'errors':errors,'unrelatedContentUnchanged':True,'interactions':['mouse hover','keyboard selection and focus','touch taps','wheel scroll','reduced motion','design routing']},indent=2))
print('Nine viewports and hero interactions passed. Unrelated landing content unchanged.')
