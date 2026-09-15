from flask import Blueprint, render_template, jsonify, request, url_for
from app.models.catalog import SECTIONS, TEMPLATES, empty_profile, demo_profile
from app.models.collection import COLLECTION

bp = Blueprint('editor', __name__)


@bp.get('/')
def index():
    language = request.args.get('lang', 'en')
    if language not in ('en', 'hi'):
        language = 'en'
    return render_template('landing.html', language=language,
                           designs=[TEMPLATES[i] for i in [0,4,5,11,16,18]], design_count=len(TEMPLATES))


@bp.get('/create')
def create():
    new_draft = empty_profile()
    new_draft['template'] = 'craft-editorial-ivory'
    designs = [*COLLECTION, *(d for d in TEMPLATES if not d['id'].startswith('craft-'))]
    return render_template('editor.html', config_data=dict(sections=SECTIONS, templates=designs,
                           empty=new_draft, demo=demo_profile(), demoPhoto=url_for('static', filename='artwork/demo-portrait.jpg'),
                           demoPhotos={'male': url_for('static', filename='artwork/demo-portrait.jpg'),
                                       'female': url_for('static', filename='artwork/demo-portrait-female.jpg')}))


@bp.get('/health')
def health():
    return jsonify(status='ok')
