"""Real desktop/mobile smoke journey. Run against a local Flask server."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tmp' / 'qa'
OUT.mkdir(parents=True, exist_ok=True)
URL = os.getenv('APP_URL', 'http://127.0.0.1:5050')

with sync_playwright() as p:
    chrome=os.getenv('CHROMIUM_EXECUTABLE')
    if not chrome and Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome').exists():
        chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    browser = p.chromium.launch(headless=True, executable_path=chrome, chromium_sandbox=True)
    context = browser.new_context(viewport={'width':1440,'height':1050},accept_downloads=True)
    page = context.new_page()
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(URL)
    page.locator('.hero-start').click()
    page.wait_for_selector('[data-for="myself"]')
    page.evaluate('document.fonts.ready')
    page.screenshot(path=str(OUT/'desktop-start.png'),full_page=True)
    page.locator('#next').click()
    page.locator('.design-card[data-template="warm"]').click()
    page.locator('#next').click()
    page.locator('#next').click()
    page.locator('[data-field="personal.0.name"]').fill('Ananya Rao')
    page.locator('[data-field="personal.0.age"]').fill('28')
    page.locator('[data-field="personal.0.city"]').fill('Bengaluru')
    page.wait_for_timeout(550)
    assert page.locator('#document-preview h1').inner_text()=='Ananya Rao'
    page.reload()
    page.wait_for_selector('[data-field="personal.0.name"]')
    assert page.locator('[data-field="personal.0.name"]').input_value()=='Ananya Rao'
    page.locator('#next').click()
    page.locator('[data-field="education.0.degree"]').fill('M.Des')
    page.locator('[data-add-entry="education"]').click()
    page.locator('[data-field="education.1.degree"]').fill('B.Arch')
    page.locator('[data-field="career.0.role"]').fill('Architect')
    page.locator('[data-disclosure="work-0"]>summary').click()
    
    page.locator('[data-field="career.0.income"]').fill('PRIVATE SALARY')
    page.locator('[data-field-visibility="career.0.income"]').click()
    page.locator('#next').click()
    page.locator('[data-field="family.0.father"]').fill('A warm family that values kindness and learning.')
    page.locator('#next').click()
    page.locator('#skip').click()
    page.locator('[data-field="about.0.introduction"]').fill('I love thoughtful design, quiet walks and music. I value kindness and an equal partnership.')
    page.locator('#next').click()
    # Upload through the actual local image/crop flow.
    from PIL import Image
    image=Image.new('RGB',(900,1200),'#a4937d');image.save(OUT/'test-photo.jpg')
    page.locator('#photo-input').set_input_files(OUT/'test-photo.jpg')
    page.wait_for_selector('#crop-dialog[open]')
    page.locator('#crop-zoom').fill('1.25')
    page.locator('#rotate-photo').click()
    page.locator('#apply-crop').click()
    assert page.locator('.photo-card img').count()==1
    page.locator('#next').click()
    page.locator('[data-disclosure="custom"]>summary').click()
    page.locator('#add-custom').click()
    page.locator('[data-custom-title]').fill('Languages spoken')
    page.locator('[data-custom$=":label"]').fill('Languages')
    page.locator('[data-custom$=":value"]').fill('English, Hindi, Kannada')
    page.locator('.design-card[data-template="professional"]').click()
    assert page.locator('#document-preview h1').inner_text()=='Ananya Rao'
    assert 'PRIVATE SALARY' not in page.locator('#document-preview').inner_text()
    page.screenshot(path=str(OUT/'desktop-design.png'),full_page=True)
    page.locator('#next').click()
    page.locator('#export-consent').check()
    transmitted=[]
    page.on('request',lambda request:transmitted.append(request.post_data) if '/api/export/' in request.url else None)
    with page.expect_download(timeout=65000) as download:
        page.locator('[data-export="pdf"]').click()
    file=download.value
    file.save_as(OUT/'journey.pdf')
    assert (OUT/'journey.pdf').read_bytes().startswith(b'%PDF')
    assert transmitted and 'PRIVATE SALARY' not in transmitted[0]
    page.screenshot(path=str(OUT/'desktop-export.png'),full_page=True)
    # Offline edits and local backup persist without a network service.
    context.set_offline(True)
    page.locator('[data-step="3"]').first.click()
    page.locator('[data-field="personal.0.city"]').fill('Pune')
    page.wait_for_timeout(600)
    assert 'Offline' in page.locator('#save-status').inner_text()
    context.set_offline(False)
    page.reload();page.wait_for_selector('[data-field="personal.0.city"]')
    assert page.locator('[data-field="personal.0.city"]').input_value()=='Pune'
    # Hindi UI/document and mobile view.
    page.locator('#language').select_option('hi')
    assert page.locator('html').get_attribute('lang')=='hi'
    page.locator('[data-field="personal.0.name"]').fill('अनन्या राव')
    page.wait_for_timeout(500)
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path=str(OUT/'mobile-editor.png'),full_page=True)
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    page.locator('#mobile-preview').click()
    page.screenshot(path=str(OUT/'mobile-preview.png'),full_page=True)
    assert page.locator('#document-preview h1').inner_text()=='अनन्या राव'
    page.locator('#expand-preview').click()
    page.locator('#language').select_option('en')
    # Keyboard-safe backup and restoration.
    page.locator('#more-button').click()
    with page.expect_download() as backup:
        page.locator('#backup-button').click()
    backup.value.save_as(OUT/'backup.json')
    assert json.loads((OUT/'backup.json').read_text())['sections']['personal']['city']=='Pune'
    page.locator('#import-file').set_input_files(OUT/'backup.json')
    page.locator('#confirm-action').click()
    assert page.locator('[data-field="personal.0.name"]').input_value()=='अनन्या राव'
    assert not errors,errors
    browser.close()
    print(json.dumps({'browser_errors':errors,'result':'Desktop/mobile complete journey passed','artifacts':str(OUT)}))
