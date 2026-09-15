"""Optional asset build: pip install fonttools brotli; python scripts/compress_fonts.py."""
from pathlib import Path
from fontTools.ttLib import TTFont
root=Path(__file__).resolve().parents[1]/'app/static/fonts'
for source in root.glob('*.ttf'):
    font=TTFont(source);font.flavor='woff2';font.save(source.with_suffix('.woff2'))
    print(source.name,'→',source.with_suffix('.woff2').stat().st_size,'bytes')
