import pytest
from app.models.repair import REGISTRY
from app.models.catalog import TEMPLATES,demo_profile
from app.models.profile import Profile
from app.services.rendering import build_document_html


def test_all_saved_template_ids_have_explicit_compositions():
    assert set(REGISTRY)=={t['id'] for t in TEMPLATES}
    assert len(REGISTRY)==49
    assert len({(x['layout'],x['header'],x['style']) for x in REGISTRY.values()})==49


def test_removed_designs_are_not_available_but_old_drafts_still_open():
    from app.models.catalog import AVAILABLE_TEMPLATES
    removed={'craft-nikah-nocturne','craft-christian-cathedral-ivory'}
    assert len(AVAILABLE_TEMPLATES)==47
    assert not removed & {d['id'] for d in AVAILABLE_TEMPLATES}
    assert 'craft-cathedral-cross' in {d['id'] for d in AVAILABLE_TEMPLATES}
    for id in removed:
        raw=demo_profile();raw['template']=id
        assert Profile.parse(raw).data['template']==id


def test_print_treatment_requires_deliberate_supported_selection(client,monkeypatch):
    captured=[]
    def capture(doc,kind):
        captured.append(doc)
        return b'%PDF-test','application/pdf','pdf'
    monkeypatch.setattr('app.routes.exports.export_document',capture)
    p=demo_profile();p['template']='figma-ganesha-maroon'
    assert client.post('/api/export/pdf?paper=light',json=p).status_code==200
    assert captured[-1]['print_treatment']=='light'
    assert client.post('/api/export/pdf',json=p).status_code==200
    assert captured[-1]['print_treatment']=='original'
    p['template']='editorial'
    assert client.post('/api/export/pdf?paper=light',json=p).status_code==422


def test_invocation_is_real_text_and_old_watermark_is_absent(app):
    with app.app_context():
        for id in ['figma-ganesha-ivory','figma-ganesha-rose','figma-ganesha-maroon','figma-ganesha-festive']:
            p=demo_profile();p['template']=id
            html=build_document_html(Profile.parse(p).document())
            assert 'श्री गणेशाय नमः' in html
            assert '--design-bg' not in html
            assert 'r-devotion' in html
