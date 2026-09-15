"""Five content fixtures × every design; preview pixels derive from the exported PDF."""
import base64,copy,io,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.models.catalog import TEMPLATES,demo_profile
from app.models.profile import Profile
from app.services.rendering import preview_document
import pypdfium2 as pdfium
from PIL import Image,ImageDraw
from browser_support import chromium_executable
OUT=Path('tmp/qa/studio/render');OUT.mkdir(parents=True,exist_ok=True)
a=demo_profile(include_photo=True);a['sections']['partner']={};a['sections']['about']={'introduction':'Kind, curious and grounded. I enjoy books and being outdoors.'};a['sections']['family']={'father':'Teacher','mother':'Architect','siblings':'One sister'}
b=copy.deepcopy(a);b['sections']['education']*=2;b['sections']['about']['interests']='Reading, hiking, cooking, music'
c=copy.deepcopy(b);c['sections']['education']=[{'degree':f'Qualification {i+1}','institution':'National Institute of Technology','specialization':'Engineering and design','year':'2018'} for i in range(5)];c['sections']['career']=[{'role':f'Role {i+1}','company':'A thoughtful design company','location':'Bengaluru','description':'Building products with care and curiosity. '*4} for i in range(4)];c['sections']['family']={k:('A family that values kindness, education and shared time. '*35) for k in ['father','mother','siblings']};c['sections']['about']={'introduction':'I value an equal partnership, honest communication and curiosity about the world. '*45,'interests':'Reading, hiking, cooking, music, history, photography and travel. '*10};c['photos']*=3
h=copy.deepcopy(b);h['language']='hi';h['sections']['personal']={'name':'अनन्या शर्मा','age':'28','height':'173 सेमी','city':'बेंगलुरु','nativePlace':'लखनऊ','motherTongue':'हिन्दी'};h['sections']['education']=[{'degree':'अभियांत्रिकी में स्नातक','institution':'राष्ट्रीय प्रौद्योगिकी संस्थान','specialization':'कंप्यूटर विज्ञान','year':'2019'}]*2;h['sections']['career']=[{'role':'सॉफ्टवेयर अभियंता','company':'प्रौद्योगिकी संस्थान','location':'बेंगलुरु'}];h['sections']['family']={'father':'विजय शर्मा, शिक्षक','mother':'सुनीता शर्मा, शिक्षिका','siblings':'एक छोटी बहन, जो उच्च शिक्षा प्राप्त कर रही है।'};h['sections']['about']={'introduction':'मुझे परिवार के साथ समय बिताना, अच्छी किताबें पढ़ना और नई जगहों को देखना पसंद है। जीवन में दयालुता और समानता महत्वपूर्ण हैं। '*20,'interests':'संगीत, यात्रा, फ़ोटोग्राफ़ी और खाना बनाना'}
e=copy.deepcopy(b);e['sections']['personal']['name']='Ananya Lakshmi Narayanan Subramanian Venkataraman Rajagopalan';e['sections']['education'][0]['institution']='International Institute of Advanced Interdisciplinary Engineering and Technology Research and Development Studies';e['sections']['career'][0]['company']='International Collaborative Technology and Product Development Research Corporation';e['sections']['personal']['city']='Thiruvananthapuram, Kerala, India'
fixtures={'A-short':a,'B-medium':b,'C-long':c,'D-hindi':h,'E-long-names':e}
app=create_app({'TESTING':True,'WTF_CSRF_ENABLED':False,'RATELIMIT_ENABLED':False,'CHROMIUM_EXECUTABLE':chromium_executable()})
rows=[];sheets={key:[] for key in fixtures};issues=[]
with app.app_context():
 for theme in TEMPLATES:
  for key,profile in fixtures.items():
   profile['template']=theme['id'];doc=Profile.parse(profile).document();result=preview_document(doc)
   pdf=base64.b64decode(result['pdf']);(OUT/f'{key}-{theme["id"]}.pdf').write_bytes(pdf)
   with pdfium.PdfDocument(pdf) as rendered:
    assert len(rendered)==result['pageCount']==len(result['pages'])
    alltext=''
    for i in range(len(rendered)):
     page=rendered[i];w,h=page.get_size();assert abs(w/h-210/297)<.001
     bitmap=page.render(scale=1200/w);image=bitmap.to_pil().convert('RGB');encoded=io.BytesIO();image.save(encoded,format='WEBP',quality=85,method=3)
     assert encoded.getvalue()==base64.b64decode(result['pages'][i]),(key,theme['id'],i,'preview differs from PDF')
     text=page.get_textpage();alltext+=text.get_text_range()
     for char in range(text.count_chars()):
      left,bottom,right,top=text.get_charbox(char)
      if right-left>.2 and top-bottom>.2 and (left<0 or bottom<0 or right>w+1 or top>h+1):issues.append([key,theme['id'],i,'glyph outside sheet'])
     text.close()
     if i==0:
      image.save(OUT/f'{key}-{theme["id"]}.png');small=image.copy();small.thumbnail((180,255));sheets[key].append((theme['id'],small.copy()))
     image.close();bitmap.close();page.close()
    if key!='D-hindi':assert 'Teacher' in alltext or key=='C-long'
   if key=='B-medium':
    thumb=preview_document(doc,True);assert thumb['pageCount']==result['pageCount'];assert 'pdf' not in thumb
    with pdfium.PdfDocument(pdf) as source:
     page=source[0];bitmap=page.render(scale=300/page.get_width());image=bitmap.to_pil().convert('RGB');encoded=io.BytesIO();image.save(encoded,format='WEBP',quality=85,method=3)
     assert encoded.getvalue()==base64.b64decode(thumb['pages'][0]),theme['id']
     image.close();bitmap.close();page.close()
   rows.append({'profile':key,'template':theme['id'],'pages':result['pageCount'],'pdfBytes':len(pdf)})
   (OUT/'results.json').write_text(json.dumps({'cases':rows,'issues':issues},indent=2))
  print(theme['id'],flush=True)
for key,items in sheets.items():
 sheet=Image.new('RGB',(5*210,4*295),'#eee9e3');draw=ImageDraw.Draw(sheet)
 for i,(name,im) in enumerate(items):
  x=(i%5)*210;y=(i//5)*295;sheet.paste(im,(x+15,y+22));draw.text((x+8,y+4),name,fill='#1f1a1d')
 sheet.save(OUT/f'{key}-contact.jpg')
assert not issues,issues
print(json.dumps({'verified':len(rows),'issues':issues}))
