"""Live previews must work without Chromium and preserve disclosure boundaries."""
import re

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


def test_https_preview_with_real_session_and_strict_csrf(app):
    app.config.update(WTF_CSRF_ENABLED=True, WTF_CSRF_SSL_STRICT=True,
                      SESSION_COOKIE_SECURE=True)
    client = app.test_client()
    origin = 'https://localhost'
    editor = client.get('/create', base_url=origin)
    # A no-referrer policy strips the header Flask-WTF requires on HTTPS,
    # even when the session cookie and CSRF token are valid.
    assert editor.headers['Referrer-Policy'] == 'same-origin'
    token = re.search(r'name="csrf-token" content="([^"]+)"',
                      editor.get_data(as_text=True)).group(1)
    headers = {'X-CSRFToken': token, 'Referer': origin + '/create'}
    response = client.post('/api/preview/html', base_url=origin,
                           headers=headers, json={'profile': demo_profile()})
    assert response.status_code == 200
    assert 'Aarav Mehta' in response.json['html']
    # Keep both token and same-origin validation; don't disable CSRF to fix it.
    for invalid_headers in ({'X-CSRFToken': token},
                            {'X-CSRFToken': token, 'Referer': 'https://other.example/'},
                            {'Referer': origin + '/create'}):
        response = client.post('/api/preview/html', base_url=origin,
                               headers=invalid_headers, json={'profile': demo_profile()})
        assert response.status_code == 400
