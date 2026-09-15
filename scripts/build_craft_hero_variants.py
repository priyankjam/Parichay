"""Public hero artwork: same fictional Aarav profile in two more real templates."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.models.catalog import demo_profile
from app.models.profile import Profile
from app.services.rendering import export_document
import pypdfium2 as pdfium
from flask import render_template as flask_render_template
from unittest.mock import patch

def compact_sample(name,**context):
 context['css'] += """@media print{
 .theme-traditional{font-size:9pt;line-height:1.5}
 .theme-traditional .doc-label{font-size:8pt}
 .theme-traditional .doc-header{padding-bottom:10px;margin-bottom:12px}
 .theme-traditional .doc-portrait{width:80px;height:102px;margin-top:12px}
 .theme-traditional h1{font-size:26pt}
 .theme-traditional .doc-rule{margin-top:10px}
 .theme-traditional .doc-section{margin-bottom:10px}
 .theme-traditional h2{margin-bottom:6px;padding:3px}
 }"""
 return flask_render_template(name,**context)
app=create_app({'TESTING':True,'RATELIMIT_ENABLED':False})
with app.app_context():
 for lang in ('en','hi'):
  for template in ('editorial','traditional'):
   d=demo_profile(include_photo=True);d.update(gender='male',language=lang,template=template)
   s=d['sections'];s['about']['introduction']='Thoughtful, close to family, and always curious. I enjoy discovering new places and making time for the people I love.'
   s['family']['siblings']='One younger sister, postgraduate student.'
   s['partner']['preferences']='A kind, supportive partner who values family, friendship and shared growth.'
   if lang=='hi':
    s['personal'].update(name='आरव मेहता',city='बेंगलुरु, भारत',nativePlace='अहमदाबाद',motherTongue='गुजराती')
    s['education']=[dict(degree='एम.डेस, इंटरेक्शन डिज़ाइन',institution='राष्ट्रीय डिज़ाइन संस्थान',year='2019')]
    s['career']=[dict(role='प्रोडक्ट डिज़ाइनर',company='स्वतंत्र डिज़ाइन स्टूडियो',location='बेंगलुरु')]
    s['family']=dict(father='राजेश मेहता · वास्तुकार',mother='नीता मेहता · शिक्षिका',siblings='एक छोटी बहन, स्नातकोत्तर की छात्रा।')
    s['about']=dict(introduction='परिवार के करीब, नए अनुभवों के लिए उत्सुक। नई जगहें देखना और अपनों के साथ समय बिताना पसंद है।',interests='किताबें · यात्रा · चित्रकला · संगीत')
    s['partner']['preferences']='एक सहृदय साथी जो परिवार, दोस्ती और साथ आगे बढ़ने को महत्व दे।'
   with patch('app.services.rendering.render_template',compact_sample):
    pdf,_,_=export_document(Profile.parse(d).document(),'pdf')
   with pdfium.PdfDocument(pdf) as doc:
    assert len(doc)==1,(lang,template,len(doc))
    page=doc[0];bitmap=page.render(scale=800/page.get_width());im=bitmap.to_pil().convert('RGB')
    file=Path(f'app/static/artwork/hero-craft-{template}-{lang}.webp');im.save(file,'WEBP',quality=86,method=6);print(file,flush=True)
    im.close();bitmap.close();page.close()
