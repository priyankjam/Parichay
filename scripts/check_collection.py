"""Deterministic fictional fixtures, real Chromium/PDF pipeline, geometry and text QA."""
import argparse,base64,json,sys,copy,io
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.models.catalog import empty_profile,demo_profile
from app.models.profile import Profile
from app.models.collection import COLLECTION
from app.services.rendering import build_document_html,export_document
from playwright.sync_api import sync_playwright
import pypdfium2 as pdfium
from PIL import Image,ImageOps,ImageDraw

def fixtures():
    short=empty_profile();short['sections'].update(personal={'name':'Aarav Mehta','age':'29','height':'178 cm','city':'Bengaluru'},education=[{'degree':'M.Des, Interaction Design'}],career=[{'role':'Product Designer'}],family={'father':'Rajesh Mehta · Architect','mother':'Neeta Mehta · Teacher'},contact={'email':'aarav@example.com'})
    medium=demo_profile(True);medium['sections']['personal'].update(maritalStatus='Never married',nationality='Indian');medium['sections']['contact']={'name':'Aarav Mehta','email':'aarav@example.com'}
    long=copy.deepcopy(medium);long['sections']['about']['introduction']=('I value kindness, curiosity and an equal partnership. I enjoy reading, photography and long walks, and make time for the people around me.\n\n'*28).strip();long['sections']['career']=[{'role':f'Design role {i+1}','company':'Independent studio','description':'I work with a thoughtful team to build useful products.'} for i in range(5)];long['sections']['education']*=3
    long['sections']['family']['siblings']='\n'.join(f'Sibling {i+1}: A postgraduate student who enjoys music and the outdoors.' for i in range(8));long['sections']['culture']={'religion':'Included only by choice','community':'Optional community','gotra':'Optional detail'};long['sections']['astrology']={'birthDate':'1996-06-16','birthTime':'10:30','birthPlace':'Bengaluru'};long['customSections']=[{'id':'custom-values','title':'Values and everyday life','fields':[{'label':'A shared life','value':'We make decisions together and respect one another. '*18}]}];long['photos']*=3
    missing=copy.deepcopy(medium);missing['hiddenSections']=['family','culture','about','astrology','photos']
    no_photo=copy.deepcopy(medium);no_photo['photos']=[]
    scripts={'hi':'आरव मेहता · शिक्षा और परिवार · समानता और सम्मान','mr':'आनंद पाटील · शिक्षण आणि कुटुंब · समानता','gu':'આરવ મહેતા · શિક્ષણ અને પરિવાર','pa':'ਅਮਨਦੀਪ ਸਿੰਘ · ਸਿੱਖਿਆ ਅਤੇ ਪਰਿਵਾਰ','bn':'অর্ণব সেন · শিক্ষা এবং পরিবার','ta':'அருண் குமார் · கல்வி மற்றும் குடும்பம்','te':'అరవింద్ కుమార్ · విద్య మరియు కుటుంబం','kn':'ಅರುಣ್ ಕುಮಾರ್ · ಶಿಕ್ಷಣ ಮತ್ತು ಕುಟುಂಬ','ml':'അരുൺ കുമാർ · വിദ്യാഭ്യാസവും കുടുംബവും','ur':'احمد علی · تعلیم اور خاندان · احترام اور برابری'}
    multi=copy.deepcopy(medium);multi['language']='hi';multi['sections']['personal']['name']='आरव मेहता';multi['customSections']=[{'id':'custom-languages','title':'अपनी भाषा में','fields':[{'label':k,'value':v} for k,v in scripts.items()]}]
    rtl=copy.deepcopy(short);rtl['presentation']['direction']='rtl';rtl['sections']['personal']['name']=scripts['ur'];rtl['sections']['about']={'introduction':'میں ایک ایسا رشتہ چاہتا ہوں جس میں احترام، دوستی اور برابری ہو۔ '*18}
    return {'short':short,'medium':medium,'long':long,'no-photo':no_photo,'missing':missing,'multilingual':multi,'rtl':rtl}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--batch',type=int,required=True);parser.add_argument('--quick',action='store_true');args=parser.parse_args()
    app=create_app({'TESTING':True,'RATELIMIT_ENABLED':False});out=Path(f'output/template-collection/batch-{args.batch}');out.mkdir(parents=True,exist_ok=True)
    cases=fixtures();fixtures_dir=Path('docs/template-collection/test-profiles');fixtures_dir.mkdir(exist_ok=True)
    for name,data in cases.items():
        # Real fictional demo photo assets are referenced without duplicating base64 in the docs.
        fixture=copy.deepcopy(data);fixture['photos']=['@demo-portrait.jpg']*len(fixture['photos']);(fixtures_dir/(name+'.json')).write_text(json.dumps(fixture,ensure_ascii=False,indent=2))
    report=[];thumbs=[]
    with app.app_context(),sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=app.config['CHROMIUM_EXECUTABLE'],headless=True,chromium_sandbox=True)
        context=browser.new_context(java_script_enabled=False);context.route('**/*',lambda route:route.abort());page=context.new_page();page.emulate_media(media='print')
        paginator=Path('app/static/js/collection-paginator.js').read_text()
        for design in [d for d in COLLECTION if d['batch']==args.batch]:
            for name,data in cases.items():
                if args.quick and name!='medium':continue
                raw=copy.deepcopy(data);raw['template']=design['id'];doc=Profile.parse(raw).document();page.set_content(build_document_html(doc),wait_until='load');page.evaluate('document.fonts.ready');geo=page.evaluate(paginator)
                fonts=page.locator('.craft-value').evaluate_all('(els)=>els.map(e=>parseFloat(getComputedStyle(e).fontSize))');assert not fonts or min(fonts)>=14
                assert not page.locator('.continuation .sacred-art,.continuation .craft-art').count()
                if name in ('no-photo','missing'):assert page.locator('.craft-portrait').count()==0
                if name=='missing':assert page.locator('[data-section=family],[data-section=about]').count()==0
                pdf=page.pdf(format='A4',print_background=True,prefer_css_page_size=True,tagged=True,margin={k:'0' for k in ['top','right','bottom','left']})
                target=out/f'{design["slug"]}-{name}.pdf';target.write_bytes(pdf)
                with pdfium.PdfDocument(pdf) as rendered:
                    assert len(rendered)==geo['pages'],(target,len(rendered),geo)
                    assert abs(rendered[0].get_width()-595.28)<1 and abs(rendered[0].get_height()-841.89)<1
                    text=''.join(p.get_textpage().get_text_range() for p in rendered)
                    if name not in ('multilingual','rtl'):assert 'Aarav' in text
                    if name=='long':assert 'A shared life' in text and 'Design role 5' in text
                    if name=='medium':
                        image=rendered[0].render(scale=1.2).to_pil().convert('RGB');image.save(out/f'{design["slug"]}.png');ImageOps.grayscale(image).save(out/f'{design["slug"]}-grayscale.png');image.thumbnail((280,396));thumbs.append((design['name'],image.copy()))
                        web=rendered[0].render(scale=300/rendered[0].get_width()).to_pil().convert('RGB');dest=Path('app/static/artwork/thumbnails')/f'{design["id"]}.webp';web.save(dest,'WEBP',quality=87)
                    if name=='long':rendered[len(rendered)-1].render(scale=.9).to_pil().save(out/f'{design["slug"]}-continuation.png')
                report.append({'template':design['id'],'case':name,'pages':geo['pages'],'bytes':len(pdf),'geometry':geo['violations'],'minimum_body_pt':min(fonts)*.75 if fonts else None,'A4':True,'selectable_text':True})
                print(design['name'],name,geo['pages'],flush=True)
            if not args.quick:
                # Exercise the actual isolated subprocess API for each template too.
                raw=copy.deepcopy(cases['short']);raw['template']=design['id'];pdf,kind,ext=export_document(Profile.parse(raw).document(),'pdf');assert pdf.startswith(b'%PDF') and ext=='pdf'
        browser.close()
    cols=min(3,len(thumbs));sheet=Image.new('RGB',(cols*310,((len(thumbs)+cols-1)//cols)*438),'#e9e3d8');draw=ImageDraw.Draw(sheet)
    for i,(name,im) in enumerate(thumbs):x=(i%cols)*310+15;y=(i//cols)*438;draw.text((x,y+8),name,fill='#292329');sheet.paste(im,(x,y+30))
    sheet.save(out/'contact-sheet.jpg');(out/('quick-report.json' if args.quick else 'report.json')).write_text(json.dumps(report,indent=2));print('PASS',len(report),'cases',flush=True)
if __name__=='__main__':main()
