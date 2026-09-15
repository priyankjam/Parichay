"""Capture the existing product and inventory product CSS before refactoring."""
import json
import re
from collections import Counter
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_support import chromium_executable

out = Path('tmp/qa/paper-plum/before')
out.mkdir(parents=True, exist_ok=True)
inventory = {}
for filename in ['app.css', 'workspace.css', 'landing.css']:
    css = (Path('app/static/css') / filename).read_text()
    selectors = re.findall(r'([^{}]+)\{([^{}]*)\}', css)
    counts = Counter(selector.strip() for selector, _ in selectors)
    inventory[filename] = {
        'bytes': len(css), 'rules': len(selectors),
        'selectors': [selector.strip() for selector, _ in selectors],
        'repeated_selectors': {key: count for key, count in counts.items() if count > 1},
        'colors': dict(Counter(re.findall(r'#[0-9a-fA-F]{3,8}\b', css))),
        'pixel_values': dict(Counter(re.findall(r'[\d.]+px', css))),
        'important_count': css.count('!important'),
    }
(out / 'style-inventory.json').write_text(json.dumps(inventory, indent=2))
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=chromium_executable(), headless=True, chromium_sandbox=True)
    page = browser.new_page(viewport={'width':1440, 'height':1000})
    page.goto('http://127.0.0.1:5050/')
    page.screenshot(path=str(out / 'landing.png'), full_page=True)
    page.locator('.hero-start').click()
    page.wait_for_selector('[data-for]')
    for step in range(11):
        page.evaluate('(step)=>{const e=document.querySelector("#section-jump");e.value=step;e.dispatchEvent(new Event("change"))}',str(step))
        page.screenshot(path=str(out / f'step-{step}.png'))
    page.locator('#expand-preview').click()
    page.screenshot(path=str(out / 'preview.png'))
    page.keyboard.press('Escape')
    page.locator('#more-button').click()
    page.screenshot(path=str(out / 'menu.png'))
    page.locator('#menu-privacy').click()
    page.screenshot(path=str(out / 'privacy.png'))
    page.keyboard.press('Escape')
    page.goto('http://127.0.0.1:5050/missing')
    page.screenshot(path=str(out / 'error.png'))
    browser.close()
print(json.dumps({file: {key: val for key,val in details.items() if key in ['bytes','rules','important_count']} for file,details in inventory.items()}))
