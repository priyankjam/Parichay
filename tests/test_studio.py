"""Private preview boundary and identical export-engine dispatch."""
from app.models.catalog import demo_profile
from app.services.rendering import ExportError
import pytest


def test_preview_reuses_export_document(client, monkeypatch):
    calls = []
    def render(document, thumbnail):
        calls.append((document, thumbnail))
        return {'pageCount': 2, 'pages': ['encoded-page'], 'width': 210, 'height': 297}
    monkeypatch.setattr('app.routes.exports.preview_document', render)
    profile = demo_profile()
    profile['sections']['career'][0]['income'] = 'PRIVATE SALARY'
    profile['hiddenFields'].append('career.0.income')
    response = client.post('/api/preview', json={'profile': profile, 'thumbnail': True})
    assert response.status_code == 200
    assert response.json['pageCount'] == 2
    assert 'no-store' in response.headers['Cache-Control']
    assert calls[0][1] is True
    assert 'PRIVATE SALARY' not in str(calls[0][0])


def test_preview_rejects_invalid_request(client):
    for value in [None, [], {'profile': {}}, {'profile': demo_profile(), 'thumbnail': 'yes'}]:
        assert client.post('/api/preview', json=value).status_code == 422
    assert client.get('/api/preview').status_code == 405


def test_preview_csrf(app):
    app.config['WTF_CSRF_ENABLED'] = True
    assert app.test_client().post('/api/preview', json={'profile': demo_profile()}).status_code == 400


@pytest.mark.parametrize('code,retry_after', [('busy', '2'), ('renderer', None), ('timeout', None)])
def test_preview_only_retries_temporary_capacity(client, monkeypatch, code, retry_after):
    def unavailable(*args):
        raise ExportError(code)
    monkeypatch.setattr('app.routes.exports.preview_document', unavailable)
    response = client.post('/api/preview', json={'profile': demo_profile()})
    assert response.status_code == 503
    assert response.headers.get('Retry-After') == retry_after
    assert 'no-store' in response.headers['Cache-Control']
