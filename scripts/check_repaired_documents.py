"""Measure geometry and lossless pagination, with full-collection stress fixtures."""
import sys,json,copy,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
from app import create_app
from app.models.profile import Profile
from app.models.catalog import demo_profile,empty_profile
from app.services.repaired_documents import REGISTRY
from app.services.rendering import build_document_html
from playwright.sync_api import sync_playwright
app=create_app({'TESTING':True,'RATELIMIT_ENABLED':False});results=[]
with app.app_context(),sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=app.config['CHROMIUM_EXECUTABLE'],chromium_sandbox=True)
 context=browser.new_context(java_script_enabled=False);context.route('**/*',lambda r:r.abort());page=context.new_page();page.emulate_media(media='print');page.set_viewport_size({'width':794,'height':1123})
 paginator=(ROOT/'app/static/js/repaired-paginator.js').read_text()
 for id,design in REGISTRY.items():
  for variant in ['no-photo','hindi','stress','single','photos']:
   raw=demo_profile(True);raw['template']=id
   if variant=='no-photo':raw['photos']=[]
   if variant=='photos':raw['photos']=raw['photos']*3
   if variant=='hindi':raw['language']='hi';raw['sections']['personal']['name']='आरव मेहता';raw['sections']['about']['introduction']='मुझे किताबें पढ़ना और यात्रा करना पसंद है। परिवार और मित्र मेरे लिए बहुत महत्वपूर्ण हैं।';raw['customSections']=[{'id':'custom-test','title':'मेरी कहानी','fields':[{'label':'सप्ताहांत','value':'परिवार के साथ समय और सुबह की सैर।'}]}]
   if variant=='stress':
    raw['sections']['personal']['name']='Aarav Mehta Sharma Venkataraman Subramanian'
    raw['sections']['education']=[{'degree':f'Qualification {i} - communication and interaction design','institution':'National Institute of Design and Technology, Ahmedabad, Gujarat'} for i in range(12)]
    raw['sections']['career'][0].update(company='A multidisciplinary international design and research organization',location='Bengaluru, Karnataka, India')
    raw['sections']['contact']['email']='longunbrokenaddress'*6+'@example.com'
    raw['sections']['about']['introduction']=('A paragraph about life, meaningful work, and family. '*25+'\n\n')*2
    raw['customSections']=[{'id':'custom-long','title':'Everyday life','fields':[{'label':'The people, places, small moments and everyday traditions that matter most to me and my family','value':('Reading, learning, making things and spending time outdoors. '*20+'\n\n')*2}]}]
   if variant=='single':raw=empty_profile();raw['template']=id;raw['sections']['contact']['email']='only@example.com'
   doc=Profile.parse(raw).document();page.set_content(build_document_html(doc),wait_until='load');page.evaluate('document.fonts.ready')
   expected=page.locator('.r-source .r-row').evaluate_all('(rows)=>Object.fromEntries(rows.map(r=>[r.dataset.rowId,r.querySelector(".r-value").textContent]))')
   try:
    measure=page.evaluate(paginator)
    actual=page.locator('.r-page .r-row').evaluate_all('(rows)=>{const out={};rows.forEach(r=>out[r.dataset.rowId]=(out[r.dataset.rowId]||"")+r.querySelector(".r-value").textContent);return out}')
    assert actual==expected,('lost or reordered value fragments',set(expected)-set(actual),[(k,len(expected[k]),len(actual.get(k,''))) for k in expected if expected[k]!=actual.get(k)])
    assert page.locator('.r-page').count()>=1
    collisions=page.locator('.r-page').evaluate_all('''pages=>pages.flatMap((p,i)=>{const boxes=[...p.querySelectorAll('.r-row')].map(r=>[r,r.getBoundingClientRect()]);return boxes.flatMap(([r,a],j)=>boxes.slice(j+1).filter(([s,b])=>Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1).map(()=>({page:i+1,kind:'row overlap'})))})''')
    assert not collisions,collisions
    if variant=='no-photo':assert page.locator('.r-portrait').count()==0
    if variant=='photos':assert page.locator('.r-gallery img').count()==2
    results.append({'id':id,'case':variant,'pages':measure['pages'],'status':'passed'})
   except Exception as error:
    results.append({'id':id,'case':variant,'status':'failed','reason':str(error)});print(id,variant,str(error)[:300],flush=True)
  print(design['number'],id,flush=True)
 browser.close()
(ROOT/'output/template-repair/validation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print('PASS',sum(x['status']=='passed' for x in results),'FAIL',sum(x['status']=='failed' for x in results),flush=True)
if any(x['status']=='failed' for x in results):sys.exit(1)
