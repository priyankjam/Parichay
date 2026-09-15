"""Browser checks for errors, accessible preview, import safety and narrow screens."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

chrome=os.getenv('CHROMIUM_EXECUTABLE')
if not chrome and Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome').exists():
    chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=chrome,headless=True,chromium_sandbox=True)
    page=browser.new_page(viewport={'width':320,'height':740})
    page.goto(os.getenv('APP_URL','http://127.0.0.1:5050/create'))
    page.wait_for_selector('[data-for="myself"]')
    for step in range(11):
        # Desktop step links are hidden on mobile; use the native next flow.
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'Overflow at step {step}'
        if step==3:
            page.locator('[data-field="personal.0.name"]').fill('<script>alert(123)</script>')
            page.locator('[data-field="personal.0.age"]').fill('17')
            page.locator('#mobile-next').click()
            assert page.locator('[data-field="personal.0.age"]').count()==1
            page.locator('[data-field="personal.0.age"]').fill('28')
        if step<10:page.locator('#mobile-next').click()
    page.locator('#export-consent').check()
    page.route('**/api/export/pdf',lambda route:route.fulfill(status=503,content_type='application/json',body='{"error":"Try again shortly."}'))
    page.locator('[data-export="pdf"]').click()
    page.wait_for_selector('#form-error:not([hidden])')
    assert page.locator('#form-error').inner_text()=='Try again shortly.'
    assert not page.locator('[data-export="pdf"]').is_disabled()
    page.locator('#mobile-preview').click()
    assert page.locator('#preview-dialog').evaluate('el=>el.open')
    assert page.locator('#document-preview h1').inner_text()=='<script>alert(123)</script>'
    assert page.locator('#document-preview script').count()==0
    page.keyboard.press('Escape')
    assert page.locator('#editor-main').evaluate('el=>el.inert')==False
    # Local delete then reload must not restore the deleted draft.
    page.locator('#more-button').click();page.locator('#clear-button').click();page.locator('#confirm-action').click()
    page.wait_for_selector('#info-dialog',state='hidden')
    page.wait_for_selector('[data-for="myself"]')
    page.reload();page.wait_for_selector('[data-for="myself"]')
    assert page.locator('#sample-badge').get_attribute('hidden') is None
    # Simulate storage denial in a new page; the editor must remain usable.
    context=browser.new_context(viewport={'width':390,'height':844})
    context.add_init_script("Object.defineProperty(window,'indexedDB',{get(){throw new Error('denied')}})")
    blocked=context.new_page();blocked.goto(os.getenv('APP_URL','http://127.0.0.1:5050/create'))
    blocked.wait_for_selector('[data-for="myself"]')
    assert 'Not saved' in blocked.locator('#save-status').inner_text()
    browser.close()
    print('Narrow screens, validation, network retry, XSS escaping, keyboard preview, deletion and denied storage passed.')
