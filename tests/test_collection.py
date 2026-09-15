import copy
import json
from pathlib import Path
import pytest
from app.models.catalog import empty_profile, TEMPLATES
from app.models.profile import Profile, ValidationError
from app.models.collection import COLLECTION, resolve_presentation
from app.services.collection import arrange_sections, SCRIPT_FONTS
from app.services.rendering import build_document_html


def test_layout_registry_is_independent_and_unique():
    ids=[d['id'] for d in COLLECTION]
    assert len(ids)==len(set(ids))
    assert len({d['layout_id'] for d in COLLECTION})>=4
    for d in COLLECTION:
        assert d['supports_no_photo'] and d['default_sacred_art'] in d['supported_sacred_art']
        assert not any(k in d for k in ('allowed_caste','target_caste','auto_religion'))
        assert (Path('docs/template-collection/specs')/f'{d["number"]:02d}-{d["slug"]}.md').exists()
        for asset in d['assets']:
            assert Path(f'app/static/artwork/collection-v1/{asset}-pdf.webp').exists()


def test_identity_does_not_select_design_or_header():
    p=empty_profile();p['template']=COLLECTION[0]['id'];p['sections']['personal'].update(name='Any surname',city='Mathura');p['sections']['culture']={'religion':'Any religion','caste':'Any caste'}
    parsed=Profile.parse(p).data
    assert parsed['template']==p['template']
    assert parsed['presentation']['sacred_art']=='default'
    assert resolve_presentation(COLLECTION[0],parsed['presentation'])['id']=='none'


def test_explicit_header_none_and_compatible_choices():
    for d in COLLECTION:
        assert resolve_presentation(d,{'sacred_art':'none'})['id']=='none'
        for value in d['supported_sacred_art']:
            assert resolve_presentation(d,{'sacred_art':value})['id']==value
        if 'cross' not in d['supported_sacred_art']:
            assert resolve_presentation(d,{'sacred_art':'cross'})['id']==d['default_sacred_art']


@pytest.mark.parametrize('presentation',[None,[],{'direction':'sideways'},{'sacred_art':'../../secret'},{'salutation':'yes'}])
def test_rejects_invalid_presentation(presentation):
    p=empty_profile();p['presentation']=presentation
    with pytest.raises(ValidationError):Profile.parse(p)


def test_old_backups_get_safe_defaults():
    p=empty_profile();p.pop('presentation');assert Profile.parse(p).data['presentation']==dict(sacred_art='default',direction='auto',salutation=False)


def test_hidden_header_metadata_and_html_escaping(app):
    p=empty_profile();p['template']=COLLECTION[0]['id'];p['sections']['personal']={'name':'<script>unsafe()</script>','city':'HIDDEN-CITY'};p['sections']['career']=[{'role':'HIDDEN-ROLE'}];p['hiddenFields']=['personal.0.city','career.0.role'];p['sections']['culture']={'religion':'SECRET'};p['hiddenSections']=['culture']
    with app.app_context():html=build_document_html(Profile.parse(p).document())
    assert '<script>unsafe()' not in html and '&lt;script&gt;' in html
    assert 'HIDDEN-CITY' not in html and 'HIDDEN-ROLE' not in html and 'SECRET' not in html


def test_all_scripts_have_vendored_glyphs():
    from fontTools.ttLib import TTFont
    root=Path('app/static/fonts')
    samples={'Noto Bengali':'পরিবার','Noto Gurmukhi':'ਪਰਿਵਾਰੴ','Noto Gujarati':'પરિવાર','Noto Tamil':'குடும்பம்','Noto Telugu':'కుటుంబం','Noto Kannada':'ಕುಟುಂಬ','Noto Malayalam':'കുടുംബം','Noto Arabic':'احترام','Noto Symbols':'☬✝☸','Noto Devanagari':'शिक्षा'}
    for family,pattern,_ in SCRIPT_FONTS:
        with TTFont(next(root.glob(pattern))) as font:
            cmap=font.getBestCmap();assert all(ord(c) in cmap for c in samples[family]),family
