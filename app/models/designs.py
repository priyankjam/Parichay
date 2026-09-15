"""Trusted template presentation metadata; never read styles from a profile payload."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGMA_DESIGNS = json.loads((ROOT / 'biodata_templates/figma.json').read_text())
FONT_FILES = {
    'Inria Sans': [('InriaSans-Regular.ttf', '400', 'normal'), ('InriaSans-Bold.ttf', '700', 'normal')],
    'Figtree': [('Figtree[wght].ttf', '300 900', 'normal')],
    'Poppins': [('Poppins-Medium.ttf', '500', 'normal'), ('Poppins-SemiBold.ttf', '600', 'normal'), ('Poppins-Bold.ttf', '700', 'normal')],
    'Tiro Sanskrit': [('TiroDevanagariSanskrit-Regular.ttf', '400', 'normal')],
    'Merriweather': [('Merriweather-Italic[opsz,wdth,wght].ttf', '300 900', 'italic')],
}

def find_design(template):
    return next((d for d in FIGMA_DESIGNS if d['id'] == template), None)


def design_css(d):
    scale = 680 / 595
    padding = ' '.join(f'{n * scale:.3f}px' for n in d['padding'])
    # Source art may be taller than A4; preserve its relative safe areas at A4 size.
    # Some source artwork was composed around a short, centered first-page title.
    # Continuous text on later pages needs a clear rectangle on every sheet.
    top, right, bottom, left = d.get('printSafePadding', d['padding'])
    height = d.get('height', 842)
    print_padding = f'{top / height * 297:.3f}mm {right / 595 * 210:.3f}mm {bottom / height * 297:.3f}mm {left / 595 * 210:.3f}mm'
    family = d.get('nameFont', d['body'])
    return f'''\n.theme-{d['id']},.export-document[data-theme="{d['id']}"]{{
 --doc-accent:{d['color']};--doc-ink:{d['ink']};--doc-paper:{d['paper']};--page-paper:{d['paper']};
 --design-bg:url("{d['background']}");--design-padding:{padding};--design-print-padding:{print_padding};
 --design-body:"{d['body']}";--design-heading:"{d['heading']}";--design-name:"{family}";
 --design-align:{'center' if d.get('center') else 'left'};--design-name-style:{'italic' if d.get('italic') else 'normal'};
}}\n'''


def write_browser_styles():
    css = []
    for family, fonts in FONT_FILES.items():
        for filename, weight, style in fonts:
            css.append(f'@font-face{{font-family:"{family}";src:url("../fonts/{Path(filename).stem}.woff2") format("woff2");font-weight:{weight};font-style:{style};font-display:swap}}')
    css.extend(design_css(d) for d in FIGMA_DESIGNS)
    (ROOT / 'static/css/figma-designs.css').write_text('\n'.join(css))
