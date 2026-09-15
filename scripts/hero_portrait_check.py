from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_support import chromium_executable
out=Path('tmp/qa/hero-refinement');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 page=b.new_page()
 for width in (1440,768,390,320):
  page.set_viewport_size({'width':width,'height':1000});page.goto('http://127.0.0.1:5050/',wait_until='networkidle')
  page.locator('.hero-collection').scroll_into_view_if_needed()
  # Map portrait samples through each sheet's CSS rotation and confirm the
  # front document does not cover the rear portrait's center or corners.
  for selector in ('.sheet-floral','.sheet-ivory'):
   visible=page.locator(selector).evaluate('''el => {
    const r=el.getBoundingClientRect(),w=el.offsetWidth,h=el.offsetHeight,m=new DOMMatrix(getComputedStyle(el).transform);
    return [[.75,.26],[.94,.26],[.75,.4],[.94,.4],[.845,.33]].every(([x,y])=>{
     const dx=(x-.5)*w,dy=(y-.5)*h;
     const px=r.x+r.width/2+m.a*dx+m.c*dy,py=r.y+r.height/2+m.b*dx+m.d*dy;
     const hit=document.elementFromPoint(px,py);return hit&&el.contains(hit);
    });
   }''')
   assert visible,(width,selector,'portrait obscured')
  rear=page.locator('.sheet-floral').bounding_box();front=page.locator('.sheet-ivory').bounding_box()
  assert page.locator('.sheet-floral').evaluate('(e)=>e.offsetTop')==page.locator('.sheet-ivory').evaluate('(e)=>e.offsetTop'),(width,'not aligned')
  page.locator('.hero-collection').screenshot(path=str(out/f'hero-{width}.png'))
 b.close()
print('Both portrait areas are unobstructed at desktop, tablet and narrow mobile widths.')
