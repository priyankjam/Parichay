"""Gallery must display cached samples without waiting on the PDF endpoint."""
import time
from playwright.sync_api import sync_playwright,expect
from browser_support import chromium_executable
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 for width in (1440,390):
  page=browser.new_page(viewport={'width':width,'height':900})
  errors=[];requests=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  page.on('request',lambda request:requests.append(request.post_data_json) if '/api/preview' in request.url else None)
  # A slow/unavailable PDF renderer must never hold up the gallery images.
  page.route('**/api/preview',lambda route:route.fulfill(status=503,body='unavailable'))
  page.goto('http://127.0.0.1:5050/create')
  page.locator('[data-gender="female"]').click()
  page.locator('[data-language="hi"]').click()
  start=time.monotonic()
  if width==1440:page.locator('[data-step="1"]').click()
  else:page.locator('#section-jump').select_option('1')
  page.wait_for_function('''() => [...document.querySelectorAll('[data-thumbnail] img')].filter(img=>{const r=img.getBoundingClientRect();return r.top<innerHeight&&r.bottom>0}).every(img=>img.complete&&img.naturalWidth>0&&!img.hidden)''',timeout=4000)
  elapsed=time.monotonic()-start
  assert page.locator('[data-thumbnail]').count()==19
  assert all('/female-hi-' in src for src in page.locator('[data-thumbnail] img').evaluate_all('(imgs)=>imgs.map(i=>i.getAttribute("src"))'))
  assert not any(r['thumbnail'] for r in requests),requests
  assert not errors,errors
  print(f'{width}px: visible gallery images loaded in {elapsed:.2f}s; no thumbnail PDF jobs',flush=True)
  page.close()
 browser.close()
