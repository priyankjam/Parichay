from flask import Flask, jsonify, request, render_template
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import HTTPException, SecurityError
from .config import Config

csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=['120 per minute'])


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    if not app.config['SECRET_KEY']:
        raise RuntimeError('Set a strong SECRET_KEY before starting production.')
    csrf.init_app(app)
    limiter.init_app(app)
    from .routes.editor import bp as editor
    from .routes.exports import bp as exports
    app.register_blueprint(editor)
    app.register_blueprint(exports)

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        # Flask-WTF requires a same-origin Referer for HTTPS POSTs. Do not send
        # it to other sites, but retain it for our preview/export requests.
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; font-src 'self'; connect-src 'self'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        )
        response.headers['X-Robots-Tag'] = 'noindex, nofollow'
        if request.path.startswith(('/static/artwork/collection-v1/', '/static/artwork/collection-gallery-v1/', '/static/artwork/collection-gallery-v2/', '/static/artwork/repair-gallery-v2/')):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        elif request.path.startswith('/static/fonts/'):
            response.headers['Cache-Control'] = 'public, max-age=86400'
        elif request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'no-cache'
        else:
            response.headers['Cache-Control'] = 'no-store, private'
        if app.config['SESSION_COOKIE_SECURE']:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        return response

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return jsonify(error='Your session changed. Refresh this page; your saved draft will remain.'), 400

    @app.errorhandler(HTTPException)
    def http_error(error):
        # Host validation runs before Flask can build URLs. Rendering the normal
        # error template here would fail again when it calls url_for().
        if isinstance(error, SecurityError):
            return jsonify(error='Invalid request host.'), 400
        messages = {413: 'This file is too large. Use photos under 8 MB each.',
                    429: 'Please wait a minute before trying again.',
                    404: 'This page could not be found.'}
        message = messages.get(error.code, 'The request could not be completed.')
        if request.path.startswith('/api/'):
            return jsonify(error=message), error.code
        return render_template('error.html', message=message), error.code

    @app.errorhandler(Exception)
    def unexpected_error(error):
        # Do not include request payloads, photo data or stack locals in logs.
        app.logger.error('Request failed: %s', type(error).__name__)
        message = 'Something went wrong. Your local draft is safe. Please try again.'
        if request.path.startswith('/api/'):
            return jsonify(error=message), 500
        return render_template('error.html', message=message), 500

    return app
