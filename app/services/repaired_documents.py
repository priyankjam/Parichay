"""A4 compositions from the 49-template audit; profile values stay in the domain model."""
from copy import deepcopy
from pathlib import Path
from flask import current_app, render_template
from app.services.collection import SCRIPT_FONTS, file_uri, art_uri
from app.models.collection import BY_ID, resolve_presentation
import re, base64

from app.models.repair import REGISTRY

def uri(path):
    mime = 'image/svg+xml' if path.suffix == '.svg' else 'image/jpeg' if path.suffix == '.jpg' else 'image/webp'
    return f'data:{mime};base64,'+base64.b64encode(path.read_bytes()).decode()


def build_repaired_html(document):
    doc=deepcopy(document); design=deepcopy(REGISTRY[doc['template']]); n=design['number']
    if n==48 and doc.get('print_treatment')=='light':
        design.update(paper='#fffcf0',ink='#421927',accent='#76512a',label='#655d54')
    root=Path(current_app.static_folder)
    sacred=resolve_presentation(BY_ID[doc['template']],{}) if doc['template'] in BY_ID else {'id':'none','salutation':False}
    if n>=46:sacred={'id':'ganesha','asset':'ganesha','label':'Ganesha','salutation':False}
    if sacred.get('asset'):sacred['src']=art_uri(sacred['asset'])
    if n>=46:
        emblem='ganesha-line-light' if n>=48 and doc.get('print_treatment')!='light' else 'ganesha-line'
        sacred['src']=uri(root/'artwork/repair-v1'/f'{emblem}.svg')
    # Preserve the supplied invocation verbatim, pending independent language review.
    sacred['invocation']='श्री गणेशाय नमः' if n>=46 else ''
    order=design['order']
    key=lambda s:'custom' if s['key'].startswith('custom-') else s['key']
    sections=sorted(doc['sections'],key=lambda s:order.index(key(s)) if key(s) in order else len(order))
    rows={s['key']:[r for g in s['groups'] for r in g] for s in sections}
    def value(s,k):return next((r['value'] for r in rows.get(s,[]) if r.get('key')==k),'')
    doc['subtitle']=' · '.join(filter(None,[value('career','role'),value('personal','city')]))
    row_index=0
    for section in sections:
        section['number']=sections.index(section)+1
        for group in section['groups']:
            for row in group:
                row['render_id']=str(row_index);row_index+=1
                # Display labels, never entered values, lose form-only instructions.
                if row.get('key')=='income':row['label']='आय' if doc['language']=='hi' else 'Income'
                if row.get('prose'):row['stack']=True
    doc['lead']=[]
    if design['layout']=='essay':
        doc['lead']=[s for s in sections if s['key']=='about'];sections=[s for s in sections if s['key']!='about']
    doc['lanes']=[[s for s in sections if key(s) in design['facts']],[s for s in sections if key(s) not in design['facts']]] if design['layout'] in ['split','essay'] else [sections]
    # Empty sidebar disappears; no-photo removes the portrait reservation as well.
    doc['lanes']=[lane for lane in doc['lanes'] if lane]
    doc['continued']='जारी' if doc['language']=='hi' else 'continued'
    doc['page_word']='पृष्ठ' if doc['language']=='hi' else 'Page'
    art_map={3:'sage-branch',6:'ink-leaf',8:'alpana-ornament',10:'paithani-peacock',11:'miniature-pavilion',13:'braj-lotus',24:'ahimsa-geometry',25:'dhamma-lotus'}
    art=art_uri(art_map[n]) if n in art_map else None
    vectors={4:'arch',5:'deco',7:'kolam',9:'patola',18:'phulkari',19:'phulkari',20:'phulkari',21:'emerald',22:'lancet',36:'peach',37:'lavender',38:'blue',39:'amber',41:'blue-frame',42:'wreath',43:'garden',44:'blossom',45:'blossom-soft',46:'gold-frame',47:'rose',48:'maroon-frame',49:'festive'}
    if n in vectors:art=uri(root/'artwork/repair-v1'/f'{vectors[n]}.svg')
    text=str(doc)+str(sacred)
    fonts=[('Parichay Serif','DMSerifDisplay.ttf'),('Parichay Sans','DMSans.ttf')];fallback=[]
    if n==45:fonts.append(('Parichay Text','TiroDevanagariSanskrit-Regular.ttf'))
    for family,pattern,chars in SCRIPT_FONTS:
        if re.search('['+chars+']',text):
            fonts.append((family,next((root/'fonts').glob(pattern)).name));fallback.append('"'+family+'"')
    css=(root/'css/repaired-document.css').read_text()
    for family,filename in fonts:
        css+=f'\n@font-face{{font-family:"{family}";src:url("{file_uri(str(root/"fonts"/filename))}");font-weight:100 900}}'
    fs=','.join(fallback+['sans-serif']);display='Parichay Serif' if design['serif'] else 'Parichay Sans'
    css+=f'\n.repaired-document{{--font-body:"Parichay Sans",{fs};--font-display:"{display}",{fs};--paper:{design["paper"]};--accent:{design["accent"]};--ink:{design["ink"]};--label:{design["label"]};--body-size:{design["body_size"]}pt;--section-size:{design["heading_size"]}pt;--name-size:{design["name_size"]}pt;--photo-width:{design["portrait"][0]}mm;--photo-height:{design["portrait"][1]}mm;--lane:{design["lane"]}mm;--label-width:{design["label_width"]}mm;--left:{design.get("left",18)}mm;--right:{design.get("right",18)}mm;}}'
    return render_template('repaired-document.html',doc=doc,design=design,sacred=sacred,art=art,css=css)
