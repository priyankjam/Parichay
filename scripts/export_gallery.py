"""Create synthetic document fixtures and page images for manual rendering QA."""
import io
import argparse
import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image
from app import create_app
from app.models.catalog import demo_profile,TEMPLATES
from app.services.images import normalize_image

out=Path('tmp/qa/exports');out.mkdir(parents=True,exist_ok=True)
chrome=os.getenv('CHROMIUM_EXECUTABLE')
if not chrome and Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome').exists():
    chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
app=create_app({'TESTING':True,'WTF_CSRF_ENABLED':False,'RATELIMIT_ENABLED':False,'CHROMIUM_EXECUTABLE':chrome})
client=app.test_client()
photo=io.BytesIO();Image.new('RGB',(800,1000),'#a5947e').save(photo,format='JPEG')
photo=normalize_image(photo.getvalue())
parser=argparse.ArgumentParser()
parser.add_argument('--theme',choices=[t['id'] for t in TEMPLATES])
args=parser.parse_args()
for theme in TEMPLATES:
    if args.theme and theme['id']!=args.theme:
        continue
    for variant in ['standard','hindi-long']:
        profile=demo_profile();profile['template']=theme['id']
        if variant=='hindi-long':
            profile['language']='hi';profile['sections']['personal']['name']='अनन्या श्रीनिवासन कृष्णमूर्ति'
            profile['sections']['education']=[{'degree':f'Qualification {i+1}','institution':'एक लंबा संस्थान नाम — भारतीय प्रौद्योगिकी और डिज़ाइन संस्थान'} for i in range(12)]
            profile['sections']['about']['introduction']='मुझे किताबें पढ़ना, संगीत सुनना और नई जगहों की यात्रा करना पसंद है। परिवार और मित्र मेरे लिए बहुत महत्वपूर्ण हैं। '*35
            profile['customSections']=[{'id':'custom-qa','title':'अन्य जानकारी','fields':[{'label':'भाषाएँ','value':'हिन्दी, मराठी, अंग्रेज़ी'},{'label':'लंबा विवरण','value':'A'*500}]}]
            profile['photos']=[photo]*5
        response=client.post('/api/export/pdf',json=profile)
        assert response.status_code==200,response.json
        stem=f'{theme["id"]}-{variant}'
        (out/f'{stem}.pdf').write_bytes(response.data)
        parsed=PdfReader(io.BytesIO(response.data))
        text=''.join(page.extract_text() for page in parsed.pages)
        if variant=='hindi-long':
            assert 'Qualification 12' in text
            assert 'अनन्या' in text
            assert text.count('A')>=500
        with pdfium.PdfDocument(response.data) as pdf:
            for i in range(len(pdf)):
                page=pdf[i];bitmap=page.render(scale=1.2);image=bitmap.to_pil();image.save(out/f'{stem}-{i+1}.png');bitmap.close();page.close()
        print(stem,len(parsed.pages),'pages',len(response.data),'bytes')
