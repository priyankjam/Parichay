"""Live previews must work without Chromium and preserve disclosure boundaries."""
from app.models.catalog import demo_profile


def test_html_preview_never_launches_browser(client, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('HTML previews must not start an export process')
    monkeypatch.setattr('app.services.rendering.subprocess.Popen', forbidden)
    profile = demo_profile()
    profile['sections']['career'][0]['income'] = 'PRIVATE SALARY'
    profile['hiddenFields'].append('career.0.income')
    profile['sections']['personal']['name'] = '<script>alert("x")</script>'
    response = client.post('/api/preview/html', json={'profile': profile})
    assert response.status_code == 200
    assert 'no-store' in response.headers['Cache-Control']
    html = response.json['html']
    assert 'PRIVATE SALARY' not in str(response.json)
    assert '<script>' not in html
    assert '&lt;script&gt;' in html
    assert '/static/fonts/' in html
    assert 'data:font' not in html
    assert 'repaired-document' in html
    assert 'r-source' in html  # Browser performs pagination after fonts load.
    assert 'pdf' not in response.json


def test_html_preview_validates_profile(client):
    for raw in [None, [], {}, {'profile': {}}, {'profile': {'template': 'missing'}}]:
        assert client.post('/api/preview/html', json=raw).status_code == 422


def test_html_preview_requires_csrf(app):
    app.config['WTF_CSRF_ENABLED'] = True
    response = app.test_client().post('/api/preview/html', json={'profile': demo_profile()})
    assert response.status_code == 400
