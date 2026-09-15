"""Landing → editor, mobile jumps/popup and v1 family-draft migration."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

out=Path('tmp/qa/revision');out.mkdir(parents=True,exist_ok=True)
url=os.getenv('APP_URL','http://127.0.0.1:5050')
chrome=os.getenv('CHROMIUM_EXECUTABLE')
if not chrome and Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome').exists():
    chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=chrome,chromium_sandbox=True)
    context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
    page=context.new_page();errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(url);page.evaluate('document.fonts.ready')
    assert page.locator('#step-content').count()==0
    assert page.locator('.hero-start').count()==1
    page.screenshot(path=str(out/'landing-desktop.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path=str(out/'landing-mobile.png'),full_page=True)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.locator('.hero-start').click()
    page.wait_for_selector('#section-jump option[value="10"]',state='attached')
    for i in range(11):
        page.locator('#section-jump').select_option(str(i))
        assert page.locator('#step-count').inner_text().endswith('/ 11')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),i
    page.locator('#section-jump').select_option('5')
    assert page.locator('[data-field^="family."]').count()==3
    assert page.locator('[data-field$="relationship"]').count()==0
    page.locator('[data-field="family.0.father"]').fill('Ravi Rao · Architect')
    page.locator('[data-field="family.0.mother"]').fill('Meera Rao · Teacher')
    page.locator('[data-field="family.0.siblings"]').fill('One younger brother, a musician.')
    page.screenshot(path=str(out/'family-mobile.png'),full_page=True)
    page.locator('#section-jump').select_option('3')
    page.locator('[data-field="personal.0.name"]').fill('Ananya Rao')
    page.locator('#section-jump').select_option('5')
    assert page.locator('[data-field="family.0.father"]').input_value()=='Ravi Rao · Architect'
    page.wait_for_timeout(450)
    scroll=page.evaluate('scrollY')
    page.locator('#mobile-preview').click()
    assert page.locator('#preview-dialog').evaluate('el=>el.open')
    rect=page.locator('#preview-dialog').bounding_box()
    assert rect['x']>0 and rect['y']>0 and rect['width']<390 and rect['height']<844
    assert 'Ravi Rao' in page.locator('#document-preview').inner_text()
    assert 'Mother' in page.locator('#document-preview').inner_text()
    page.locator('#preview-template').select_option('warm')
    page.screenshot(path=str(out/'preview-popup-mobile.png'),full_page=True)
    page.locator('#preview-zoom').click()
    assert page.locator('#document-preview').bounding_box()['width']>=679
    page.locator('#preview-zoom').click()
    assert page.locator('#document-preview').bounding_box()['width']<390
    page.keyboard.press('Escape')
    assert not page.locator('#preview-dialog').evaluate('el=>el.open')
    assert abs(page.evaluate('scrollY')-scroll)<3
    assert page.locator('#section-jump').input_value()=='5'
    page.locator('#section-jump').select_option('10')
    page.locator('#export-consent').check()
    with page.expect_download(timeout=65000) as d:page.locator('[data-export="pdf"]').click()
    d.value.save_as(out/'family-full-bleed.pdf')
    # Seed a legacy draft while on the landing page (which has no autosave script).
    raw=page.evaluate("JSON.parse(document.getElementById('app-config').textContent).empty")
    raw['schemaVersion']=1
    raw['sections']['family']=[{'relationship':'Father','name':'Legacy Father','occupation':'Architect'},
                               {'relationship':'Mother','name':'PRIVATE LEGACY','occupation':'Teacher'},
                               {'relationship':'Guardian','name':'Aunt Leela'}]
    raw['hiddenFields']=['family.1.name']
    page.goto(url)
    page.evaluate('''raw => new Promise((resolve,reject)=>{
      const r=indexedDB.open('parichay-local',1);
      r.onsuccess=()=>{const db=r.result,tx=db.transaction('drafts','readwrite');tx.objectStore('drafts').put({profile:raw,step:5,visited:[0,5]},'current');tx.oncomplete=()=>{db.close();resolve()};tx.onerror=()=>reject(tx.error)};
    })''',raw)
    page.locator('.hero-start').click()
    page.wait_for_selector('[data-field="family.0.father"]')
    assert page.locator('[data-field="family.0.father"]').input_value()=='Legacy Father\nArchitect'
    page.locator('#mobile-preview').click()
    text=page.locator('#document-preview').inner_text()
    assert 'PRIVATE LEGACY' not in text and 'Aunt Leela' in text
    page.locator('#expand-preview').click()
    page.locator('#language').select_option('hi')
    assert page.get_by_label('पिता',exact=True).count()==1
    assert page.locator('#section-jump option[value="5"]').inner_text().endswith('परिवार')
    page.screenshot(path=str(out/'family-hindi-mobile.png'),full_page=True)
    assert not errors,errors
    browser.close()
    print(json.dumps({'result':'Landing, mobile navigation/modal, export and private v1 migration passed','browser_errors':errors}))
