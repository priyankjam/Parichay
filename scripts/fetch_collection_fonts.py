"""Vendor current OFL Noto families from Google's font repository; keep provenance."""
import json
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import quote
families=['notosansgujarati','notosansgurmukhi','notosansbengali','notosanstamil','notosanstelugu','notosanskannada','notosansmalayalam','notonaskharabic','notosanssymbols2','notosanssymbols']
root=Path('app/static/fonts'); manifest={}
for family in families:
    api=f'https://api.github.com/repos/google/fonts/contents/ofl/{family}'
    files=json.load(urlopen(Request(api,headers={'User-Agent':'Parichay font vendor'}),timeout=40))
    for item in files:
        if item['name'].endswith('.ttf') or item['name']=='OFL.txt':
            target=root/(('OFL-'+family+'.txt') if item['name']=='OFL.txt' else item['name'])
            if not target.exists(): target.write_bytes(urlopen(item['download_url'],timeout=40).read())
            if item['name'].endswith('.ttf'): manifest[family]={'file':item['name'],'source':item['download_url'],'sha':item['sha']}
    print(family,flush=True)
Path('docs/template-collection/font-provenance.json').write_text(json.dumps(manifest,indent=2))
