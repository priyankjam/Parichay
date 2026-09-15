import json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from browser_support import chromium_executable
url=json.loads(Path('tmp/reset-link.json').read_text())['url']
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 ctx=b.new_context();old=ctx.new_page();old.goto('http://127.0.0.1:5050/create')
 old.get_by_role('button',name='Start with my details').click();old.get_by_label('Full name',exact=True).fill('Reset verification profile')
 old.wait_for_timeout(600)
 reset=ctx.new_page();reset.goto(url);reset.wait_for_url('**/?fresh=*')
 # A stale editor's connection has been closed and must not restore the old draft.
 old.get_by_label('Full name',exact=True).fill('Stale data should not return');old.wait_for_timeout(600)
 reset.goto('http://127.0.0.1:5050/create');reset.get_by_role('button',name='Start with my details').click()
 expect(reset.get_by_label('Full name',exact=True)).to_have_value('')
 b.close()
print('Reset clears the saved draft and blocks stale editor writes')
