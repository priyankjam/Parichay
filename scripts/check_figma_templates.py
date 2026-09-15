"""Render every new template using the real private PDF pipeline; build safe demo thumbnails."""
import io,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.models.designs import FIGMA_DESIGNS
from app.models.catalog import demo_profile
from app.models.profile import Profile
from app.services.rendering import export_document
from pypdf import PdfReader
import pypdfium2 as pdfium
out=Path('tmp/qa/figma/exports');out.mkdir(parents=True,exist_ok=True)
thumbs=Path('app/static/artwork/thumbnails');thumbs.mkdir(exist_ok=True)
app=create_app({'TESTING':True,'RATELIMIT_ENABLED':False})
results=[]
with app.app_context():
 for design in FIGMA_DESIGNS:
  if len(sys.argv)>1 and design['id'] not in sys.argv[1:]:continue
  for long in [False,True]:
   data=demo_profile();data['template']=design['id']
   if long:
    data['language']='hi';data['sections']['personal']['name']='अनन्या राव'
    data['sections']['education']=[{'degree':f'Education {i}','institution':'विश्वविद्यालय और प्रौद्योगिकी संस्थान'} for i in range(8)]
    data['sections']['career']=[{'role':f'Career {i}','company':'स्वतंत्र संस्था'} for i in range(4)]
    data['sections']['about']['introduction']='मुझे पढ़ना और यात्रा करना पसंद है। '*100
    data['customSections']=[{'id':'custom-figma-test','title':'मेरा परिचय','fields':[{'label':'Languages','value':'Hindi, English'}]}]
    data['sections']['contact']['phone']='NEVER-SHARE';data['hiddenFields']=['contact.0.phone']
   doc=Profile.parse(data).document();pdf,_,_=export_document(doc,'pdf')
   reader=PdfReader(io.BytesIO(pdf));text=''.join(p.extract_text() for p in reader.pages)
   assert ('अनन्या' if long else 'Aarav Mehta') in text
   assert 'NEVER-SHARE' not in text
   if long:assert 'Education 7' in text and 'Career 3' in text and 'Hindi, English' in text
   name=design['id']+('-long' if long else '')
   (out/(name+'.pdf')).write_bytes(pdf)
   with pdfium.PdfDocument(pdf) as document:
    page=document[0];bitmap=page.render(scale=1.5);image=bitmap.to_pil()
    image.save(out/(name+'.png'))
    bitmap.close();page.close()
   record={'template':design['id'],'fixture':'Hindi long' if long else 'English sample','pages':len(reader.pages),'bytes':len(pdf)}
   results.append(record);print(json.dumps(record),flush=True)
(out/'results.json').write_text(json.dumps(results,indent=2))
