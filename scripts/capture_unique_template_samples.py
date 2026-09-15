"""Full A4 screenshots and PDFs of every selectable design, using fictional data."""
import base64,copy,html,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.models.catalog import TEMPLATES,demo_profile
from app.models.collection import COLLECTION
from app.models.profile import Profile
from app.services.rendering import build_document_html
from playwright.sync_api import sync_playwright
import pypdfium2 as pdfium
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/unique-template-samples'
OUT.mkdir(parents=True,exist_ok=True)
app=create_app({'TESTING':True,'RATELIMIT_ENABLED':False})
ordered=[*COLLECTION,*(d for d in TEMPLATES if not d['id'].startswith('craft-'))]

def sample(gender):
 p=demo_profile(True);p['gender']=gender
 person=p['sections']['personal'];person.update(maritalStatus='Never married',nationality='Indian')
 p['sections']['education'][0]['specialization']='Human-centred design';p['sections']['education'][1]['specialization']='Visual communication'
 p['sections']['career'][0].update(income='INR 22 lakh per year',description='Designing accessible digital products with a small, multidisciplinary team.')
 p['sections']['astrology']={'birthDate':'1997-06-16','birthTime':'09:20','birthPlace':'Ahmedabad, Gujarat'}
 p['sections']['contact'].update(relationship='Self')
 p['customSections']=[{'id':'custom-everyday','title':'Everyday life','fields':[{'label':'A good weekend','value':'A morning walk, cooking with family, and time with a good book.'}]}]
 if gender=='female':
  person.update(name='Ananya Mehta',age='28',height='165 cm')
  p['sections']['astrology'].update(birthDate='1998-04-12',birthTime='10:15')
  p['sections']['contact'].update(name='Ananya Mehta',email='ananya@example.com')
  p['photos']=['data:image/jpeg;base64,'+base64.b64encode((ROOT/'app/static/artwork/demo-portrait-female.jpg').read_bytes()).decode()]
 return p

manifest=[];overview=[]
with app.app_context(),sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=app.config['CHROMIUM_EXECUTABLE'],headless=True,chromium_sandbox=True)
 context=browser.new_context(java_script_enabled=False);context.route('**/*',lambda route:route.abort());page=context.new_page();page.emulate_media(media='print')
 craft_paginator=(ROOT/'app/static/js/collection-paginator.js').read_text()
 # Match the existing worker exactly for the original document families.
 from app.services.render_worker import PAGINATION_SCRIPT
 for number,design in enumerate(ordered,1):
  folder=OUT/f'{number:02d}-{design["id"]}';folder.mkdir(exist_ok=True)
  item={'number':number,'id':design['id'],'name':design['name'],'samples':{}}
  for gender in ['male','female']:
   raw=sample(gender);raw['template']=design['id'];doc=Profile.parse(raw).document();page.set_content(build_document_html(doc),wait_until='load');page.evaluate('document.fonts.ready');page.evaluate(craft_paginator if design['id'].startswith('craft-') else PAGINATION_SCRIPT)
   if design['id'].startswith('craft-'):assert page.locator('.craft-document').get_attribute('dir')=='ltr'
   pdf=page.pdf(format='A4',print_background=True,prefer_css_page_size=True,tagged=True,margin={k:'0' for k in ['top','right','bottom','left']});pdf_file=folder/f'{gender}-sample.pdf';pdf_file.write_bytes(pdf);files=[]
   with pdfium.PdfDocument(pdf) as source:
    text=''.join(p.get_textpage().get_text_range() for p in source)
    assert raw['sections']['personal']['name'] in text and raw['sections']['contact']['email'] in text
    normalized=''.join(text.casefold().split())
    assert 'everydaylife' in normalized and 'human-centreddesign' in normalized
    for index,rendered in enumerate(source):
     image=rendered.render(scale=1200/rendered.get_width()).to_pil().convert('RGB');target=folder/f'{gender}-page-{index+1:02d}.png';image.save(target,optimize=True);files.append(str(target.relative_to(OUT)))
     if index==0:
      thumb=image.copy();thumb.thumbnail((300,425));thumb.save(folder/f'{gender}-thumbnail.webp','WEBP',quality=88)
      if gender=='male':overview.append((design['name'],thumb.copy()))
   item['samples'][gender]={'pages':files,'pdf':str(pdf_file.relative_to(OUT)),'thumbnail':str((folder/f'{gender}-thumbnail.webp').relative_to(OUT))}
  manifest.append(item);print(number,design['name'],len(item['samples']['male']['pages']),len(item['samples']['female']['pages']),flush=True)
 browser.close()
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
# An at-a-glance contact sheet; the page PNGs remain the full-resolution review source.
width,height=230,355;cols=7;sheet=Image.new('RGB',(cols*width,((len(overview)+cols-1)//cols)*height),'#eee8dc');draw=ImageDraw.Draw(sheet)
for i,(name,im) in enumerate(overview):
 im.thumbnail((width-18,height-40));x=(i%cols)*width+(width-im.width)//2;y=(i//cols)*height+32;sheet.paste(im,(x,y));draw.text(((i%cols)*width+8,(i//cols)*height+8),f'{i+1:02d} '+name[:30],fill='#422936')
sheet.save(OUT/'all-designs.jpg',quality=90)
(OUT/'README.md').write_text('''# All unique Parichay template samples\n\n49 separately selectable designs. Each folder contains male and female fictional English samples, full A4 PNG pages (1200 pixels wide), a selectable-text PDF, and a small browsing thumbnail. Every page is included; long profiles are not squeezed onto one page.\n\nOpen index.html to browse. These are document screenshots from the exact application export renderer, with no editor controls. Optional sensitive fields are not filled merely to occupy space. No real phone number or personal draft appears in this folder.\n''')
cards=[]
for item in manifest:
 gender_blocks=[]
 for gender,data in item['samples'].items():
  links=''.join(f'<a href="{f}" target="_blank" rel="noopener">Page {i+1} PNG ↗</a>' for i,f in enumerate(data['pages']))
  gender_blocks.append(f'<div data-person="{gender}" {"hidden" if gender=="female" else ""}><a href="{data["pages"][0]}" target="_blank" rel="noopener"><img src="{data["thumbnail"]}" width="300" height="425" loading="lazy" alt="{html.escape(item["name"])} — {gender} sample"></a><div class="links">{links}<a href="{data["pdf"]}" target="_blank" rel="noopener">Complete PDF ↗</a></div></div>')
 cards.append(f'<article><h2><small>{item["number"]:02d}</small> {html.escape(item["name"])}</h2>{"".join(gender_blocks)}</article>')
(OUT/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Parichay — All template screenshots</title><style>*{box-sizing:border-box}body{margin:0;background:#f6f0e5;color:#292124;font:15px/1.6 system-ui,sans-serif}header,main{max-width:1440px;margin:auto;padding:35px 28px}h1{font:42px/1.1 Georgia,serif;color:#632b45;margin:12px 0}header p{max-width:750px;color:#625951}nav{position:sticky;top:0;background:#f6f0e5f5;border-bottom:1px solid #d8ccbf;padding:12px 28px;z-index:2;display:flex;gap:10px}button{padding:12px 20px;border:1px solid #c9b6ba;border-radius:28px;background:transparent;color:#632b45;font:inherit;cursor:pointer}button[aria-pressed=true]{background:#632b45;color:#fff}main{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:35px 24px}h2{font-size:15px;margin:0 0 13px;min-height:48px}small{color:#93787a}img{display:block;width:100%;height:auto;box-shadow:0 8px 22px #42292513}.links{display:flex;flex-wrap:wrap;gap:10px 16px;margin-top:16px}a{font-size:12px;color:#632b45;text-underline-offset:4px}a:focus-visible,button:focus-visible{outline:3px solid #632b45;outline-offset:4px}[hidden]{display:none!important}@media(max-width:1000px){main{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(max-width:750px){main{grid-template-columns:repeat(2,minmax(0,1fr));padding:24px 18px;gap:28px 18px}}@media(max-width:450px){main{grid-template-columns:1fr}h2{min-height:0}.links a{font-size:14px}}</style><header><span>PARICHAY · DOCUMENT REVIEW</span><h1>Every design. Every page.</h1><p>49 unique designs with complete fictional information, captured directly from the application's A4 export. Choose a sample person, then open any page at full resolution.</p><a href="all-designs.jpg">View the full collection at a glance ↗</a></header><nav aria-label="Sample person"><button data-choice="male" aria-pressed="true">Male sample</button><button data-choice="female" aria-pressed="false">Female sample</button></nav><main>'''+''.join(cards)+'''</main><script>document.querySelectorAll('[data-choice]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-choice]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));document.querySelectorAll('[data-person]').forEach(x=>x.hidden=x.dataset.person!==b.dataset.choice)});</script></html>''')
print('DONE',len(manifest),'designs;',sum(len(s['pages']) for d in manifest for s in d['samples'].values()),'full-page screenshots',flush=True)
