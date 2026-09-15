"""Stress names, unbroken text, section continuity, optional headers, and art safe zones."""
import sys,json,copy,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.check_collection import fixtures,create_app,Profile,COLLECTION,build_document_html,sync_playwright,pdfium
out=Path('output/template-collection/edge-checks');out.mkdir(exist_ok=True)
a=create_app({'TESTING':True,'RATELIMIT_ENABLED':False});report=[];symbol_previews=[]
with a.app_context(),sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=a.config['CHROMIUM_EXECUTABLE'],headless=True,chromium_sandbox=True);c=b.new_context(java_script_enabled=False);c.route('**/*',lambda r:r.abort());p=c.new_page();p.emulate_media(media='print');paginator=Path('app/static/js/collection-paginator.js').read_text()
 for d in COLLECTION:
  cases=[]
  stress=fixtures()['short'];stress['sections']['personal']['name']='A very long family name with a second given name and an extended surname '*2;stress['customSections']=[{'id':'custom-edge','title':'An extended personal statement','fields':[{'label':'A long uninterrupted field','value':'W'*2900+' END_OF_FIELD'}]}];cases.append(('long-name-unbroken',stress))
  whole=fixtures()['short'];whole['sections']['personal'].update(city='Bengaluru, Karnataka, India. '*6,nativePlace='Ahmedabad, Gujarat, India. '*7,motherTongue='English, Hindi and Gujarati. '*6,nationality='Indian citizen, living in Bengaluru. '*5);whole['sections']['education']=[{'degree':f'EDUCATION_{i:02d}','institution':'National Institute of Design'} for i in range(8)];cases.append(('section-continuity',whole))
  for option in d['supported_sacred_art']:
   raw=fixtures()['short'];raw['presentation']={'sacred_art':option,'direction':'auto','salutation':d['id']=='craft-ambedkarite-blue'};cases.append(('header-'+option,raw))
  for name,raw in cases:
   raw=copy.deepcopy(raw);raw['template']=d['id'];doc=Profile.parse(raw).document();p.set_content(build_document_html(doc),wait_until='load');p.evaluate('document.fonts.ready');geo=p.evaluate(paginator)
   art_overlap=p.evaluate('''()=>[...document.querySelectorAll('.craft-page')].flatMap(page=>{const body=page.querySelector('.craft-body').getBoundingClientRect();return [...page.querySelectorAll('.craft-art')].filter(art=>{const r=art.getBoundingClientRect();return r.left<body.right-.5&&r.right>body.left+.5&&r.top<body.bottom-.5&&r.bottom>body.top+.5}).map(x=>x.className)})''');assert not art_overlap,(d['id'],name,art_overlap)
   if name=='header-none':assert p.locator('.sacred-art').count()==0
   elif name.startswith('header-'):assert p.locator('.sacred-art').count()==1
   pdf=p.pdf(format='A4',print_background=True,prefer_css_page_size=True,tagged=True,margin={k:'0' for k in ['top','right','bottom','left']})
   with pdfium.PdfDocument(pdf) as source:
    texts=[page.get_textpage().get_text_range() for page in source];text=''.join(texts)
    if name=='long-name-unbroken':assert 'END_OF_FIELD' in text
    if name=='section-continuity':
     starts=[i for i,t in enumerate(texts) if 'EDUCATION_00' in t];ends=[i for i,t in enumerate(texts) if 'EDUCATION_07' in t];assert starts==ends,(d['id'],starts,ends)
    if name.startswith('header-'):
     source[0].render(scale=1.1).to_pil().save(out/f'{d["slug"]}-{name}.png')
    if name=='long-name-unbroken' and d['number'] in [1,4,14,17]:source[0].render(scale=.8).to_pil().save(out/f'{d["slug"]}-long-name.png')
   report.append({'template':d['id'],'case':name,'pages':geo['pages'],'art_overlap':art_overlap,'passed':True})
  print(d['name'],'edges passed',flush=True)
 b.close()
(out/'report.json').write_text(json.dumps(report,indent=2));print('PASS',len(report),'edge cases')
