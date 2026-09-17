import os
import secrets


class Config:
    APP_ENV = os.getenv('APP_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY') or (secrets.token_hex(32) if APP_ENV != 'production' else None)
    MAX_CONTENT_LENGTH = 18 * 1024 * 1024
    MAX_FORM_MEMORY_SIZE = 128 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = APP_ENV == 'production'
    WTF_CSRF_TIME_LIMIT = None  # Long editing sessions; token is still session-bound.
    RATELIMIT_STORAGE_URI = os.getenv('RATELIMIT_STORAGE_URI', 'memory://')
    RATELIMIT_HEADERS_ENABLED = True
    CHROMIUM_EXECUTABLE = os.getenv('CHROMIUM_EXECUTABLE') or None
    RENDER_PYTHON_EXECUTABLE = os.getenv('RENDER_PYTHON_EXECUTABLE') or None
    EXPORT_TIMEOUT_SECONDS = int(os.getenv('EXPORT_TIMEOUT_SECONDS', '40'))
    TRUSTED_HOSTS = [h.strip() for h in os.getenv('TRUSTED_HOSTS', 'localhost,127.0.0.1').split(',')]
