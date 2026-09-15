"""One semantic document builder shared by gallery, preview and all exports.

Layout, art and optional cultural headers are independent. Assets and typefaces
come exclusively from our registry, never from a path supplied in user content.
"""
import base64
import re
from pathlib import Path
from copy import deepcopy
from functools import lru_cache
from flask import current_app, render_template
from app.models.collection import BY_ID, LAYOUTS, ARTWORK_PACKS, resolve_presentation

SCRIPT_FONTS = [
    ('Noto Devanagari', 'NotoSansDevanagari.ttf', '\u0900-\u097f'),
    ('Noto Bengali', 'NotoSansBengali*ttf', '\u0980-\u09ff'),
    ('Noto Gurmukhi', 'NotoSansGurmukhi*ttf', '\u0a00-\u0a7f'),
    ('Noto Gujarati', 'NotoSansGujarati*ttf', '\u0a80-\u0aff'),
    ('Noto Tamil', 'NotoSansTamil*ttf', '\u0b80-\u0bff'),
    ('Noto Telugu', 'NotoSansTelugu*ttf', '\u0c00-\u0c7f'),
    ('Noto Kannada', 'NotoSansKannada*ttf', '\u0c80-\u0cff'),
    ('Noto Malayalam', 'NotoSansMalayalam*ttf', '\u0d00-\u0d7f'),
    ('Noto Arabic', 'NotoNaskhArabic*ttf', '\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff'),
    ('Noto Symbols', 'NotoSansSymbols[[]wght].ttf', '\u2600-\u27ff'),
]

@lru_cache(maxsize=64)
def file_uri(filename):
    path = Path(filename)
    kind = 'font/ttf' if path.suffix == '.ttf' else 'image/webp'
    return 'data:' + kind + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def art_uri(asset):
    return file_uri(str(Path(current_app.static_folder) / 'artwork/collection-v1' / f'{asset}-pdf.webp'))


def arrange_sections(sections, design):
    """Priorities are presentation metadata; field labels are never reimplemented."""
    priority = design['section_priority']
    def rank(section):
        key = 'custom' if section['key'].startswith('custom-') else section['key']
        return priority.index(key) if key in priority else priority.index('custom')
    ordered = sorted(deepcopy(sections), key=rank)
    layout = design['layout_id']
    # Full-width prose and narrow metadata receive different measures. Pairing
    # at section boundaries lets the paginator carry entire sections together.
    two_column = LAYOUTS[layout]['columns'] == 2
    if not two_column:
        return [{'sections': [s]} for s in ordered]
    units, pending = [], []
    def flush():
        if not pending: return
        left, right = [], []
        if design['right_sections']:
            for section in pending:
                key = 'custom' if section['key'].startswith('custom-') else section['key']
                (right if key in design['right_sections'] else left).append(section)
        else:
            scores = [0, 0]
            for section in pending:
                lane = 0 if scores[0] <= scores[1] else 1
                (left if lane == 0 else right).append(section)
                scores[lane] += 70 + sum(35 + len(r['value']) for g in section['groups'] for r in g)
        if left and right:
            units.append({'columns': [left, right]})
        else:
            units.extend({'sections': [s]} for s in (left or right))
        pending.clear()
    for section in ordered:
        length = sum(len(r['value']) for g in section['groups'] for r in g)
        wide = section['key'] == 'contact' or length > 900 or (section['key'] == 'about' and design['id'] == 'craft-sage-botanical')
        if wide:
            flush(); units.append({'sections': [section]})
        else:
            pending.append(section)
    flush()
    return units


def build_collection_html(document):
    design = deepcopy(BY_ID[document['template']])
    pack = ARTWORK_PACKS.get(design['artwork_pack_id'])
    if pack: design['art_placement'] = pack['placement']
    sacred = resolve_presentation(design, document.get('presentation', {}))
    if sacred.get('asset'): sacred['src'] = art_uri(sacred['asset'])
    doc = deepcopy(document)
    doc['units'] = arrange_sections(doc['sections'], design)
    # Derive header metadata only from visible, normalized rows.
    rows = {s['key']: [r for g in s['groups'] for r in g] for s in doc['sections']}
    def first(section, key):
        return next((r['value'] for r in rows.get(section, []) if r.get('key') == key), '')
    doc['subtitle'] = ' · '.join(v for v in [first('career', 'role'), first('personal', 'city')] if v)
    doc['direction'] = sacred['direction']
    doc['continued'] = 'जारी' if doc['language'] == 'hi' else 'continued'
    static = Path(current_app.static_folder)
    css = (static / 'css/collection-document.css').read_text()
    text = str(doc) + sacred.get('symbol', '') + ('जय भीम' if sacred['salutation'] else '')
    fonts = [('Parichay Serif','DMSerifDisplay.ttf'), ('Parichay Sans','DMSans.ttf')]
    fallback = []
    for family, pattern, characters in SCRIPT_FONTS:
        if re.search('[' + characters + ']', text):
            matches = list((static/'fonts').glob(pattern))
            if not matches: raise RuntimeError(f'Missing vendored typeface: {family}')
            fonts.append((family, matches[0].name)); fallback.append(f'"{family}"')
    for family, filename in fonts:
        css += f'\n@font-face{{font-family:"{family}";src:url("{file_uri(str(static / "fonts" / filename))}") format("truetype");font-weight:100 900;font-display:block;}}'
    fallback = ','.join(fallback + ['sans-serif'])
    css += f'\n.craft-document{{--doc-font-body:"Parichay Sans",{fallback};--doc-font-display:"Parichay Serif",{fallback};--doc-paper:{design["palette"][0]};--doc-accent:{design.get("text_accent", design["palette"][1])};--doc-detail:{design["palette"][2]};}}'
    art = art_uri(design['artwork_pack_id']) if design['artwork_pack_id'] != 'none' else None
    return render_template('collection-document.html', doc=doc, design=design, sacred=sacred, art=art, css=css)
