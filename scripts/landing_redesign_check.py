from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from browser_support import chromium_executable
out=Path('tmp/qa/landing-redesign');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 for lang in ('en','hi'):
  page=browser.new_page();errors=[];bad=[];api=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  page.on('response',lambda response:bad.append(response.url) if response.status>=400 else None)
  page.on('request',lambda request:api.append(request.url) if '/api/' in request.url else None)
  page.goto('http://127.0.0.1:5050/?lang='+lang,wait_until='networkidle')
  expect(page.locator('h1')).to_have_count(1)
  page.locator('[data-design=professional]').click();expect(page.locator('#collection-image')).to_have_attribute('src',f'/static/artwork/gallery-v1/male-{lang}-professional.webp')
  assert 'design=professional' in page.locator('#use-design').get_attribute('href')
  page.locator('[data-script=hi]').click();expect(page.locator('#language-name')).to_have_text('आरव मेहता')
  page.locator('[data-privacy=phone]').check();expect(page.locator('[data-private-row=phone]')).to_be_visible()
  page.locator('[data-privacy=work]').uncheck();expect(page.locator('[data-private-row=work]')).to_be_hidden()
  page.reload(wait_until='networkidle')
  for width in (1440,1024,768,430,390,360,320):
   page.set_viewport_size({'width':width,'height':900})
   page.evaluate('''async () => {await document.fonts.ready;for(let y=0;y<document.body.scrollHeight;y+=700){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,25));}window.scrollTo(0,0);}''')
   page.wait_for_timeout(150)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(lang,width,'overflow')
   assert page.locator('.landing-header').bounding_box()['height']<=64
   assert page.locator('img').evaluate_all('(images)=>images.every(i=>i.complete&&i.naturalWidth>0)'),(lang,width,'image')
   page.screenshot(path=str(out/f'{lang}-{width}.png'),full_page=True,animations='disabled')
  assert not errors,errors
  assert not bad,bad
  assert not api,api
  page.emulate_media(reduced_motion='reduce')
  assert page.locator('.hero-sheet') .first.evaluate('(e)=>getComputedStyle(e).transitionDuration')=='0s'
  page.close()
 browser.close()
print('English/Hindi interactions, seven widths, images, no overflow, reduced motion and zero API jobs passed.')
