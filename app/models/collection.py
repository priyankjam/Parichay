"""Curated metadata only: identity never participates in template selection."""
import json
from pathlib import Path

COLLECTION = json.loads((Path(__file__).resolve().parents[1] / 'biodata_templates/collection.json').read_text())
LAYOUTS = json.loads((Path(__file__).resolve().parents[1] / 'biodata_templates/layouts.json').read_text())
ARTWORK_PACKS = json.loads((Path(__file__).resolve().parents[1] / 'biodata_templates/artwork-packs.json').read_text())
BY_ID = {item['id']: item for item in COLLECTION}
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

def resolve_presentation(design, presentation):
    """A choice on one template cannot leak incompatible iconography into another."""
    choice = presentation.get('sacred_art', 'default')
    if choice == 'default' or choice not in design['supported_sacred_art']:
        choice = design['default_sacred_art']
    return {**SACRED_ART[choice], 'id': choice,
            'direction': presentation.get('direction', 'auto'),
            'salutation': bool(presentation.get('salutation')) and design['id'] == 'craft-ambedkarite-blue'}
