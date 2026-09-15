"""Complete fictional profile, real shared layout; bounded, prebuilt browsing images."""
import base64,copy,json,sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.models.catalog import demo_profile
from app.models.collection import COLLECTION
from app.models.profile import Profile
from app.services.rendering import build_document_html
from playwright.sync_api import sync_playwright
import pypdfium2 as pdfium
parser=argparse.ArgumentParser();parser.add_argument('--batch',type=int);parser.add_argument('--template');args=parser.parse_args()
app=create_app({'TESTING':True,'RATELIMIT_ENABLED':False});out=Path('app/static/artwork/collection-gallery-v1');out.mkdir(exist_ok=True)
with app.app_context(),sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=app.config['CHROMIUM_EXECUTABLE'],chromium_sandbox=True)
 context=browser.new_context(java_script_enabled=False);context.route('**/*',lambda r:r.abort());page=context.new_page();page.emulate_media(media='print');paginator=Path('app/static/js/collection-paginator.js').read_text()
 for d in [d for d in COLLECTION if (not args.batch or d['batch']==args.batch) and (not args.template or d['id']==args.template)]:
  for gender in ['male','female']:
   for language in ['en','hi']:
    raw=demo_profile(True);raw.update(template=d['id'],gender=gender,language=language)
    if gender=='female':
     raw['sections']['personal']['name']='अनन्या मेहता' if language=='hi' else 'Ananya Mehta';raw['sections']['contact']['name']=raw['sections']['personal']['name'];raw['sections']['contact']['email']='ananya@example.com';raw['photos']=['data:image/jpeg;base64,'+base64.b64encode(Path('app/static/artwork/demo-portrait-female.jpg').read_bytes()).decode()]
    elif language=='hi':raw['sections']['personal']['name']='आरव मेहता';raw['sections']['contact']['name']='आरव मेहता'
    page.set_content(build_document_html(Profile.parse(raw).document()),wait_until='load');page.evaluate('document.fonts.ready');page.evaluate(paginator);pdf=page.pdf(format='A4',print_background=True,prefer_css_page_size=True,tagged=True,margin={k:'0' for k in ['top','right','bottom','left']})
    with pdfium.PdfDocument(pdf) as doc:
     image=doc[0].render(scale=360/doc[0].get_width()).to_pil().convert('RGB');target=out/f'{gender}-{language}-{d["id"]}.webp';image.save(target,'WEBP',quality=86,method=4)
     if gender=='male' and language=='en':image.save(Path('app/static/artwork/thumbnails')/f'{d["id"]}.webp','WEBP',quality=86,method=4)
    print(target.name,flush=True)
 browser.close()
