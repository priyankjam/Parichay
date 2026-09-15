"""Mobile state, accessibility, viewport and desktop-isolation regressions.

Viewport tests replay a real PDF fixture to avoid hundreds of renderer jobs.
mobile_product_check.py separately exercises the live renderer and download.
"""
import base64
import io
import json
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageChops
from playwright.sync_api import expect, sync_playwright
from browser_support import chromium_executable

OUT = Path('tmp/qa/mobile-redesign')
URL = 'http://127.0.0.1:5050/create'
STEPS = [0, 3, 4, 5, 7, 6, 8, 9, 10]
checks, errors, metrics = [], [], []
pdf = (OUT / 'mobile-flow.pdf').read_bytes()
document = pdfium.PdfDocument(pdf)
buffer = io.BytesIO()
document[0].render(scale=1).to_pil().save(buffer, 'WEBP')
sheet_image = base64.b64encode(buffer.getvalue()).decode()
fixture = {'pages': [sheet_image, sheet_image], 'pageCount': 2,
           'pdf': base64.b64encode(pdf).decode(), 'text': document[0].get_textpage().get_text_range()}
SEED = """async ({step,empty=false,extra={}})=>{
 const c=JSON.parse(document.getElementById('app-config').textContent);
 const profile=structuredClone(empty?c.empty:c.demo);profile.photos=[];
 const {openDraftStore}=await import('/static/js/storage.js');
 await (await openDraftStore()).put({profile,step,visited:[0,3],mobile:extra});
}"""

def screenshot(page, name, full=False):
    page.evaluate('window.scrollTo(0,0)')
    page.screenshot(path=str(OUT / name), full_page=full, animations='disabled')

def go(page, step):
    if page.url.endswith(f'#section-{step}'):
        return
    if page.locator('#m-navigator').is_hidden():
        page.locator('#m-back').click()
    page.locator('#m-navigator').click()
    page.locator(f'[data-m="nav-go"][data-target="{step}"]').click()
    expect(page.locator('#m-sheet')).not_to_be_visible()
    expect(page).to_have_url(URL + f'#section-{step}')

def new_page(browser, width=390, height=844, replay=True):
    context = browser.new_context(viewport={'width': width, 'height': height},
                                  is_mobile=True, has_touch=True, reduced_motion='reduce',
                                  accept_downloads=True)
    if replay:
        context.route('**/api/preview', lambda route: route.fulfill(json=fixture))
    page = context.new_page()
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(URL)
    expect(page.locator('.m-heading h1')).to_be_visible()
    return context, page

def seed(page, step=3, empty=False, extra=None):
    page.goto(URL + f'#section-{step}')
    page.evaluate(SEED, {'step': step, 'empty': empty, 'extra': extra or {}})
    page.reload()
    expect(page.locator('.m-heading h1')).to_be_visible()

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=chromium_executable(), headless=True,
                                chromium_sandbox=True)
    context, page = new_page(browser)
    seed(page, extra={'chosen': ['contact.0.email'], 'completed': 'malformed', 'skipped': 7})
    expect(page.locator('[data-field="contact.0.email"]')).to_be_visible()
    checks.append('Malformed optional progress metadata does not block a valid draft')

    # Browser Back/Forward must dismiss and reopen the secondary surface, not leave creation.
    page.locator('#m-navigator').click()
    page.go_back(); expect(page.locator('#m-sheet')).not_to_be_visible()
    page.go_forward(); expect(page.locator('#m-sheet')).to_be_visible()
    page.locator('[data-target="4"]').click()
    page.locator('[data-m="entry-edit"]').first.click()
    page.locator('[data-field="education.0.degree"]').fill('Edited qualification')
    page.go_back(); expect(page.locator('.m-record').first).to_contain_text('Edited qualification')
    page.go_forward(); expect(page.locator('[data-field="education.0.degree"]')).to_have_value('Edited qualification')
    # A deletion must return to the list, even if another record occupies the deleted index.
    page.locator('#m-primary-action').click()
    page.locator('[data-m="entry-add"][data-section="education"]').click()
    page.locator('[data-field="education.1.degree"]').fill('Second qualification')
    page.locator('#m-primary-action').click()
    page.locator('[data-m="entry-edit"][data-index="0"]').first.click()
    page.locator('[data-m="record-remove"]').click()
    page.locator('#confirm-cancel').click()
    expect(page.locator('[data-field="education.0.degree"]')).to_have_value('Edited qualification')
    page.locator('[data-m="record-remove"]').click()
    page.locator('#confirm-action').click()
    expect(page.locator('#info-dialog')).not_to_be_visible()
    expect(page.locator('[data-field]')).to_have_count(0)
    expect(page.locator('[data-m="entry-edit"][data-section="education"]')).to_contain_text('Second qualification')
    checks.append('Sheet/entry Back and Forward, edit retention and confirmed record deletion')

    go(page, 3)
    page.get_by_label('Age', exact=True).fill('17')
    page.locator('#m-primary-action').click()
    expect(page.get_by_label('Age', exact=True)).to_be_focused()
    expect(page.locator('[id="personal.0.age-error"]')).to_be_visible()
    page.get_by_label('Age', exact=True).fill('29')
    page.get_by_label('Full name', exact=True).fill('Immediate refresh test')
    page.reload()
    expect(page.get_by_label('Full name', exact=True)).to_have_value('Immediate refresh test')
    context.set_offline(True)
    page.get_by_label('Full name', exact=True).fill('Saved while offline')
    expect(page.locator('.m-save-state')).to_have_text('Saved offline')
    context.set_offline(False)
    page.reload()
    expect(page.get_by_label('Full name', exact=True)).to_have_value('Saved while offline')
    checks.append('Inline age validation, immediate reload and offline local save')

    # Keyboard: unit selection keeps focus; shortened visual viewport hides the action dock.
    page.locator('[data-unit="ft"]').focus(); page.keyboard.press('Enter')
    expect(page.locator('[data-unit="ft"]')).to_be_focused()
    page.get_by_label('Full name', exact=True).focus()
    page.evaluate("""()=>{window.originalHeight=visualViewport.height;
      Object.defineProperty(visualViewport,'height',{configurable:true,get:()=>window.originalHeight-260});
      visualViewport.dispatchEvent(new Event('resize'));}""")
    expect(page.locator('.m-primary-dock')).not_to_be_visible()
    page.get_by_label('Full name', exact=True).blur()
    page.evaluate("delete visualViewport.height;visualViewport.dispatchEvent(new Event('resize'))")
    expect(page.locator('.m-primary-dock')).to_be_visible()
    checks.append('Keyboard focus survives unit selection; simulated soft-keyboard viewport leaves fields usable')

    go(page, 8)
    portrait = Path('app/static/artwork/demo-portrait-female.jpg')
    page.locator('#photo-input').set_input_files(str(portrait))
    expect(page.locator('#crop-dialog')).to_be_visible()
    page.go_back(); expect(page.locator('#crop-dialog')).not_to_be_visible()
    expect(page.locator('.m-photo-main img')).to_have_count(0)
    page.locator('#add-photo').click()
    page.locator('#photo-input').set_input_files(str(portrait))
    page.locator('#apply-crop').click()
    expect(page.locator('#crop-dialog')).not_to_be_visible()
    original = page.locator('.m-photo-main img').get_attribute('src')
    page.locator('[data-replace-photo]').click()
    page.locator('#photo-input').set_input_files(str(portrait))
    page.locator('#crop-dialog .dialog-close').click()
    expect(page.locator('#crop-dialog')).not_to_be_visible()
    assert page.locator('.m-photo-main img').get_attribute('src') == original
    page.locator('[data-replace-photo]').click()
    page.locator('#photo-input').set_input_files({'name': 'invalid.jpg', 'mimeType': 'image/jpeg', 'buffer': b'invalid photo'})
    expect(page.locator('#form-error')).to_be_visible()
    assert page.locator('.m-photo-main img').get_attribute('src') == original
    checks.append('Crop browser Back, replacement cancellation and invalid image preserve the original')

    go(page, 9)
    page.locator('#m-preview-action').click()
    expect(page.locator('#preview-page-number')).to_have_text('Page 1 of 2')
    page.locator('#preview-next').click()
    expect(page.locator('#preview-page-number')).to_have_text('Page 2 of 2')
    page.locator('#preview-zoom').click()
    assert page.locator('#document-preview').bounding_box()['width'] > 700
    page.locator('#preview-zoom').click()
    assert page.locator('#document-preview').bounding_box()['width'] < 390
    page.locator('[data-m="preview-continue"]').click()
    expect(page.locator('#m-review-image')).to_be_visible()
    expect(page).to_have_url(URL + '#section-10')
    page.go_back(); expect(page).to_have_url(URL + '#section-9')
    checks.append('Full-screen preview page navigation, zoom, Continue and subsequent Back')

    # Informational and destructive actions use one surface with a clear escape route.
    page.locator('#m-options').click();page.locator('[data-m="privacy"]').click()
    expect(page.locator('#m-sheet')).to_contain_text('Nothing is published')
    page.go_back(); expect(page.locator('#m-sheet')).not_to_be_visible()
    page.locator('#m-options').click();page.locator('[data-m="delete"]').click()
    expect(page.locator('#info-dialog')).to_be_visible();page.go_back()
    expect(page.locator('#info-dialog')).not_to_be_visible()
    expect(page).to_have_url(URL + '#section-9')
    checks.append('Privacy and delete cancellation return to the same section')
    context.close()

    # Replay fixtures only in geometry checks. The original data store remains isolated.
    for width, height in [(320,568),(360,800),(375,667),(390,844),(412,915),(430,740)]:
        context, page = new_page(browser, width, height)
        seed(page)
        for step in STEPS:
            if step == 0:
                go(page, 0)
            elif step == 3 and page.url.endswith('#section-0'):
                page.locator('#m-primary-action').click()
            else:
                go(page, step)
            page.evaluate('window.scrollTo(0,0)')
            expect(page.locator('.m-heading h1')).to_be_visible()
            assert page.evaluate('document.documentElement.scrollWidth')<=width+1 and page.evaluate('innerWidth')<=width+1, (width, step, 'overflow')
            dock = page.locator('.m-primary-dock').bounding_box()
            assert abs(dock['y'] + dock['height'] - height) <= 1, (width, step, dock)
            # The first task control must be reachable in the initial viewport.
            task = page.locator('#step-content input:not([hidden]),#step-content textarea,#step-content button').filter(visible=True).first
            box = task.bounding_box()
            assert box['y'] < height - dock['height'], (width, step, 'task below fold')
            small=page.locator('#step-content button,#m-progress button,.m-app-header button,.m-primary-dock button').evaluate_all('els=>els.filter(e=>!e.disabled&&e.getClientRects().length).filter(e=>{const r=e.getBoundingClientRect();return r.width<43||r.height<43}).map(e=>({text:e.textContent,rect:e.getBoundingClientRect().toJSON()}))')
            assert not small,(width,step,small)
            screenshot(page, f'mobile-{width}-{step}.png')
            metrics.append({'width':width,'height':height,'step':step,'firstControlY':round(box['y'])})
        # The shorter/taller browser heights exercise fixed chrome without changing phone width.
        go(page,3)
        for h in [568,667,740,800,844,915]:
            page.set_viewport_size({'width':width,'height':h})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            assert page.locator('#m-primary-action').bounding_box()['height']>=48
        page.set_viewport_size({'width':width,'height':height})
        page.locator('#m-navigator').click()
        snapshot = page.locator('#m-sheet').aria_snapshot()
        assert 'dialog "Your biodata"' in snapshot and 'Personal details' in snapshot
        # Focus cannot escape a modal through keyboard Tab.
        for _ in range(15):
            page.keyboard.press('Tab')
            assert page.evaluate("document.activeElement.closest('#m-sheet')!==null")
        screenshot(page,f'mobile-{width}-navigator.png')
        context.close()
    checks.append('All nine stages at six phone sizes; all six widths × six heights; labelled sheets and trapped keyboard focus')

    # Desktop/tablet regression: same data, original JS vs current JS, deterministic PDF.
    before = (OUT/'editor-before.js').read_text()
    diffs=[]
    for width,height in [(768,1024),(1024,1366),(1440,900)]:
        captures={}
        for version in ['before','after']:
            c=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
            c.route('**/api/preview',lambda r:r.fulfill(json=fixture))
            if version=='before':
                c.route('**/static/js/editor.js',lambda r:r.fulfill(body=before,content_type='application/javascript'))
            page=c.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(URL)
            page.evaluate(SEED,{'step':3})
            for step in [3,5,9]:
                page.goto(URL+f'#section-{step}');page.evaluate(SEED,{'step':step});page.reload()
                expect(page.locator('#step-content h1')).to_be_visible()
                page.evaluate('document.fonts.ready')
                page.wait_for_timeout(300)
                assert page.locator('.m-app-header').is_hidden()
                path=OUT/f'{version}-{width}-{step}.png'
                page.screenshot(path=str(path),animations='disabled')
                captures[version,step]=path
            c.close()
        for step in [3,5,9]:
            a=Image.open(captures['before',step]).convert('RGB');b=Image.open(captures['after',step]).convert('RGB')
            difference=ImageChops.difference(a,b)
            changed=sum(max(px)>15 for px in difference.get_flattened_data())/(width*height)
            diffs.append({'width':width,'step':step,'changedPixelFraction':changed})
            assert changed<.002, (width,step,changed)
    checks.append('Original vs updated desktop/tablet screenshots remain visually identical within raster timing tolerance')
    assert not errors, errors
    (OUT/'regression-result.json').write_text(json.dumps({'checks':checks,'metrics':metrics,'desktopDiffs':diffs,'errors':errors},indent=2))
    browser.close()
print('\n'.join(checks))
