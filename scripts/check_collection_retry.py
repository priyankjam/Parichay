"""Inject temporary capacity responses; successful recovery uses the real renderer."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright, expect
from scripts.browser_support import chromium_executable

out = Path('output/template-collection/browser')
checks = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=chromium_executable(), headless=True, chromium_sandbox=True)
    for mode in ['recover', 'bounded', 'stale']:
        context = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        page = context.new_page()
        state = {'requests': [], 'remaining': 2}
        def route(request):
            payload = request.request.post_data_json
            name = payload['profile']['sections']['personal'].get('name', '')
            state['requests'].append(name)
            busy = mode == 'bounded' or state['remaining'] > 0
            if busy:
                state['remaining'] -= 1
                request.fulfill(status=503, headers={'Retry-After': '0.1'}, content_type='application/json', body='{"error":"Temporarily busy"}')
            else:
                request.continue_()
        page.route('**/api/preview', route)
        page.goto('http://127.0.0.1:5050/create#section-3')
        field = page.locator('[data-field="personal.0.name"]')
        if mode == 'stale':
            with page.expect_response(lambda r: '/api/preview' in r.url and r.status == 503):
                field.fill('Earlier Fictional Draft')
            field.fill('Current Fictional Draft')
            expect(page.locator('#preview-text')).to_contain_text('Current Fictional Draft', timeout=65000)
            expect(page.locator('#preview-text')).not_to_contain_text('Earlier Fictional Draft')
        else:
            field.fill('Fictional Recovery Check')
            expect(page.locator('#document-preview')).to_have_attribute('data-state', 'error' if mode == 'bounded' else 'ready', timeout=65000)
            assert len(state['requests']) == (4 if mode == 'bounded' else 3), state
        checks.append({'case': mode, 'requests': len(state['requests']), 'passed': True})
        context.close()
    browser.close()
(out / 'busy-recovery.json').write_text(json.dumps(checks, indent=2))
print('PASS recovery, bounded retries, and stale draft protection')
