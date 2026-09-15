from pathlib import Path
import re
from playwright.sync_api import sync_playwright,expect
from browser_support import chromium_executable
out=Path('tmp/qa/flower-cursor');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 page=b.new_page(viewport={'width':1440,'height':1000});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:5050/',wait_until='networkidle')
 page.locator('.hero-copy h1').hover();expect(page.locator('.genda-cursor')).to_be_visible()
 assert page.locator('.hero-copy h1').evaluate('(e)=>getComputedStyle(e).cursor')=='none'
 page.locator('.hero-copy .button').hover();expect(page.locator('.genda-cursor')).to_have_class(re.compile(r'(?=.*is-visible)(?=.*is-blooming)(?=.*is-cta-bloom)'))
 assert page.locator('.genda-cursor').evaluate('(e)=>getComputedStyle(e).pointerEvents')=='none'
 page.mouse.down();expect(page.locator('.genda-cursor')).to_have_class(re.compile(r'(?=.*is-cta-bloom)(?=.*is-pressed)'))
 page.mouse.move(100,90);page.mouse.up()
 page.locator('.hero-copy .button').hover();page.wait_for_timeout(800)
 page.locator('.hero').screenshot(path=str(out/'hero-cursor.png'))
 page.locator('.landing-header .brand').hover();expect(page.locator('.genda-cursor')).to_be_hidden()
 assert page.locator('.landing-header .brand').evaluate('(e)=>getComputedStyle(e).cursor')!='none'
 page.locator('#how-it-works h2').hover();expect(page.locator('.genda-cursor')).to_be_hidden()
 page.locator('.hero-copy .button').hover();page.keyboard.press('Tab');expect(page.locator('.genda-cursor')).to_be_hidden()
 page.emulate_media(reduced_motion='reduce');page.locator('.hero-copy .button').hover()
 assert page.locator('.genda-cursor svg').evaluate('(e)=>getComputedStyle(e).transitionDuration')=='0s'
 page.goto('http://127.0.0.1:5050/create');assert page.locator('script[src*="flower-cursor"]').count()==0
 mobile=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 mobile.goto('http://127.0.0.1:5050/');mobile.locator('.hero-copy h1').tap();assert mobile.locator('.genda-cursor.is-visible').count()==0
 assert not errors,errors
 b.close()
print('Hero-only scope, hover/click, keyboard, reduced motion, editor exclusion and touch behavior passed.')
