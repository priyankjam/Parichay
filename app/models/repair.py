"""Trusted composition metadata; IDs remain compatible with existing drafts."""
import json
from pathlib import Path
REGISTRY = json.loads((Path(__file__).resolve().parents[1] / 'biodata_templates/repair.json').read_text())
