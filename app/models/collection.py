"""Curated metadata only: identity never participates in template selection."""
import json
from copy import deepcopy
from pathlib import Path

BASE_COLLECTION = json.loads((Path(__file__).resolve().parents[1] / 'biodata_templates/collection.json').read_text())
VARIANTS = json.loads((Path(__file__).resolve().parents[1] / 'biodata_templates/variants.json').read_text())
LAYOUTS = json.loads((Path(__file__).resolve().parents[1] / 'biodata_templates/layouts.json').read_text())
ARTWORK_PACKS = json.loads((Path(__file__).resolve().parents[1] / 'biodata_templates/artwork-packs.json').read_text())
SACRED_ART = {
    'none': {'label': 'None'},
    'krishna': {'label': 'Krishna', 'asset': 'krishna'},
    'ganesha': {'label': 'Ganesha', 'asset': 'ganesha'},
    'rama': {'label': 'Rama', 'asset': 'rama'},
    'ambedkar': {'label': 'Dr. B. R. Ambedkar', 'asset': 'ambedkar'},
    'ik-onkar': {'label': 'Ik Onkar', 'symbol': '\u0a74', 'font': 'Noto Gurmukhi'},
    'khanda': {'label': 'Khanda', 'symbol': '\u262c', 'font': 'Noto Symbols'},
    'cross': {'label': 'Christian cross', 'symbol': '\u271d', 'font': 'Noto Symbols'},
    'dhamma-wheel': {'label': 'Wheel of Dharma', 'symbol': '\u2638', 'font': 'Noto Symbols'},
}

COLLECTION = []
for base in BASE_COLLECTION:
    versions = [dict(id=base['id'], name=base['name'], hi=base['hi'], sacred_art=base['default_sacred_art'])]
    versions.extend(v for v in VARIANTS if v['base'] == base['id'])
    for version in versions:
        design = deepcopy(base)
        design.update(id=version['id'], name=version['name'], hi=version['hi'],
                      slug=version['id'].removeprefix('craft-'), css_slug=base['slug'], spec_slug=base['slug'],
                      base_template_id=base['id'], variant_sacred_art=version['sacred_art'],
                      variant_salutation=version.get('salutation', False), supports_rtl=False,
                      default_sacred_art=version['sacred_art'], supported_sacred_art=[version['sacred_art']])
        COLLECTION.append(design)
BY_ID = {item['id']: item for item in COLLECTION}


def migrate_template_choice(template_id, presentation):
    """Preserve old customized drafts by choosing the equivalent standalone card."""
    design = BY_ID.get(template_id)
    if not design or design['base_template_id'] != template_id:
        return template_id
    base = next(item for item in BASE_COLLECTION if item['id'] == template_id)
    choice = presentation.get('sacred_art', 'default')
    if choice not in base['supported_sacred_art']:
        choice = base['default_sacred_art']
    salutation = bool(presentation.get('salutation')) and template_id == 'craft-ambedkarite-blue'
    return next(item['id'] for item in COLLECTION if item['base_template_id'] == template_id
                and item['variant_sacred_art'] == choice and item['variant_salutation'] == salutation)


def resolve_presentation(design, presentation):
    """The selected card owns its artwork; all documents use left-to-right layout."""
    choice = design['variant_sacred_art']
    return {**SACRED_ART[choice], 'id': choice,
            'direction': 'ltr', 'salutation': design['variant_salutation']}
