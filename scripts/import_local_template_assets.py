"""Import reviewed, photo-free backgrounds; reference biodata never becomes artwork.

Run after build_figma_backgrounds.py to apply the user's higher-quality source files.
Only format conversion/compression is performed; originals remain untouched.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'biodata template'
FILES = {
    'figma-peach-floral': 'Boi data templates/Basic/Basic flower 4/Basic - Flower - 4-1.png',
    'figma-lavender-floral': 'Boi data templates/Basic/Basic flower 3/Basic - Flower - 3-1.png',
    'figma-blue-botanical': 'Boi data templates/Basic/Basic flower 6/Basic - Flower - 6-1.png',
    'figma-amber-botanical': 'Boi data templates/Basic/Basic flower 6/Basic - Flower - 6-1.png',
    'figma-floral-wreath': 'Boi data templates/Basic/Basic 1/Basic Template - Flower -  1-1.png',
    'figma-garden-corners': 'Boi data templates/Basic/Basic 2/Basic Template - Flower -  2-1.png',
    'figma-ganesha-ivory': 'Boi data templates/Hindu tradition/Hindu traditional 2/Hindu Traditional 2-1.png',
    'figma-ganesha-rose': 'Boi data templates/Hindu tradition/Hindu Traditional 3/Hindu Traditional 3-1.png',
}


def main():
    destination = ROOT / 'app/static/artwork/templates'
    records = []
    sources = [(key, SOURCE / value) for key, value in FILES.items()]
    sources.append(('figma-ganesha-festive', ROOT / 'app/static/artwork/sources/festive-frame-free.png'))
    for template, path in sources:
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source).convert('RGB')
            image.thumbnail((1400, 2000))
            image.save(destination / f'{template}.webp', 'WEBP', quality=92, method=6)
            image.save(destination / f'{template}.jpg', 'JPEG', quality=92, optimize=True)
        records.append({'template': template, 'source': str(path.relative_to(ROOT)),
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    portrait = ROOT / 'app/static/artwork/demo-portrait.jpg'
    with Image.open(SOURCE / 'Reference/Dummy photo.png') as source:
        image = ImageOps.exif_transpose(source).convert('RGB')
        image.thumbnail((552, 736))
        image.save(portrait, 'JPEG', quality=90, optimize=True)
    (ROOT / 'app/static/artwork/local-provenance.json').write_text(json.dumps(records, indent=2))
    print(f'Imported {len(records)} backgrounds and the supplied demo portrait.')


if __name__ == '__main__':
    main()
