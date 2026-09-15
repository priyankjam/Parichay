"""Capture the actual mobile UI in disposable browser contexts, without modifying it."""
import json
import io
import math
import argparse
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright, expect
from browser_support import chromium_executable

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/mobile-ux-review'
OUT.mkdir(parents=True, exist_ok=True)
manifest = []
errors = []
parser=argparse.ArgumentParser()
parser.add_argument('--language',choices=['en','hi','both'],default='both')
parser.add_argument('--append',action='store_true')
parser.add_argument('--share-only',action='store_true')
args=parser.parse_args()
if args.append:
    previous=json.loads((OUT/'manifest.json').read_text())
    manifest=previous['screens'];errors=previous['browserErrors']
STEPS = [(0, 'Gender and language'), (1, 'Style preference'), (3, 'Personal and contact'),
         (4, 'Education and career'), (5, 'Family'), (6, 'Culture and birth details'),
         (7, 'About you and interests'), (8, 'Photos'), (9, 'Design and preview'), (10, 'Download and share')]

def save_manifest():
    (OUT / 'manifest.json').write_text(json.dumps({'viewport': {'width':390,'height':844},
        'screens':manifest,'browserErrors':errors}, ensure_ascii=False, indent=2))

def settle(page):
    page.evaluate('document.fonts.ready')
    page.wait_for_timeout(350)

def capture(page, lang, slug, title, note='', full=True, top=True, group='Journey'):
    settle(page)
    if top:
        page.evaluate('window.scrollTo(0,0)')
    page.wait_for_timeout(150)
    folder = OUT / lang
    folder.mkdir(exist_ok=True)
    files = {}
    for variant in (['viewport','full'] if full else ['viewport']):
        filename = f'{lang}/{slug}-{variant}.png'
        page.screenshot(path=str(OUT / filename), full_page=variant=='full', animations='disabled')
        if variant=='full' and page.locator('.mobile-action-dock:visible').count():
            # Full-page capture otherwise burns the fixed dock into the middle of the
            # document. Recover that content from a real scrolled viewport, then put
            # the same dock once at the end. Viewport originals remain untouched.
            box = page.locator('.mobile-action-dock').bounding_box()
            base = Image.open(OUT / filename).convert('RGB')
            if base.height>844 and box:
                y0,y1 = math.floor(box['y']), min(844,math.ceil(box['y']+box['height']))
                original = Image.open(OUT / files['viewport']).convert('RGB')
                page.evaluate('scrollTo(0,540)')
                page.wait_for_timeout(100)
                offset = round(page.evaluate('scrollY'))
                scrolled = Image.open(io.BytesIO(page.screenshot(animations='disabled'))).convert('RGB')
                base.paste(scrolled.crop((0,y0-offset,390,y1-offset)),(0,y0))
                base.paste(original.crop((0,y0,390,y1)),(0,base.height-(y1-y0)))
                base.save(OUT / filename)
                page.evaluate('scrollTo(0,0)')
        files[variant] = filename
    manifest.append({'language':lang,'title':title,'group':group,'note':note,'files':files,
                     'pageHeight':page.evaluate('document.documentElement.scrollHeight'),
                     'horizontalOverflow':page.evaluate('document.documentElement.scrollWidth>innerWidth')})
    save_manifest()
    print(f'Captured {lang}: {title}', flush=True)

def jump(page, step):
    page.locator('#section-jump').select_option(str(step))
    settle(page)

def load_gallery(page):
    # Trigger the same lazy thumbnail loading that normal scrolling would trigger.
    for card in page.locator('.design-card').all():
        card.scroll_into_view_if_needed()
        thumb = card.locator('[data-thumbnail]')
        expect(thumb).to_have_attribute('data-state','ready',timeout=65000)
    page.evaluate('scrollTo(0,0)')

def dialog_capture(page, lang, slug, title, selector='#info-dialog'):
    dialog = page.locator(selector)
    expect(dialog).to_be_visible()
    dialog.evaluate('(e)=>e.scrollTop=0')
    capture(page,lang,slug,title,full=False,top=False,group='Dialogs and states')
    if dialog.evaluate('(e)=>e.scrollHeight>e.clientHeight+5'):
        dialog.evaluate('(e)=>e.scrollTop=e.scrollHeight')
        capture(page,lang,slug+'-bottom',title+' — lower content',full=False,top=False,group='Dialogs and states')

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
    languages=[] if args.share_only else (('en','hi') if args.language=='both' else (args.language,))
    for lang in languages:
        context = browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,
            is_mobile=True,has_touch=True,accept_downloads=True,locale='en-IN')
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto('http://127.0.0.1:5050/?lang='+lang,wait_until='networkidle')
        page.evaluate('''async()=>{await document.fonts.ready;for(let y=0;y<document.body.scrollHeight;y+=650){scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}scrollTo(0,0);}''')
        page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
        capture(page,lang,'00-landing','Landing page')
        page.goto('http://127.0.0.1:5050/create?lang='+lang)
        expect(page.locator('#use-demo')).to_be_visible()
        capture(page,lang,'01-gender-language','01 · Gender and language',note='New guest draft.')
        jump(page,1)
        load_gallery(page)
        capture(page,lang,'02-style','02 · Style preference',note='All 19 designs; fresh draft with fictional sample thumbnails.')
        if lang=='en':
            page.evaluate('scrollTo(0,900)')
            capture(page,lang,'02-style-scrolled','Style gallery — sticky filters while scrolling',full=False,top=False,group='Dialogs and states')
            jump(page,3)
            capture(page,lang,'03-personal-empty','Personal details — empty state',group='Dialogs and states')
            jump(page,8)
            capture(page,lang,'08-photos-empty','Photos — empty state',group='Dialogs and states')
        jump(page,0)
        page.locator('#use-demo').click()
        if lang=='en':dialog_capture(page,lang,'sample-confirm','Load sample confirmation')
        page.locator('#confirm-action').click()
        expect(page.locator('#info-dialog')).not_to_be_visible()
        expect(page.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
        for number,(step,title) in enumerate(STEPS[2:],3):
            jump(page,step)
            if step==9:load_gallery(page)
            capture(page,lang,f'{number:02d}-step-{step}',f'{number:02d} · {title}',note='Fictional sample biodata. Default disclosure states preserved.')

        jump(page,9)
        page.locator('#spotlight-toggle').click()
        expect(page.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
        capture(page,lang,'11-spotlight','Spotlight mode',group='Dialogs and states')
        page.locator('#spotlight-toggle').click()
        page.evaluate('scrollTo(0,0)')
        page.locator('#mobile-preview').click()
        dialog_capture(page,lang,'12-full-preview','Full preview popup',selector='#preview-dialog')
        page.keyboard.press('Escape')

        if lang=='en':
            jump(page,3)
            while page.locator('#step-content details:not([open])').count():
                page.locator('#step-content details:not([open])').first.locator('summary').first.click()
            capture(page,lang,'personal-expanded','Personal and contact — all optional groups expanded',group='Dialogs and states')
            jump(page,5)
            page.locator('[data-field-visibility="family.0.father"]').click()
            capture(page,lang,'field-removed','Family — one field removed from biodata',group='Dialogs and states')
            page.locator('[data-field-visibility="family.0.father"]').click()
            page.locator('[data-hide="family"]').check()
            capture(page,lang,'section-hidden','Family — entire section hidden',group='Dialogs and states')
            page.locator('[data-hide="family"]').uncheck()
            jump(page,7)
            while page.locator('#step-content details:not([open])').count():
                page.locator('#step-content details:not([open])').first.locator('summary').first.click()
            page.locator('#add-custom').click()
            page.locator('[data-custom-title]').last.fill('A little more about me')
            page.locator('[data-custom$=":0:label"]').last.fill('A weekend well spent')
            page.locator('[data-custom$=":0:value"]').last.fill('A morning walk, cooking with family, and discovering a new book.')
            capture(page,lang,'about-custom','About you — partner preferences and custom section expanded',group='Dialogs and states')
            jump(page,8)
            page.locator('[data-crop="0"]').click()
            dialog_capture(page,lang,'photo-crop','Photo crop and adjustment',selector='#crop-dialog')
            page.keyboard.press('Escape')
            page.evaluate('scrollTo(0,0)')
            page.locator('#more-button').click()
            capture(page,lang,'draft-menu','Draft options menu',full=False,group='Dialogs and states')
            page.locator('#menu-privacy').click()
            dialog_capture(page,lang,'privacy','Privacy information')
            page.keyboard.press('Escape')
            # Close the menu if the privacy action has left it open.
            page.keyboard.press('Escape')
            page.locator('#more-button').click()
            page.locator('#clear-button').click()
            dialog_capture(page,lang,'delete-confirm','Delete draft confirmation')
            page.locator('#confirm-cancel').click()
            jump(page,10)
            page.locator('[data-disclosure="image-formats"] summary').click()
            page.locator('#export-consent').check()
            capture(page,lang,'download-formats','Download — consent enabled and all file formats',group='Dialogs and states')
            with page.expect_download(timeout=65000):page.locator('[data-export="pdf"]').click()
            expect(page.locator('#export-result')).to_be_visible()
            capture(page,lang,'download-success','Download complete',group='Dialogs and states')
            page.evaluate("Object.defineProperty(navigator,'canShare',{value:undefined,configurable:true})")
            page.locator('#share-file').click()
            expect(page.locator('#share-help')).to_be_visible()
            capture(page,lang,'share-help','WhatsApp sharing instructions',note='Fallback shown on browsers without native file sharing.',group='Dialogs and states')
        context.close()
    if args.share_only:
        context=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True,accept_downloads=True)
        context.add_init_script("Object.defineProperty(navigator,'canShare',{value:undefined,configurable:true})")
        page=context.new_page()
        page.goto('http://127.0.0.1:5050/create?lang=en')
        page.locator('#use-demo').click();page.locator('#confirm-action').click()
        expect(page.locator('#info-dialog')).not_to_be_visible()
        jump(page,10);page.locator('#export-consent').check()
        with page.expect_download(timeout=65000):page.locator('[data-export="pdf"]').click()
        page.locator('#share-file').click();expect(page.locator('#share-help')).to_be_visible()
        capture(page,'en','share-help','WhatsApp sharing instructions',note='Fallback shown on browsers without native file sharing.',group='Dialogs and states')
        context.close()
    browser.close()
save_manifest()
print(f'Finished: {len(manifest)} screens/states; browser errors: {errors}',flush=True)
