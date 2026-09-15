"""Gender-aware sample data, matching galleries, family fields and five-choice hobbies."""
import base64,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from browser_support import chromium_executable
out=Path('tmp/qa/editor-refinements');out.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[1]
female='data:image/jpeg;base64,'+base64.b64encode((root/'app/static/artwork/demo-portrait-female.jpg').read_bytes()).decode()
male='data:image/jpeg;base64,'+base64.b64encode((root/'app/static/artwork/demo-portrait.jpg').read_bytes()).decode()
read_draft="""async()=>{const {openDraftStore}=await import('/static/js/storage.js');return (await (await openDraftStore()).get()).profile;}"""
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 page=b.new_page(viewport={'width':1440,'height':900});errors=[];calls=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:calls.append(r.post_data_json) if r.url.endswith('/api/preview') else None)
 page.goto('http://127.0.0.1:5050/create')
 assert page.locator('[data-for]').count()==0
 expect(page.locator('[data-gender]')).to_have_count(2)
 expect(page.locator('[data-language]')).to_have_count(2)
 expect(page.locator('#steps .step-link')).to_have_count(10)
 page.locator('[data-gender="female"]').click()
 page.locator('[data-language="hi"]').click()
 expect(page.locator('[data-gender="female"]')).to_have_attribute('aria-pressed','true')
 page.reload()
 expect(page.locator('[data-language="hi"]')).to_have_attribute('aria-pressed','true')
 expect(page.locator('[data-gender="female"]')).to_have_attribute('aria-pressed','true')
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(out/'combined-mobile.png'))
 page.locator('[data-language="en"]').click();page.set_viewport_size({'width':1440,'height':900})
 page.locator('#next').click();page.locator('#next').click()
 expect(page.get_by_label('Full name',exact=True)).to_be_visible()
 expect(page.locator('#step-count')).to_contain_text('03 / 10')
 page.locator('#back').click();expect(page.locator('.design-card')).to_have_count(19)
 page.locator('#back').click();page.screenshot(path=str(out/'gender.png'))
 page.locator('#next').click()
 expect(page.locator('.design-card')).to_have_count(19);expect(page.locator('.design-filter')).to_have_count(5)
 expect(page.locator('#preview-text')).to_contain_text('Ananya Mehta',timeout=65000)
 assert all(r['profile']['photos']==[female] for r in calls)
 assert page.evaluate(read_draft)['photos']==[],'Sample preview must not become a user upload'
 expect(page.locator('[data-thumbnail="editorial"]')).to_have_attribute('data-state','ready',timeout=65000)
 assert page.locator('.design-card').first.evaluate('(e)=>getComputedStyle(e).paddingLeft')=='0px'
 page.screenshot(path=str(out/'style-desktop.png'))
 step_two=page.locator('[data-template]').evaluate_all('(els)=>els.map(e=>e.dataset.template)')
 page.locator('[data-step="9"]').click()
 assert page.locator('[data-template]').evaluate_all('(els)=>els.map(e=>e.dataset.template)')==step_two
 page.locator('[data-step="0"]').click();page.locator('#use-demo').click();page.locator('#confirm-action').click()
 expect(page.get_by_label('Full name',exact=True)).to_have_value('Ananya Mehta')
 page.locator('[data-step="5"]').click()
 for label in ('Father','Mother','Siblings'):
  assert page.get_by_label(label,exact=True).evaluate('(e)=>e.tagName')=='INPUT'
 page.get_by_label('Father',exact=True).fill('Vijay Mehta, architect')
 expect(page.locator('#preview-text')).to_contain_text('Vijay Mehta, architect',timeout=65000)
 page.screenshot(path=str(out/'family-desktop.png'))
 page.locator('[data-step="6"]').click()
 assert page.locator('[data-disclosure="culture"],[data-disclosure="astrology"]').count()==0
 expect(page.get_by_label('Religion',exact=False).first).to_be_visible()
 expect(page.get_by_label('Date of birth',exact=False).first).to_be_visible()
 page.screenshot(path=str(out/'culture-desktop.png'))
 page.locator('[data-step="7"]').click()
 while page.locator('[data-hobby][aria-pressed=true]').count():page.locator('[data-hobby][aria-pressed=true]').first.click()
 for hobby in ('reading','travel','music','cooking','fitness'):page.locator(f'[data-hobby="{hobby}"]').click()
 expect(page.locator('#hobby-count')).to_have_text('5 / 5')
 expect(page.locator('[data-hobby="yoga"]')).to_be_disabled()
 page.locator('[data-hobby="fitness"]').click();page.locator('#custom-hobby').fill('Pottery');page.locator('#custom-hobby').press('Enter')
 expect(page.locator('#hobby-count')).to_have_text('5 / 5')
 expect(page.locator('[data-hobby="Pottery"]')).to_have_attribute('aria-pressed','true')
 expect(page.locator('#preview-text')).to_contain_text('Pottery',timeout=65000)
 assert page.locator('.app-header').bounding_box()['y']==0, 'Header moved while selecting hobbies'
 page.screenshot(path=str(out/'hobbies-desktop.png'))
 page.reload();expect(page.locator('#hobby-count')).to_have_text('5 / 5')
 page.locator('#language').select_option('hi');expect(page.locator('[data-hobby="reading"]')).to_contain_text('पढ़ना')
 expect(page.locator('#preview-text')).to_contain_text('पढ़ना',timeout=65000)
 for width,height in [(360,800),(390,844),(768,1024)]:
  page.set_viewport_size({'width':width,'height':height});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.locator('.hobby-options').scroll_into_view_if_needed()
  page.screenshot(path=str(out/f'hobbies-{width}.png'))
 page.locator('#language').select_option('en');page.locator('#section-jump').select_option('8')
 page.locator('#photo-input').set_input_files(str(root/'app/static/artwork/demo-portrait-female.jpg'))
 expect(page.locator('#crop-dialog')).to_be_visible();page.locator('#apply-crop').click()
 page.wait_for_timeout(600);before=page.evaluate(read_draft)['photos'];assert len(before)==2
 page.locator('#section-jump').select_option('0');page.locator('[data-gender="male"]').click()
 page.wait_for_timeout(800);after=page.evaluate(read_draft)['photos']
 assert after[0]==male and after[1]==before[1], 'Only known demo portraits should change'
 page.locator('[data-gender="female"]').click();page.wait_for_timeout(800)
 assert page.evaluate(read_draft)['photos']==[female,before[1]]
 page.set_viewport_size({'width':390,'height':844})
 page.locator('#section-jump').select_option('1');expect(page.locator('.design-card')).to_have_count(19)
 expect(page.locator('[data-thumbnail=editorial]')).to_have_attribute('data-state','ready',timeout=65000)
 expect(page.locator('[data-thumbnail=professional]')).to_have_attribute('data-state','ready',timeout=65000)
 page.screenshot(path=str(out/'style-mobile.png'))
 page.goto('http://127.0.0.1:5050/create#section-2')
 expect(page.locator('[data-gender="female"]')).to_have_attribute('aria-pressed','true')
 expect(page.locator('[data-language="en"]')).to_have_attribute('aria-pressed','true')
 assert page.url.endswith('#section-0')
 assert not errors,errors
 (out/'result.json').write_text(json.dumps({'genderSample':True,'uploadedPhotoPreserved':True,'galleryTemplates':19,'familyInputs':3,'cultureExpanded':True,'hobbyLimit':5,'HindiAndPersistence':True,'errors':errors},indent=2))
 b.close()
print('Gender, gallery, family, expanded culture, hobbies and photo preservation passed')
