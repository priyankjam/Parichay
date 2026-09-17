import base64
import io
import os
import unicodedata
from pathlib import Path
import pytest
from PIL import Image
from pypdf import PdfReader
from app.models.catalog import TEMPLATES, empty_profile
from app.models.designs import FIGMA_DESIGNS
from app.models.profile import Profile


def test_catalog_artwork_and_disclosure_remain_independent():
    from app.models.collection import COLLECTION
    assert len(TEMPLATES) == 19 + len(COLLECTION) and len({d['id'] for d in TEMPLATES}) == len(TEMPLATES)
    for design in FIGMA_DESIGNS:
        assert Path('app' + design['background']).is_file()
        profile = empty_profile(); profile['template'] = design['id']
        profile['sections']['personal']['name'] = 'Keep my name'
        profile['sections']['culture']['religion'] = 'PRIVATE-CULTURE'
        profile['hiddenSections'] = ['culture']
        doc = Profile.parse(profile).document()
        assert doc['illustrated'] and doc['name'] == 'Keep my name'
        assert 'PRIVATE-CULTURE' not in str(doc)
        assert profile['sections']['family'] == {}


@pytest.mark.skipif(os.getenv('RUN_EXPORT_TESTS')!='1', reason='Real Chromium export')
@pytest.mark.parametrize('template',['figma-ganesha-maroon','figma-blossom-serif'])
def test_long_opening_section_and_multiple_photos(client, template):
    profile = empty_profile(); profile['template'] = template
    profile['sections']['personal']['name'] = 'Photo profile'
    profile['customSections'] = [{'id':'custom-long', 'title':'Full introduction',
       'fields':[{'label':'My story', 'value':('A thoughtful introduction. '*105)+' END-OF-STORY'}]}]
    image = Image.new('RGB',(600,750),'#748b73'); source=io.BytesIO();image.save(source,'JPEG')
    photo='data:image/jpeg;base64,'+base64.b64encode(source.getvalue()).decode()
    profile['photos']=[photo,photo,photo]
    result=client.post('/api/export/pdf',json=profile)
    assert result.status_code==200,result.json
    pdf=PdfReader(io.BytesIO(result.data));text=unicodedata.normalize('NFKC', ''.join(p.extract_text() for p in pdf.pages))
    assert 'END-OF-STORY' in ''.join(text.split()) and 'Photo profile' in text
    assert 2<=len(pdf.pages)<=10
    assert len(result.data)<2*1024*1024


@pytest.mark.skipif(os.getenv('RUN_EXPORT_TESTS')!='1', reason='Real Chromium export')
@pytest.mark.parametrize('kind', ['png', 'jpg'])
def test_illustrated_image_exports_keep_background(client, kind):
    profile = empty_profile()
    profile['template'] = 'figma-ganesha-festive'
    profile['sections']['personal']['name'] = 'Image export'
    result = client.post('/api/export/' + kind, json=profile)
    assert result.status_code == 200
    with Image.open(io.BytesIO(result.data)) as image:
        assert image.format == ('PNG' if kind == 'png' else 'JPEG')
        assert image.width > 1000 and image.height > image.width
        red, green, blue = image.convert('RGB').getpixel((image.width//2, image.height//2))
        assert all(abs(a-b)<=3 for a,b in zip((red,green,blue),(71,27,40))), 'The new flat maroon text field must survive image export'
