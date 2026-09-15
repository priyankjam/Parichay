"""Public gallery samples: fictional data only, rendered through the export pipeline."""
import base64,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.models.catalog import TEMPLATES,demo_profile
from app.models.profile import Profile
from app.services.rendering import preview_document
app=create_app({'TESTING':True,'RATELIMIT_ENABLED':False})
out=Path('app/static/artwork/gallery-v1');out.mkdir(exist_ok=True)
with app.app_context():
 for gender in ('male','female'):
  for language in ('en','hi'):
   for design in TEMPLATES:
    target=out/f'{gender}-{language}-{design["id"]}.webp'
    if target.exists():continue
    data=demo_profile(include_photo=True);data.update(gender=gender,language=language,template=design['id'])
    if gender=='female':
     data['sections']['personal']['name']='अनन्या मेहता' if language=='hi' else 'Ananya Mehta'
     data['photos']=['data:image/jpeg;base64,'+base64.b64encode(Path('app/static/artwork/demo-portrait-female.jpg').read_bytes()).decode()]
    result=preview_document(Profile.parse(data).document(),True)
    target.write_bytes(base64.b64decode(result['pages'][0]))
    print(target.name,flush=True)
