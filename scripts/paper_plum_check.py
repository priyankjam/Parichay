"""Visual/contrast evidence for the Paper & Plum product system (local Chrome)."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from browser_support import chromium_executable
OUT=Path('tmp/qa/paper-plum/after');OUT.mkdir(parents=True,exist_ok=True)
SIZES=[(320,568),(360,800),(375,812),(390,844),(430,932),(768,1024),(820,1180),(1024,1366),(1280,800),(1440,1000),(1600,1000),(1920,1080)]
URL='http://127.0.0.1:5050'

def jump(page,step):
 page.evaluate('(n)=>{const e=document.querySelector("#section-jump");e.value=n;e.dispatchEvent(new Event("change"))}',str(step))

def capture(page,name,full=False):
 page.evaluate('document.fonts.ready')
 page.screenshot(path=str(OUT/(name+'.png')),full_page=full,animations='disabled')

def contrast(page):
 return page.evaluate('''() => {
 const rgb=s=>(s.match(/[\\d.]+/g)||[]).map(Number);
 const luminance=c=>c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
 const failures=[];
 for(const el of document.querySelectorAll('body *')){
  if(el.closest('.biodata,.design-thumbnail,.hero-specimen,.template-strip,svg')||!el.getClientRects().length||el.matches(':disabled'))continue;
  const text=[...el.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join('').trim();if(!text)continue;
  const style=getComputedStyle(el);if(style.visibility==='hidden')continue;
  const color=rgb(style.color);let bg;
  for(let node=el;node;node=node.parentElement){const c=rgb(getComputedStyle(node).backgroundColor);if(c.length===3||c[3]===1){bg=c;break}}
  if(!bg)bg=[250,247,242];
  const ratio=(Math.max(luminance(color),luminance(bg))+.05)/(Math.min(luminance(color),luminance(bg))+.05);
  const size=parseFloat(style.fontSize),bold=parseFloat(style.fontWeight)>=700,required=size>=24||(size>=18.66&&bold)?3:4.5;
  if(ratio<required)failures.push({text:text.slice(0,70),color:style.color,background:bg,ratio,required});
 }
 return failures;
}''')

with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=chromium_executable(),headless=True,chromium_sandbox=True)
 page=browser.new_page(viewport={'width':1440,'height':1000},accept_downloads=True)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 checks=[];contrast_issues=[]
 for lang in ['en','hi']:
  page.goto(URL+'/?lang='+lang)
  for w,h in SIZES:
   page.set_viewport_size({'width':w,'height':h})
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),('landing',lang,w)
   checks.append(['landing',lang,w,h])
   if w in [320,390,768,1440]:capture(page,f'landing-{lang}-{w}',True)
  contrast_issues.extend(contrast(page))
 page.set_viewport_size({'width':1440,'height':1000});page.goto(URL+'/create')
 page.wait_for_selector('[data-for]');capture(page,'onboarding-desktop')
 page.locator('#use-demo').click();page.locator('#confirm-action').click()
 page.wait_for_selector('#info-dialog',state='hidden')
 for w,h in [(1440,1000),(390,844)]:
  page.set_viewport_size({'width':w,'height':h})
  for step in range(11):
   jump(page,step);capture(page,f'editor-{w}-{step}')
   contrast_issues.extend(contrast(page))
  page.locator('#mobile-preview' if w<1100 else '#expand-preview').click();capture(page,f'preview-{w}');contrast_issues.extend(contrast(page));page.keyboard.press('Escape')
  page.locator('#more-button').click();capture(page,f'menu-{w}');contrast_issues.extend(contrast(page))
  page.locator('#menu-privacy').click();capture(page,f'privacy-{w}');contrast_issues.extend(contrast(page));page.keyboard.press('Escape')
  jump(page,8);page.locator('[data-crop="0"]').click();page.wait_for_selector('#crop-dialog[open]');capture(page,f'crop-{w}');page.keyboard.press('Escape')
  page.locator('[data-remove-photo="0"]').click();capture(page,f'confirm-{w}');page.locator('#confirm-cancel').click()
 jump(page,3);page.locator('[data-field="personal.0.age"]').fill('17');page.locator('#mobile-next').click();capture(page,'inline-error');contrast_issues.extend(contrast(page))
 page.locator('[data-field="personal.0.age"]').fill('29');jump(page,10);page.locator('#export-consent').check()
 # Hold the real request briefly to inspect indeterminate loading; don't invent server stages.
 def delayed(route):
  page.wait_for_timeout(1200);route.continue_()
 page.route('**/api/export/pdf',delayed)
 with page.expect_download(timeout=65000) as download:
  page.locator('#mobile-next').click();capture(page,'export-loading')
 download.value.save_as(OUT/'biodata.pdf');page.unroute('**/api/export/pdf',delayed)
 page.wait_for_selector('#export-result:not([hidden])');capture(page,'export-success');contrast_issues.extend(contrast(page))
 page.route('**/api/export/pdf',lambda route:route.fulfill(status=503,content_type='application/json',body=json.dumps({'error':'We could not create the PDF. Your draft is safe. Try again.'})))
 page.locator('[data-export="pdf"]').click();expect(page.locator('#form-error')).to_be_visible();capture(page,'export-error');contrast_issues.extend(contrast(page));page.unroute('**/api/export/pdf')
 assert page.locator('#export-result').is_hidden()
 with page.expect_download(timeout=65000) as retry_download:page.locator('#form-error [data-export]').click()
 assert retry_download.value.suggested_filename.endswith('.pdf')
 # Exercise long-script content and RTL geometry without claiming translated product support.
 samples={'mr':'आपली माहिती आणि आपल्या कुटुंबाची ओळख','gu':'તમારી વ્યક્તિગત માહિતી અને પરિવારનો પરિચય','pa':'ਤੁਹਾਡੀ ਨਿੱਜੀ ਜਾਣਕਾਰੀ ਅਤੇ ਪਰਿਵਾਰ ਦੀ ਜਾਣ ਪਛਾਣ','bn':'আপনার ব্যক্তিগত তথ্য এবং পরিবারের পরিচয়','or':'ଆପଣଙ୍କ ବ୍ୟକ୍ତିଗତ ସୂଚନା ଓ ପରିବାର ପରିଚୟ','ta':'உங்கள் தனிப்பட்ட தகவல்கள் மற்றும் குடும்ப அறிமுகம்','te':'మీ వ్యక్తిగత వివరాలు మరియు కుటుంబ పరిచయం','kn':'ನಿಮ್ಮ ವೈಯಕ್ತಿಕ ಮಾಹಿತಿ ಮತ್ತು ಕುಟುಂಬ ಪರಿಚಯ','ml':'നിങ്ങളുടെ വ്യക്തിഗത വിവരങ്ങളും കുടുംബ പരിചയവും','ur':'آپ کی ذاتی معلومات اور خاندان کا تعارف'}
 jump(page,3)
 for lang,example in samples.items():
  page.evaluate('([lang,text])=>{document.documentElement.lang=lang;document.documentElement.dir=lang==="ur"?"rtl":"ltr";document.querySelector(".step-heading").textContent=text;document.querySelector(".step-description").textContent=text+" · "+text}',[lang,example])
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),lang
  capture(page,'script-'+lang)
 page.reload();page.wait_for_selector('[data-field="personal.0.name"]')
 page.context.set_offline(True);expect(page.locator('#save-status')).to_contain_text('Offline');capture(page,'offline');contrast_issues.extend(contrast(page));page.context.set_offline(False)
 # Simulate storage exhaustion in this disposable browser context, then recover.
 page.evaluate('()=>{window.originalDraftPut=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(){throw new DOMException("Storage full","QuotaExceededError")}}')
 page.locator('[data-field="personal.0.name"]').fill('Aarav Mehta');expect(page.locator('#storage-warning')).to_be_visible();capture(page,'storage-error');contrast_issues.extend(contrast(page))
 page.evaluate('()=>{IDBObjectStore.prototype.put=window.originalDraftPut}')
 page.locator('[data-field="personal.0.name"]').fill('Aarav Mehta ');expect(page.locator('#storage-warning')).to_be_hidden()
 page.set_viewport_size({'width':1440,'height':1000});page.locator('#more-button').focus();page.keyboard.press('Tab')
 assert page.evaluate('parseFloat(getComputedStyle(document.activeElement).outlineWidth)>=3')
 capture(page,'keyboard-focus')
 page.emulate_media(reduced_motion='reduce');page.locator('#expand-preview').click()
 assert page.locator('#preview-dialog').evaluate('(e)=>getComputedStyle(e).animationName')=='none'
 capture(page,'reduced-motion-preview');page.keyboard.press('Escape');expect(page.locator('#preview-dialog')).not_to_be_visible()
 page.goto(URL+'/missing');capture(page,'error-page');contrast_issues.extend(contrast(page))
 assert not errors,errors
 report={'landingChecks':checks,'contrastFailures':contrast_issues,'browserErrors':errors}
 (OUT/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 assert not contrast_issues,contrast_issues[:10]
 browser.close();print(json.dumps({'landingChecks':len(checks),'contrastFailures':len(contrast_issues),'browserErrors':errors}))
