from app import create_app


def test_untrusted_host_returns_400_without_rendering_error_template(client):
    for path in ('/', '/api/preview'):
        response = client.get(path, base_url='https://untrusted.example')
        assert response.status_code == 400
        assert response.json == {'error': 'Invalid request host.'}
        assert response.headers['X-Content-Type-Options'] == 'nosniff'


def test_configured_pythonanywhere_host_serves_landing_and_editor():
    app = create_app({'TESTING': True, 'SECRET_KEY': 'hosting-test',
                      'RATELIMIT_ENABLED': False,
                      'TRUSTED_HOSTS': ['priyankjam.pythonanywhere.com']})
    client = app.test_client()
    for path in ('/', '/create'):
        assert client.get(path, base_url='https://priyankjam.pythonanywhere.com').status_code == 200
    assert client.get('/', base_url='https://untrusted.example').status_code == 400
