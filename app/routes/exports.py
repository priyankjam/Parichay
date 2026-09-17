import io
from flask import Blueprint, request, jsonify, current_app, send_file
from app import limiter
from app.models.profile import Profile, ValidationError
from app.services.images import normalize_image
from app.services.rendering import export_document, preview_document, ExportError

bp = Blueprint('exports', __name__, url_prefix='/api')


@bp.post('/preview')
@limiter.limit('60 per minute')
def preview():
    raw = request.get_json(silent=True)
    if not isinstance(raw, dict) or not isinstance(raw.get('thumbnail', False), bool):
        return jsonify(error='Choose a valid preview request.'), 422
    try:
        profile = Profile.parse(raw.get('profile'))
        document = profile.document()
        if not document['name'] and not document['sections']:
            raise ValidationError('Add at least one included detail to preview your biodata.')
        return jsonify(preview_document(document, raw.get('thumbnail', False)))
    except ValidationError as error:
        return jsonify(error=str(error)), 422
    except ExportError as error:
        current_app.logger.warning('Preview did not complete (%s)', error.code)
        response = jsonify(error=error.public_message)
        response.status_code = 503
        if error.code == 'busy':
            response.headers['Retry-After'] = '2'
        return response


@bp.post('/images/validate')
@limiter.limit('20 per minute')
def upload():
    photo = request.files.get('photo')
    if not photo:
        return jsonify(error='Choose a photo first.'), 400
    try:
        # Original filename is never used; no upload is persisted.
        return jsonify(image=normalize_image(photo.stream.read(8 * 1024 * 1024 + 1)))
    except ValidationError as e:
        return jsonify(error=str(e)), 422


@bp.post('/export/<kind>')
@limiter.limit('6 per minute')
def export(kind):
    if kind not in ('pdf', 'png', 'jpg'):
        return jsonify(error='Choose PDF, PNG or JPG.'), 404
    try:
        raw = request.get_json(silent=True)
        profile = Profile.parse(raw)
        document = profile.document()
        treatment = request.args.get('paper', 'original')
        if treatment not in ('original', 'light') or (treatment == 'light' and document['template'] != 'figma-ganesha-maroon'):
            raise ValidationError('Choose a supported print treatment.')
        document['print_treatment'] = treatment
        if not document['name'] and not document['sections']:
            raise ValidationError('Add at least one visible detail before exporting.')
        payload, mimetype, extension = export_document(document, kind)
        return send_file(io.BytesIO(payload), mimetype=mimetype, as_attachment=True,
                         download_name=f'parichay-biodata.{extension}', max_age=0)
    except ValidationError as error:
        return jsonify(error=str(error)), 422
    except ExportError as error:
        current_app.logger.warning('Export did not complete (%s)', error.code)
        return jsonify(error=error.public_message), 503
