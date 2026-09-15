"""Failure recovery, real multipage output, backup, deletion and native-share boundary."""
import json
from pathlib import Path
import pypdfium2 as pdfium
from playwright.sync_api import sync_playwright, expect
from browser_support import chromium_executable

OUT=Path('tmp/qa/mobile-redesign')
URL='http://127.0.0.1:5050/create'
checks=[];errors=[];sent=[]

def capture(page,name):
    page.screenshot(path=str(OUT/name),animations='disabled')

def jump(page,step):
    if page.locator('#m-navigator').is_hidden():page.locator('#m-back').click()
    page.locator('#m-navigator').click()
    page.locator(f'[data-target="{step}"]').click()
    expect(page.locator('#m-sheet')).not_to_be_visible()

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
    context=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce',accept_downloads=True)
    context.add_init_script("""const originalPut=IDBObjectStore.prototype.put;
      IDBObjectStore.prototype.put=function(...args){if(window.failSave)throw new DOMException('Storage full','QuotaExceededError');return originalPut.apply(this,args)};
      window.shared=[];Object.defineProperty(navigator,'canShare',{value:()=>true});
      Object.defineProperty(navigator,'share',{value:async ({files})=>window.shared.push(files.map(f=>({name:f.name,size:f.size,type:f.type})))});""")
    page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:sent.append(r.post_data_json) if r.url.endswith('/api/preview') else None)
    page.goto(URL);page.locator('#m-primary-action').click()
    page.evaluate('window.failSave=true')
    page.get_by_label('Full name',exact=True).fill('Recovery Test')
    expect(page.locator('#m-save-status')).to_have_text('Couldn’t save')
    page.locator('#m-save-status').click();expect(page.locator('#m-sheet')).to_contain_text('Your current details are still here')
    capture(page,'recovery-save-error.png')
    page.evaluate('window.failSave=false')
    page.locator('[data-m="retry-save"]').click()
    expect(page.locator('.m-save-state')).to_have_text('Saved ✓')
    page.reload();expect(page.get_by_label('Full name',exact=True)).to_have_value('Recovery Test')
    checks.append('Failed local write preserves input; retry commits it and refresh restores it')

    # Sensitive optional data must be removed from the transmitted payload, not merely hidden in CSS.
    page.locator('[data-m="add-details"]').click()
    page.locator('[data-id="contact.0.phone"]').click()
    page.get_by_label('Phone / WhatsApp',exact=True).fill('PRIVATE DO NOT SEND')
    page.locator('[data-m="field-options"][data-id="contact.0.phone"]').click()
    page.locator('[data-m="omit-field"]').click()
    expect(page.locator('[data-field="contact.0.phone"]')).to_have_count(0)
    sent.clear()
    page.route('**/api/preview',lambda r:r.fulfill(status=503,json={'error':'busy'}))
    jump(page,9);page.locator('#m-preview-action').click()
    expect(page.locator('#document-preview')).to_have_attribute('data-state','error')
    capture(page,'recovery-preview-error.png')
    page.unroute('**/api/preview');page.locator('#preview-retry').click()
    expect(page.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
    assert all('PRIVATE DO NOT SEND' not in json.dumps(payload) for payload in sent)
    page.go_back();expect(page.locator('#preview-dialog')).not_to_be_visible()
    checks.append('Preview renderer failure has a working retry; omitted sensitive content is never transmitted')

    # Long text forces real pagination through the production renderer.
    jump(page,7)
    page.get_by_label('Your introduction',exact=True).fill(('I value family, thoughtful conversations and learning something new. ' * 72).strip())
    page.locator('[data-m="custom-add"]').click()
    page.locator('[data-custom-title]').fill('More about me')
    page.locator('[data-custom$=":0:label"]').fill('A shared life')
    page.locator('[data-custom$=":0:value"]').fill(('Weekends bring time for reading, friends and exploring local places. '*30).strip())
    page.locator('#m-primary-action').click()
    jump(page,9)
    expect(page.locator('#document-preview')).to_have_attribute('data-state','ready',timeout=65000)
    page.locator('#m-preview-action').click()
    expect(page.locator('#preview-next')).to_be_enabled()
    page.locator('#preview-next').click()
    expect(page.locator('#preview-page-number')).to_contain_text('Page 2')
    capture(page,'recovery-real-page-two.png')
    page.locator('[data-m="preview-continue"]').click()
    page.locator('#m-primary-action').click();page.locator('#m-export-consent').check()
    with page.expect_download(timeout=65000) as download:page.locator('[data-format="pdf"]').click()
    download.value.save_as(OUT/'multipage-mobile.pdf')
    expect(page.locator('.m-complete')).to_be_visible()
    with pdfium.PdfDocument(OUT/'multipage-mobile.pdf') as document:
        pages=len(document)
        assert pages>1
        text='\n'.join(document[i].get_textpage().get_text_range() for i in range(pages))
        assert 'Recovery Test' in text and 'A shared life' in text and 'PRIVATE DO NOT SEND' not in text
    page.locator('#share-file').click()
    page.wait_for_function('window.shared.length===1')
    assert page.evaluate('window.shared[0][0].name').endswith('.pdf')
    checks.append(f'Real {pages}-page PDF, page navigation and native-share file handoff (share API simulated; no file sent)')

    # Generation failure keeps Review actionable and supports the exact format retry.
    page.locator('[data-m="edit-again"]').click()
    page.locator('[data-target="10"]').click()
    page.route('**/api/export/jpg',lambda r:r.fulfill(status=503,json={'error':'Your biodata is safe. We could not create the file. Try again.'}))
    page.locator('#m-primary-action').click();page.locator('#m-export-consent').check()
    page.locator('[data-format="jpg"]').click()
    expect(page.locator('#form-error')).to_contain_text('Your biodata is safe')
    expect(page.locator('[data-export="jpg"]')).to_be_enabled()
    capture(page,'recovery-export-error.png')
    page.unroute('**/api/export/jpg')
    with page.expect_download(timeout=65000) as download:page.locator('[data-export="jpg"]').click()
    assert download.value.suggested_filename.endswith('.zip')
    expect(page.locator('.m-complete')).to_be_visible()
    checks.append('Image generation failure preserves Review; retry downloads the actual multipage JPG archive')

    page.locator('#m-options').click()
    with page.expect_download() as backup:page.locator('[data-m="backup"]').click()
    backup.value.save_as(OUT/'private-test-backup.json')
    raw=json.loads((OUT/'private-test-backup.json').read_text())
    assert raw['sections']['contact']['phone']=='PRIVATE DO NOT SEND'
    assert 'contact.0.phone' in raw['hiddenFields']
    page.locator('#m-options').click();page.locator('[data-m="delete"]').click()
    page.locator('#confirm-action').click()
    expect(page.locator('#info-dialog')).not_to_be_visible()
    expect(page).to_have_url(URL+'#section-0')
    page.locator('#m-primary-action').click()
    expect(page.get_by_label('Full name',exact=True)).to_have_value('')
    page.locator('#m-options').click();page.locator('[data-m="restore"]').click()
    page.locator('#import-file').set_input_files(str(OUT/'private-test-backup.json'))
    page.locator('#confirm-action').click()
    expect(page.locator('#info-dialog')).not_to_be_visible()
    expect(page.get_by_label('Full name',exact=True)).to_have_value('Recovery Test')
    expect(page.locator('[data-field="contact.0.phone"]')).to_have_count(0)
    checks.append('Backup, confirmed deletion and restore retain the original values and visibility choices')
    assert not errors,errors
    (OUT/'recovery-result.json').write_text(json.dumps({'checks':checks,'errors':errors,'pages':pages},indent=2))
    context.close();browser.close()
print('\n'.join(checks))
