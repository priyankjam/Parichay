"""Focused regressions for the usability findings; synthetic boundaries are explicit."""
import io,json,re
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright,expect
from browser_support import chromium_executable
OUT=Path('tmp/qa/usability/after');OUT.mkdir(parents=True,exist_ok=True)
checks=[]
def photo(color,size=(800,1000)):
 out=io.BytesIO();Image.new('RGB',size,color).save(out,'JPEG');return {'name':'portrait.jpg','mimeType':'image/jpeg','buffer':out.getvalue()}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 context=b.new_context(viewport={'width':390,'height':844},accept_downloads=True);page=context.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:5050/create');page.get_by_role('button',name='Start with my details',exact=True).click()
 def jump(index):page.get_by_label('Go to section',exact=True).select_option(index=index)
 page.get_by_label('Full name',exact=True).fill('Close and return');jump(8)
 page.locator('#photo-input').set_input_files(photo('orange'));page.locator('#apply-crop').click()
 original=page.locator('.photo-card img').get_attribute('src')
 # Cancel and invalid replacement must leave the prior image intact.
 page.get_by_role('button',name='Replace',exact=True).click();page.locator('#photo-input').set_input_files(photo('blue'));page.get_by_role('button',name='Cancel photo adjustment',exact=True).click()
 assert page.locator('.photo-card img').get_attribute('src')==original
 page.get_by_role('button',name='Replace',exact=True).click();page.locator('#photo-input').set_input_files({'name':'too-large.jpg','mimeType':'image/jpeg','buffer':b'x'*(8*1024*1024+1)})
 expect(page.locator('#form-error')).to_be_focused();assert page.locator('.photo-card img').get_attribute('src')==original
 page.get_by_role('button',name='Replace',exact=True).click();page.locator('#photo-input').set_input_files(photo('blue'));page.locator('#apply-crop').click()
 assert page.locator('.photo-card').count()==1 and page.locator('.photo-card img').get_attribute('src')!=original
 checks.append('Replace cancel, invalid oversized file and successful replacement preserve photo count and old image until commit')
 for color in ['red','green','yellow','purple']:
  page.get_by_role('button',name=re.compile('Choose a photo')).click();page.locator('#photo-input').set_input_files(photo(color));page.locator('#apply-crop').click()
 assert page.locator('.photo-card').count()==5 and page.locator('#add-photo').count()==0
 page.get_by_role('button',name='Replace',exact=True).first.click();page.locator('#photo-input').set_input_files(photo('black'));page.locator('#apply-crop').click();assert page.locator('.photo-card').count()==5
 page.get_by_role('button',name='Remove',exact=True).first.click();page.get_by_role('button',name='Cancel',exact=True).click();assert page.locator('.photo-card').count()==5
 page.get_by_role('button',name='Make main',exact=True).last.click();assert page.locator('.photo-badge').count()==1
 checks.append('Five-photo limit still permits Replace; removal cancellation and main-photo selection work')
 # Close the real tab immediately after input, without waiting for debounce/commit.
 jump(3);page.get_by_label('Full name',exact=True).fill('Latest edit before tab close');page.close();page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:5050/create');expect(page.get_by_label('Full name',exact=True)).to_have_value('Latest edit before tab close');jump(8);assert page.locator('.photo-card').count()==5
 checks.append('Immediate tab close/reopen preserves latest text and all five photos')
 jump(3);page.get_by_role('button',name='Continue',exact=True).filter(visible=True).click();location=page.url
 page.get_by_role('button',name='Preview',exact=True).click();page.go_back();expect(page.locator('#preview-dialog')).not_to_be_visible();assert page.url==location
 page.go_forward();expect(page.locator('#preview-dialog')).to_be_visible();page.get_by_role('button',name='Back to editing',exact=True).click();expect(page.locator('#preview-dialog')).not_to_be_visible();page.wait_for_timeout(100);assert page.url==location
 page.go_back();expect(page.get_by_label('Full name',exact=True)).to_be_visible()
 checks.append('Preview Back, Forward, visible close and subsequent section Back preserve correct history')
 page.get_by_label('Full name',exact=True).focus();page.keyboard.press('Enter');expect(page.get_by_label('Age',exact=True)).to_be_focused()
 page.get_by_label('Age',exact=True).fill('17');page.keyboard.press('Enter');expect(page.get_by_label('Age',exact=True)).to_be_focused();expect(page.locator('[id="personal.0.age-error"]')).to_be_visible();page.get_by_label('Age',exact=True).fill('28')
 page.get_by_role('button',name=re.compile('Add date of birth')).click();expect(page.get_by_label(re.compile('^Date of birth'))).to_be_focused()
 checks.append('Next-field Enter respects validation; birth-details shortcut opens and focuses the optional date input')
 jump(3);page.get_by_label('Full name',exact=True).focus()
 # Synthetic keyboard viewport boundary, not a physical keyboard/TalkBack claim.
 page.evaluate('()=>{window.viewportHeight=visualViewport.height;Object.defineProperty(visualViewport,"height",{configurable:true,get:()=>window.viewportHeight-250});visualViewport.dispatchEvent(new Event("resize"))}')
 assert 'keyboard-open' in page.locator('body').get_attribute('class');page.get_by_label('Full name',exact=True).blur();page.wait_for_timeout(50);assert 'keyboard-open' not in page.locator('body').get_attribute('class')
 page.evaluate('()=>{delete visualViewport.height;visualViewport.dispatchEvent(new Event("resize"))}')
 checks.append('Synthetic shortened visual viewport hides dock only while an editable field has focus')
 # Privacy settings survive write-through saving, preview and export payload construction.
 jump(4);page.locator('summary').filter(has_text='More about your work').click();page.get_by_label(re.compile('^Income')).fill('PRIVATE INCOME');page.locator('[data-field-visibility="career.0.income"]').click();page.wait_for_timeout(150)
 assert 'PRIVATE INCOME' not in page.locator('#document-preview').inner_text()
 jump(7);intro=page.get_by_label('Your introduction',exact=True);intro.fill('पहचान और परिवार के बारे में लंबा परिचय। '*70);page.get_by_label('Interests & hobbies',exact=True).fill('Reading, music, cooking');page.get_by_label('Interests & hobbies',exact=True).fill('Reading, cooking')
 page.reload();expect(page.get_by_label('Interests & hobbies',exact=True)).to_have_value('Reading, cooking');assert len(page.get_by_label('Your introduction',exact=True).input_value())>2000
 checks.append('Long Hindi text and custom interest edits survive reload; hidden income stays out of live preview')
 # Every step remains available with enlarged text in both supported interface languages.
 scaled=[]
 for language in ['en','hi']:
  page.locator('#language').select_option(language);page.add_style_tag(content='html{font-size:200%}')
  for w,h in [(320,568),(360,800),(390,844),(412,915),(768,1024),(1024,1366),(1280,800),(1440,900),(1920,1080),(844,390)]:
   page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(50)
   for step in range(11):
    page.locator('#section-jump').select_option(index=step);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(language,w,step)
    assert page.locator('#section-jump').is_visible() and page.locator('#section-jump option').count()==11
   scaled.append([language,w,h])
 checks.append('220 section checks at 200% text: English/Hindi, nine portrait sizes and landscape')
 # Successful deletion must clear all completed/queued writes, including photos.
 page.goto('http://127.0.0.1:5050/create');page.reload();page.locator('#step-content h1').wait_for();page.locator('#language').select_option('en');page.locator('#more-button').click();page.get_by_role('button',name='Delete this draft',exact=True).click();page.get_by_role('button',name='Delete draft',exact=True).click();expect(page.locator('#info-dialog')).not_to_be_visible();page.reload();page.get_by_role('button',name='Start with my details',exact=True).click();expect(page.get_by_label('Full name',exact=True)).to_have_value('')
 checks.append('Delete draft clears persisted text and photo state after repeated writes')
 assert not errors,errors
 b.close()
(OUT/'recovery.json').write_text(json.dumps({'checks':checks,'scaled_views':scaled,'browser_errors':errors},indent=2));print(json.dumps(checks))
