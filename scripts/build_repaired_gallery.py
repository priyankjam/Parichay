"""Revisioned, same-scale PDF thumbnails for every ID and supported UI language."""
import sys,base64,io,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
from app import create_app
from scripts.review_fixture import review_profile
from app.models.profile import Profile
from app.services.repaired_documents import REGISTRY
from app.services.rendering import build_document_html
from playwright.sync_api import sync_playwright
import pypdfium2 as pdfium
out=ROOT/'app/static/artwork/repair-gallery-v2';out.mkdir(exist_ok=True)
app=create_app({'TESTING':True,'RATELIMIT_ENABLED':False})
parser=argparse.ArgumentParser();parser.add_argument('--only',help='Optional comma-separated template IDs');args=parser.parse_args()
with app.app_context(),sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=app.config['CHROMIUM_EXECUTABLE'],chromium_sandbox=True)
 c=b.new_context(java_script_enabled=False);c.route('**/*',lambda r:r.abort());page=c.new_page();page.emulate_media(media='print');paginator=(ROOT/'app/static/js/repaired-paginator.js').read_text()
 for id in REGISTRY:
  if REGISTRY[id].get('retired'):continue
  if args.only and id not in args.only.split(','):continue
  for gender in ['male','female']:
   for language in ['en','hi']:
    p=review_profile();p.update(template=id,gender=gender,language=language)
    if gender=='female':
     p['sections']['personal']['name']='अनन्या मेहता' if language=='hi' else 'Ananya Mehta';p['sections']['contact']['name']=p['sections']['personal']['name'];p['sections']['contact']['email']='ananya@example.com';p['photos']=['data:image/jpeg;base64,'+base64.b64encode((ROOT/'app/static/artwork/demo-portrait-female.jpg').read_bytes()).decode()]
    elif language=='hi':p['sections']['personal']['name']='आरव मेहता';p['sections']['contact']['name']='आरव मेहता'
    page.set_content(build_document_html(Profile.parse(p).document()),wait_until='load');page.evaluate('document.fonts.ready');page.evaluate(paginator)
    data=page.pdf(format='A4',print_background=True,prefer_css_page_size=True)
    with pdfium.PdfDocument(data) as doc:
     im=doc[0].render(scale=360/doc[0].get_width()).to_pil().convert('RGB');im.save(out/f'{gender}-{language}-{id}.webp','WEBP',quality=87,method=4)
     if gender=='male' and language=='en':im.save(ROOT/'app/static/artwork/thumbnails'/f'{id}.webp','WEBP',quality=87,method=4)
  print(id,flush=True)
 b.close()
