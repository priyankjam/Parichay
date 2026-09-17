import sys,base64,csv,io,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
from app import create_app
from scripts.review_fixture import review_profile
from app.models.catalog import TEMPLATES,demo_profile
from app.models.collection import COLLECTION
from app.models.profile import Profile
from app.services.rendering import export_document
from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image,ImageDraw
OUT=ROOT/'output/template-repair/after';OUT.mkdir(parents=True,exist_ok=True)
QA=ROOT/'tmp/repair-qa';QA.mkdir(parents=True,exist_ok=True)
app=create_app({'TESTING':True,'RATELIMIT_ENABLED':False})
designs=[*COLLECTION,*(d for d in TEMPLATES if not d['id'].startswith('craft-'))]
parser=argparse.ArgumentParser();parser.add_argument('--only',default='');args=parser.parse_args()
only=set(filter(None,args.only.split(',')))
rows=[];thumbs=[]
with app.app_context():
 for i,d in enumerate(designs,1):
  if d.get('retired'):continue
  p=review_profile();p['template']=d['id'];p['language']='en'
  name=f'{i:02d} - {d["name"].replace("/","-")}.pdf'
  if only and d['id'] not in only and (OUT/name).exists():
   pdf=(OUT/name).read_bytes()
  else:
   pdf,_,_=export_document(Profile.parse(p).document(),'pdf');(OUT/name).write_bytes(pdf)
  reader=PdfReader(io.BytesIO(pdf));txt=''.join(x.extract_text() for x in reader.pages)
  assert 'Aarav' in txt and 'everydaylife' in ''.join(txt.lower().split()),(name,txt[-300:])
  assert all(abs(float(x.mediabox.width)-595.28)<2 and abs(float(x.mediabox.height)-841.89)<2 for x in reader.pages)
  with pdfium.PdfDocument(pdf) as doc:
   for j,page in enumerate(doc):
    im=page.render(scale=.8).to_pil().convert('RGB');im.save(QA/f'{i:02d}-{j+1}.png')
    thumb=im.copy();thumb.thumbnail((160,226));thumbs.append((f'{i:02d} / p{j+1}',thumb))
  import unicodedata
  normalize=lambda text:''.join(unicodedata.normalize('NFKC',text).split()).casefold()
  expected=Profile.parse(p).document()
  missing=[row['value'] for section in expected['sections'] for group in section['groups'] for row in group if normalize(row['value']) not in normalize(txt)]
  assert not missing,(d['id'],missing)
  rows.append([f'{i:02d}',d['name'],d['id'],len(reader.pages),name,''])
  print(i,d['name'],len(reader.pages),flush=True)
with (OUT/'Feedback.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Number','Template','Template ID','Pages','PDF file','Your feedback']);w.writerows(rows)
for start in range(0,len(thumbs),28):
 batch=thumbs[start:start+28];sheet=Image.new('RGB',(7*180,4*260),'#eee8df');draw=ImageDraw.Draw(sheet)
 for k,(label,im) in enumerate(batch):
  x=k%7*180;y=k//7*260;draw.text((x+10,y+6),label,fill='#402b32');sheet.paste(im,(x+10,y+25))
 sheet.save(QA/f'overview-{start//28+1}.jpg')
(OUT/'README.txt').write_text(f'{len(rows)} unique Parichay templates, exported using the current app PDF renderer.\nEnglish fictional sample: Aarav Mehta, with photo, personal details, education, work, family, birth details, interests, contact, partner preferences and a custom section.\nAll pages are included. The same profile is used for fair comparison.\nUse the PDF number and page number when giving feedback, or fill in Feedback.csv.\n')
from zipfile import ZipFile,ZIP_DEFLATED
with ZipFile(OUT.with_suffix('.zip'),'w',ZIP_DEFLATED) as z:
 for file in sorted(OUT.iterdir()):z.write(file,OUT.name+'/'+file.name)
print('COMPLETE',len(rows),'PDFs',sum(r[3] for r in rows),'pages',flush=True)
