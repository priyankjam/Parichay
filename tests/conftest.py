import os
from pathlib import Path
import pytest
from app import create_app

@pytest.fixture
def app():
    chrome=os.getenv('CHROMIUM_EXECUTABLE')
    if not chrome and Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome').exists():
        chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    return create_app({'TESTING': True, 'SECRET_KEY': 'test-secret-not-for-production',
                       'WTF_CSRF_ENABLED': False, 'RATELIMIT_ENABLED': False,
                       'CHROMIUM_EXECUTABLE': chrome})

@pytest.fixture
def client(app):
    return app.test_client()
