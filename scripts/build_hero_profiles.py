"""Render complete fictional male/female hero samples; never use saved drafts."""
import base64,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.models.catalog import demo_profile
from app.models.profile import Profile
from app.services.rendering import export_document
from flask import render_template as flask_render_template
from unittest.mock import patch

# Compact stationery samples keep complete content clear of the supplied florals.
# This affects public hero artwork only, never user previews or exports.
def hero_template(name, **context):
 context["css"] += """
 @media print {
 .biodata.illustrated{font-size:9pt;line-height:1.4}
 .theme-figma-peach-floral{--design-print-padding:30mm 20mm 60mm 22mm}
 .theme-figma-blossom{--design-print-padding:35mm 18mm 60mm 18mm}
 .illustrated h1,.illustrated[lang=hi] h1{font-size:24pt}
 .illustrated h2{font-size:11pt;margin-bottom:6px}
 .illustrated .doc-label,.illustrated .doc-prose-label,.illustrated .doc-prose+.doc-prose .doc-prose-label{font-size:8.5pt}
 .illustrated .doc-section{margin-bottom:10px}
 .illustrated .doc-row{margin:3px 0;line-height:1.4}
 .illustrated .doc-header{margin-bottom:12px}
 .illustrated .doc-opening{grid-template-columns:minmax(0,1fr) 32mm;margin-bottom:12px}
 .illustrated .doc-portrait{width:32mm;height:42mm}
 .illustrated .doc-prose p{margin-bottom:5px}
 }"""
 return flask_render_template(name, **context)
import pypdfium2 as pdfium
app=create_app({'TESTING':True,'RATELIMIT_ENABLED':False})
out=Path('app/static/artwork')
with app.app_context():
 for lang in ('en','hi'):
  for gender,design in [('male','figma-peach-floral'),('female','figma-blossom')]:
   d=demo_profile(include_photo=True);d.update(gender=gender,language=lang,template=design)
   s=d['sections'];s['about']['introduction']='Thoughtful, close to family, and always curious. I enjoy discovering new places and making time for the people I love.'
   s['family']['siblings']='One younger sister, postgraduate student.'
   s['partner']['preferences']='A kind, supportive partner who values family, friendship and shared growth.'
   if gender=='female':
    s['personal'].update(name='Ananya Sharma',age='27',height='165 cm',city='Pune, India',nativePlace='Jaipur',motherTongue='Hindi')
    s['education']=[dict(degree='M.Arch, Sustainable Architecture',institution='CEPT University',year='2021')]
    s['career']= [dict(role='Architect',company='Independent architecture studio',location='Pune')]
    s['family'].update(father='Vikram Sharma · Professor',mother='Sunita Sharma · Entrepreneur',siblings='One elder brother, software engineer.')
    s['about']['interests']='Reading · Travel · Painting · Music'
    photo=out/'demo-portrait-female.jpg';d['photos']=['data:image/jpeg;base64,'+base64.b64encode(photo.read_bytes()).decode()]
   if lang=='hi':
    s['personal'].update(name='अनन्या शर्मा' if gender=='female' else 'आरव मेहता',city='पुणे, भारत' if gender=='female' else 'बेंगलुरु, भारत',nativePlace='जयपुर' if gender=='female' else 'अहमदाबाद',motherTongue='हिन्दी' if gender=='female' else 'गुजराती')
    s['education']=[dict(degree='एम.आर्क, सस्टेनेबल आर्किटेक्चर' if gender=='female' else 'एम.डेस, इंटरेक्शन डिज़ाइन',institution='सेप्ट विश्वविद्यालय' if gender=='female' else 'राष्ट्रीय डिज़ाइन संस्थान',year='2021' if gender=='female' else '2019')]
    s['career']=[dict(role='वास्तुकार' if gender=='female' else 'प्रोडक्ट डिज़ाइनर',company='स्वतंत्र डिज़ाइन स्टूडियो',location='पुणे' if gender=='female' else 'बेंगलुरु')]
    s['family']=dict(father='विक्रम शर्मा · प्रोफ़ेसर' if gender=='female' else 'राजेश मेहता · वास्तुकार',mother='सुनीता शर्मा · उद्यमी' if gender=='female' else 'नीता मेहता · शिक्षिका',siblings='एक बड़े भाई, सॉफ़्टवेयर इंजीनियर।' if gender=='female' else 'एक छोटी बहन, स्नातकोत्तर की छात्रा।')
    s['about']=dict(introduction='परिवार के करीब, नए अनुभवों के लिए उत्सुक। नई जगहें देखना और अपनों के साथ समय बिताना पसंद है।',interests='किताबें · यात्रा · चित्रकला · संगीत')
    s['partner']['preferences']='एक सहृदय साथी जो परिवार, दोस्ती और साथ आगे बढ़ने को महत्व दे।'
   with patch('app.services.rendering.render_template',hero_template):
    pdf,_,_=export_document(Profile.parse(d).document(),'pdf')
   with pdfium.PdfDocument(pdf) as doc:
    assert len(doc)==1,(lang,gender,len(doc))
    page=doc[0];bitmap=page.render(scale=800/page.get_width());im=bitmap.to_pil().convert('RGB')
    path=out/f'hero-filled-{gender}-{lang}.webp';im.save(path,'WEBP',quality=88,method=6);print(path,flush=True)
    im.close();bitmap.close();page.close()
