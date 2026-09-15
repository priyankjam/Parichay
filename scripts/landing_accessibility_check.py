import ast
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from browser_support import chromium_executable
source=Path('scripts/paper_plum_check.py').read_text();node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='contrast')
exec(ast.get_source_segment(source,node))
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 page=b.new_page(viewport={'width':1440,'height':1000})
 for lang in ('en','hi'):
  page.goto('http://127.0.0.1:5050/?lang='+lang,wait_until='networkidle')
  failures=contrast(page);assert not failures,failures
  page.locator('[data-design=ivory]').focus();page.keyboard.press('Enter');expect(page.locator('[data-design=ivory]')).to_have_attribute('aria-pressed','true')
  page.locator('[data-privacy=phone]').focus();page.keyboard.press('Space');expect(page.locator('[data-private-row=phone]')).to_be_visible()
  page.locator('[data-script=hi]').focus();page.keyboard.press('Enter');expect(page.locator('#language-name')).to_have_text('आरव मेहता')
  assert page.locator('input').evaluate_all('(els)=>els.every(e=>e.labels.length>0)')
  assert page.locator('button').evaluate_all('(els)=>els.every(e=>e.textContent.trim()||e.getAttribute("aria-label"))')
 b.close()
print('Text contrast, input labels, button names and keyboard-operated demos passed in English and Hindi.')
