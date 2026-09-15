import sys,copy,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.check_collection import fixtures,create_app,Profile,COLLECTION,build_document_html,sync_playwright,pdfium
from app.services.rendering import export_document
from PIL import Image
out=Path('output/template-collection');a=create_app({'TESTING':True,'RATELIMIT_ENABLED':False});reports=[]
with a.app_context(),sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=a.config['CHROMIUM_EXECUTABLE'],headless=True,chromium_sandbox=True);c=b.new_context(java_script_enabled=False);c.route('**/*',lambda r:r.abort());p=c.new_page();p.emulate_media(media='print');paginator=Path('app/static/js/collection-paginator.js').read_text()
 for d in COLLECTION:
  raw=fixtures()['rtl'];raw['template']=d['id'];p.set_content(build_document_html(Profile.parse(raw).document()),wait_until='load');p.evaluate('document.fonts.ready');geo=p.evaluate(paginator)
  if d['layout_id']=='arch':
   center=p.evaluate('''()=>{const a=document.querySelector('.arch-art').getBoundingClientRect(),h=document.querySelector('.craft-heading').getBoundingClientRect();return Math.abs(a.x+a.width/2-h.x-h.width/2)}''');assert center<1,center
  pdf=p.pdf(format='A4',print_background=True,prefer_css_page_size=True,tagged=True,margin={k:'0' for k in ['top','right','bottom','left']});(out/f'batch-{d["batch"]}'/f'{d["slug"]}-rtl.pdf').write_bytes(pdf)
  with pdfium.PdfDocument(pdf) as source:source[0].render(scale=.8).to_pil().save(out/(d['slug']+'-rtl-check.png'))
  report_path=out/f'batch-{d["batch"]}'/'report.json';r=json.loads(report_path.read_text())
  for row in r:
   if row['template']==d['id'] and row['case']=='rtl':row.update(bytes=len(pdf),pages=geo['pages'])
  report_path.write_text(json.dumps(r,indent=2));reports.append({'template':d['id'],'rtl':True})
 for case in ['short','medium','no-photo']:
  raw=fixtures()[case];raw['template']='craft-cathedral-cross';p.set_content(build_document_html(Profile.parse(raw).document()),wait_until='load');p.evaluate('document.fonts.ready');p.evaluate(paginator)
  assert p.evaluate('''()=>{const s=document.querySelector('.sacred-art').getBoundingClientRect(),n=document.querySelector('.craft-heading').getBoundingClientRect();return s.bottom<n.top}''')
  pdf=p.pdf(format='A4',print_background=True,prefer_css_page_size=True,tagged=True,margin={k:'0' for k in ['top','right','bottom','left']})
  with pdfium.PdfDocument(pdf) as source:source[0].render(scale=1.1).to_pil().save(out/'edge-checks'/f'cathedral-cross-{case}.png')
  reports.append({'case':case,'cross_clear_of_name':True})
 b.close()
 for kind in ['png','jpg']:
  raw=fixtures()['short'];raw['template']='craft-nikah-nocturne';raw['presentation']['direction']='rtl';payload,mime,ext=export_document(Profile.parse(raw).document(),kind);assert ext==kind;(out/f'nikah-example.{ext}').write_bytes(payload);reports.append({'export':kind,'bytes':len(payload),'passed':True})
(out/'final-render-checks.json').write_text(json.dumps(reports,indent=2));print('PASS',len(reports),'final renderer checks')
