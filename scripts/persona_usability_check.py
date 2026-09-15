"""Persona walkthroughs through visible labels/actions, in separate browser contexts.
Reactions are recorded in docs/usability-personas.md; this script records observed behavior.
"""
import io,json,re,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from browser_support import chromium_executable
MODE=sys.argv[1] if len(sys.argv)>1 else 'before'
OUT=Path('tmp/qa/usability')/MODE;OUT.mkdir(parents=True,exist_ok=True)
URL='http://127.0.0.1:5050'
RUNS=[('professional','en',390,844),('professional','en',1440,900),('parent','hi',360,800),('parent','hi',768,1024),('guided','hi',320,568),('guided','hi',412,915)]
records=json.loads((OUT/'journeys.json').read_text()) if MODE=='before' and (OUT/'journeys.json').exists() else []
with sync_playwright() as playwright:
 browser=playwright.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 for persona,lang,w,h in RUNS:
  if any(r['persona']==persona and r['viewport']==[w,h] for r in records):continue
  context=browser.new_context(viewport={'width':w,'height':h},accept_downloads=True)
  page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  events=[];started=time.monotonic();hi=lang=='hi';prefix=f'{persona}-{w}'
  def observe(task):
   print(prefix,task,flush=True)
   events.append({'task':task,'heading':page.locator('h1').first.inner_text(),'url':page.url,
    'visible_buttons':page.get_by_role('button').filter(visible=True).all_text_contents(),
    'visible_labels':page.locator('label:visible').all_text_contents(),
    'scroll_y':page.evaluate('scrollY'),'overflow':page.evaluate('document.documentElement.scrollWidth>innerWidth')})
  def snap(name):page.screenshot(path=str(OUT/f'{prefix}-{name}.png'),animations='disabled')
  def next_step():
   page.get_by_role('button',name='आगे बढ़ें' if hi else 'Continue',exact=True).filter(visible=True).click()
  def fill(en,hindi,value):page.get_by_label(hindi if hi else en,exact=True).fill(value)
  def section(en,hindi):page.locator('summary').filter(has_text=hindi if hi else en).first.click()
  page.goto(URL);observe('01-home')
  if hi:page.get_by_role('link',name='हिन्दी',exact=True).click()
  page.get_by_role('link',name='अपना बायोडाटा बनाएँ' if hi else 'Create your biodata',exact=True).first.click()
  page.get_by_role('button',name=re.compile('बेटी के लिए' if persona=='parent' else 'मेरे लिए' if hi else 'Myself')).click()
  observe('02-for-whom');next_step();observe('03-starting-style')
  if MODE=='before':
   page.get_by_role('button',name=re.compile('गणेश आइवरी' if persona=='parent' else 'मिनिमल एडिटोरियल' if hi else 'Modern Professional')).first.click()
   next_step();observe('04-language');next_step()
  else:
   starter='एलिगेंट ट्रेडिशनल' if persona=='parent' else 'मिनिमल एडिटोरियल' if hi else 'Modern Professional'
   page.get_by_role('button',name=re.compile(starter)).first.click();next_step();observe('04-language');next_step()
  name='अनन्या शर्मा' if persona=='parent' else 'अमित वर्मा' if hi else 'Ananya Rao'
  fill('Full name','पूरा नाम',name);fill('Age','उम्र','28' if persona!='guided' else '32')
  fill('Height','कद',"5'8\"");fill('Current city','वर्तमान शहर','जयपुर' if hi else 'Bengaluru')
  fill('Native place','मूल निवास','लखनऊ' if hi else 'Mysuru');fill('Mother tongue','मातृभाषा','हिन्दी' if hi else 'Kannada')
  observe('05-personal');snap('personal')
  if hi:
   section('Get in touch','संपर्क');page.get_by_label(re.compile('^फ़ोन / व्हाट्सऐप')).fill('9000000000')
  next_step()
  fill('Qualification','योग्यता','B.Tech');fill('Institution','संस्थान','विश्वविद्यालय' if hi else 'PES University')
  page.get_by_role('button',name=re.compile('एक और (शिक्षा|डिग्री) जोड़ें' if hi else 'Add another (education|degree)')).click()
  page.get_by_label('योग्यता' if hi else 'Qualification',exact=True).last.fill('M.Tech')
  # Remove the filled second qualification, first cancel to check the safeguard.
  page.get_by_role('button',name='हटाएँ' if hi else 'Remove',exact=True).filter(visible=True).first.click()
  page.get_by_role('button',name='रद्द करें' if hi else 'Cancel',exact=True).click()
  fill('Profession / role','पेशा / पद','Software engineer');fill('Company / business','कंपनी / व्यवसाय','Design company')
  fill('Work location','कार्यस्थल','Pune')
  observe('06-education-career');next_step()
  fill('Father','पिता','विजय शर्मा · शिक्षक' if hi else 'Ravi Rao · Teacher');fill('Mother','माता','सुनीता शर्मा · शिक्षिका' if hi else 'Meera Rao · Architect')
  fill('Siblings','भाई-बहन','एक भाई, इंजीनियर\nएक बहन, शिक्षिका' if hi else 'One younger brother')
  observe('07-family');next_step()
  if persona=='parent':
   section('Culture & traditions','संस्कृति और परंपराएँ')
   page.get_by_label(re.compile('^धर्म')).fill('हिन्दू');page.get_by_label(re.compile('^समुदाय')).fill('अपनी पसंद से जोड़ा गया')
   section('Birth & astrology','जन्म और ज्योतिष')
   page.get_by_label(re.compile('^जन्म तिथि')).fill('1998-05-12');page.get_by_label(re.compile('^जन्म समय')).fill('07:30')
   page.get_by_label(re.compile('^जन्म स्थान')).fill('लखनऊ');page.get_by_label(re.compile('^राशि')).fill('वृषभ');page.get_by_label(re.compile('^नक्षत्र')).fill('रोहिणी')
   observe('08-culture-birth');next_step()
  else:
   observe('08-skip-culture');page.get_by_role('button',name='अभी छोड़ें' if hi else 'Skip for now',exact=True).click()
  fill('Your introduction','आपका परिचय','मुझे परिवार के साथ समय बिताना, किताबें पढ़ना और नई जगहें देखना पसंद है।' if hi else 'I enjoy quiet weekends, reading and long walks. I value kindness, curiosity and an equal partnership.')
  fill('Interests & hobbies','रुचियाँ और शौक','संगीत, यात्रा, खाना बनाना' if hi else 'Reading, hiking, cooking')
  observe('09-about-interests');next_step()
  page.get_by_role('button',name=re.compile('फ़ोटो चुनें' if hi else 'Choose a photo')).click()
  # File selection via the browser input; no real camera or external photo is accessed.
  page.locator('input[type=file][accept="image/jpeg,image/png,image/webp"]').set_input_files('app/static/artwork/demo-portrait.jpg')
  page.get_by_role('dialog',name='फ़ोटो समायोजित करें' if hi else 'Make it your own').wait_for()
  observe('10-photo-crop');page.get_by_role('button',name='यह फ़ोटो चुनें' if hi else 'Use this photo',exact=True).click();next_step()
  observe('11-design');snap('design')
  if MODE=='after' and persona=='parent':page.get_by_role('button',name=re.compile('गणेश आइवरी')).first.click()
  # Preview, zoom, close, then find and edit work city using visible section navigation.
  page.get_by_role('button',name='प्रीव्यू' if hi else 'Preview',exact=True).click() if w<1100 else page.get_by_role('button',name=re.compile('Read preview|Open preview popup')).click()
  observe('12-preview');snap('preview')
  zoom=page.get_by_role('button',name=re.compile('^(100%|बड़ा देखें|Zoom in)$'))
  if zoom.count():zoom.click()
  page.get_by_role('button',name=re.compile('प्रीव्यू बंद करें|Close preview|Back to editing|वापस|बदलाव करने लौटें')).first.click()
  if w<1100:
   page.get_by_role('combobox').filter(visible=True).all() # inspect visible options, select by the label users see
   page.get_by_label('खंड चुनें' if hi else 'Go to section').select_option(label='✓ 05 · शिक्षा और करियर' if hi else '✓ 05 · Education & career')
  else:page.get_by_role('button',name=re.compile('Education & career')).click()
  fill('Work location','कार्यस्थल','Bengaluru');observe('13-edit-previous')
  if w<1100:page.get_by_label('खंड चुनें' if hi else 'Go to section').select_option(label='11 · डाउनलोड और साझा करें' if hi else ('11 · Export & share' if MODE=='before' else '11 · Download & share'))
  else:page.get_by_role('button',name=re.compile('Export & share|Download & share')).click()
  observe('14-download')
  page.get_by_role('checkbox',name=re.compile('मैंने शामिल जानकारी|I have reviewed')).check()
  with page.expect_download(timeout=65000) as dl:
   page.get_by_role('button',name=re.compile('PDF डाउनलोड करें' if hi else 'Download PDF')).filter(visible=True).last.click()
  dl.value.save_as(OUT/f'{prefix}.pdf')
  page.get_by_text('आपकी फ़ाइल तैयार है।' if hi else 'Your file is ready.',exact=True).wait_for()
  observe('15-share-ready');snap('share')
  # Inspect the platform hand-off without opening an OS sheet or sending a message.
  page.evaluate('()=>{window.shareCalls=[];navigator.share=async data=>window.shareCalls.push(data.files.map(f=>({name:f.name,type:f.type,size:f.size})))}')
  native=page.evaluate('()=>Boolean(navigator.canShare?.({files:[new File(["test"],"test.pdf",{type:"application/pdf"})]}))')
  share_button=page.get_by_role('button',name=re.compile('डाउनलोड की गई फ़ाइल साझा करें|Share downloaded file|WhatsApp|व्हाट्सऐप')).filter(visible=True).last
  if native:
   share_button.click();events.append({'task':'share-native-boundary','files':page.evaluate('window.shareCalls'),'delivery':'Not attempted; OS sharing is intercepted'})
  # Unsupported-browser path is tested separately and visibly.
  page.evaluate('()=>{navigator.canShare=()=>false}')
  if MODE=='before':
   with page.expect_download(timeout=5000) as shared:share_button.click()
   events.append({'task':'share-fallback','filename':shared.value.suggested_filename,'duplicate_download':True})
  else:
   share_button.click();events.append({'task':'share-fallback','copy':page.locator('#export-result').inner_text()})
  page.reload();observe('16-return');snap('return')
  # Returning users find their current section; go to the named personal section to confirm values.
  if w<1100:page.get_by_label('खंड चुनें' if hi else 'Go to section').select_option(index=3)
  else:page.get_by_role('button',name=re.compile('Personal & contact')).click()
  assert page.get_by_label('पूरा नाम' if hi else 'Full name',exact=True).input_value()==name
  assert not errors,errors
  records.append({'persona':persona,'language':lang,'viewport':[w,h],'elapsed_automation_seconds':round(time.monotonic()-started,1),'events':events,'browser_errors':errors})
  (OUT/'journeys.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));context.close()
 browser.close()
print(json.dumps({'completed':len(records),'mode':MODE}))
