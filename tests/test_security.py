import io
import pytest
from PIL import Image
from app import create_app
from app.models.catalog import demo_profile
from app.services.images import normalize_image, normalize_data_image
from app.models.profile import ValidationError


def test_headers_and_no_public_profiles(client):
    result = client.get('/')
    assert result.status_code == 200
    assert result.headers['Cache-Control'] == 'no-store, private'
    assert "script-src 'self'" in result.headers['Content-Security-Policy']
    assert result.headers['X-Frame-Options'] == 'DENY'
    assert client.get('/p/aarav').status_code == 404
    assert client.get('/api/profile/1').status_code == 404


def test_csrf_rejects_untrusted_exports():
    app = create_app({'TESTING': True, 'SECRET_KEY':'test', 'RATELIMIT_ENABLED':False})
    client = app.test_client()
    assert client.post('/api/export/pdf', json=demo_profile()).status_code == 400
    assert client.post('/api/images/validate', data={}).status_code == 400


def test_invalid_export_does_not_start_renderer(client):
    assert client.post('/api/export/pdf', json={}).status_code == 422
    assert client.post('/api/export/word', json=demo_profile()).status_code == 404
    assert client.post('/api/export/pdf', data='not json').status_code == 422


def test_html_is_escaped(app):
    from flask import render_template
    from app.models.profile import Profile
    raw = demo_profile(); raw['sections']['personal']['name']='<script>alert(1)</script>'
    with app.app_context():
        html = render_template('document.html', doc=Profile.parse(raw).document(), css='')
    assert '<script>' not in html
    assert '&lt;script&gt;' in html


def test_images_are_reencoded_and_metadata_stripped():
    original = Image.new('RGB',(2200,1000),'#776655')
    output=io.BytesIO(); original.save(output,format='JPEG',comment=b'private metadata')
    data=normalize_image(output.getvalue())
    assert data.startswith('data:image/jpeg;base64,')
    import base64
    decoded=base64.b64decode(data.split(',')[1])
    with Image.open(io.BytesIO(decoded)) as image:
        assert max(image.size)<=1600
        assert not image.getexif()
        assert 'comment' not in image.info


@pytest.mark.parametrize('data', [b'<svg xmlns="http://www.w3.org/2000/svg"></svg>', b'not an image', b'x'*(8*1024*1024+1)])
def test_bad_uploads(data):
    with pytest.raises(ValidationError): normalize_image(data)


def test_bad_data_urls():
    for url in ['file:///etc/passwd','https://localhost/private','data:image/jpeg;base64,%%%']:
        with pytest.raises(ValidationError): normalize_data_image(url)


def test_upload_endpoint(client):
    out=io.BytesIO();Image.new('RGB',(40,40),'white').save(out,format='PNG');out.seek(0)
    result=client.post('/api/images/validate',data={'photo':(out,'../../evil.html')})
    assert result.status_code==200
    assert result.json['image'].startswith('data:image/jpeg;base64,')
    assert client.post('/api/images/validate',data={}).status_code==400


def test_export_service_failure_is_recoverable(client,monkeypatch):
    from app.services.rendering import ExportError
    def fail(*args):
        raise ExportError('busy','Please retry shortly.')
    monkeypatch.setattr('app.routes.exports.export_document',fail)
    response=client.post('/api/export/pdf',json=demo_profile())
    assert response.status_code==503
    assert response.json['error']=='Please retry shortly.'
    assert 'no-store' in response.headers['Cache-Control']


def test_rate_limit_has_actionable_error():
    app=create_app({'TESTING':True,'SECRET_KEY':'test','WTF_CSRF_ENABLED':False,
                    'RATELIMIT_ENABLED':True,'RATELIMIT_STORAGE_URI':'memory://'})
    client=app.test_client()
    for _ in range(6):
        assert client.post('/api/export/pdf',json={}).status_code==422
    response=client.post('/api/export/pdf',json={})
    assert response.status_code==429
    assert 'wait' in response.json['error']


def test_landing_precedes_editor(client):
    home = client.get('/').get_data(as_text=True)
    assert 'Create my biodata' in home
    assert 'id="step-content"' not in home
    assert '/create' in home
    editor = client.get('/create').get_data(as_text=True)
    assert 'id="step-content"' in editor
    assert 'id="section-jump"' in editor
    assert '<dialog id="preview-dialog"' in editor
    hindi = client.get('/?lang=hi').get_data(as_text=True)
    assert 'अपना बायोडाटा बनाएँ' in hindi
