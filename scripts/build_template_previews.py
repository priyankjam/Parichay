"""Build gallery images from fictional data and the supplied dummy portrait.

These are public static marketing assets, never snapshots of a user's draft.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.models.catalog import TEMPLATES, demo_profile
from app.models.profile import Profile
from app.services.rendering import export_document
import pypdfium2 as pdfium

out = Path('app/static/artwork/thumbnails')
qa = Path('tmp/qa/template-previews')
out.mkdir(parents=True, exist_ok=True)
qa.mkdir(parents=True, exist_ok=True)
app = create_app({'TESTING': True, 'RATELIMIT_ENABLED': False})
with app.app_context():
    for design in TEMPLATES:
        if design['id'].startswith('craft-'):
            continue  # Complete collection samples: build_collection_gallery.py
        profile = demo_profile(include_photo=True)
        profile['template'] = design['id']
        profile['sections']['personal'].pop('nativePlace', None)
        profile['sections']['personal'].pop('motherTongue', None)
        profile['sections']['education'] = [{'degree': 'M.Des, Interaction Design'}]
        profile['sections']['career'] = [{'role': 'Product Designer', 'company': 'Independent studio'}]
        profile['sections']['family']['siblings'] = 'One younger sister'
        profile['sections']['about'] = {}
        profile['sections']['partner'] = {}
        pdf, _, _ = export_document(Profile.parse(profile).document(), 'pdf')
        with pdfium.PdfDocument(pdf) as document:
            assert len(document) == 1, (design['id'], len(document))
            page = document[0]
            bitmap = page.render(scale=1.5)
            image = bitmap.to_pil().convert('RGB')
            image.save(qa / f"{design['id']}.png")
            hero_name = {'ivory': 'ivory', 'figma-peach-floral': 'peach'}.get(design['id'])
            if hero_name:
                hero = image.copy()
                hero.thumbnail((650, 920))
                hero.save(out.parent / f'hero-{hero_name}.webp', 'WEBP', quality=90, method=6)
            image.thumbnail((357, 506))
            image.save(out / f"{design['id']}.webp", 'WEBP', quality=90, method=6)
            bitmap.close()
            page.close()
        print(design['id'], flush=True)
