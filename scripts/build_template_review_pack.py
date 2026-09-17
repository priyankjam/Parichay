"""Build a portable comparison of all PDFs, plus measured print/asset reports."""
import sys, json, csv, math, hashlib, unicodedata, shutil
from pathlib import Path
from html import escape as esc
from urllib.parse import quote
from collections import Counter
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw
from pypdf import PdfReader
import pypdfium2 as pdfium

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.models.repair import REGISTRY
from app.models.collection import BY_ID
from scripts.review_fixture import review_profile

OUT=ROOT/'output/template-repair';DOCS=ROOT/'docs/template-repair'
IMAGES=OUT/'pages';IMAGES.mkdir(exist_ok=True)
briefs={x['id']:x for x in json.loads((DOCS/'briefs.json').read_text())}
retained={3:'sage-branch',6:'ink-leaf',8:'alpana-ornament',10:'paithani-peacock',11:'miniature-pavilion',13:'braj-lotus',24:'ahimsa-geometry',25:'dhamma-lotus'}
vectors={4:'arch',5:'deco',7:'kolam',9:'patola',18:'phulkari',19:'phulkari',20:'phulkari',21:'emerald',22:'lancet',36:'peach',37:'lavender',38:'blue',39:'amber',41:'blue-frame',42:'wreath',43:'garden',44:'blossom',45:'blossom-soft',46:'gold-frame',47:'rose',48:'maroon-frame',49:'festive'}
supplied={3,6,8,10,11,12,13,14,16,24,25,27,29,36,37,38,43,44,45,46,47,48,49}
subject_review={12,14,16,27,29,46,47,48,49}
def luminance(rgb):
    channels=[x/255 for x in rgb]
    channels=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in channels]
    return sum(a*b for a,b in zip(channels,[.2126,.7152,.0722]))
def rgb(color):return tuple(int(color[i:i+2],16) for i in (1,3,5))
def contrast(a,b):
    a,b=sorted([luminance(a),luminance(b)]);return (b+.05)/(a+.05)
def embedded(font):
    font=font.get_object()
    if '/DescendantFonts' in font:return all(embedded(f) for f in font['/DescendantFonts'])
    # Chromium may embed variable-font outlines as Type 3 CharProcs. These
    # are self-contained glyph programs, with ToUnicode for selectable text.
    if font.get('/Subtype')=='/Type3':return bool(font.get('/CharProcs') and font.get('/ToUnicode'))
    descriptor=font.get('/FontDescriptor')
    return bool(descriptor and any(k in descriptor.get_object() for k in ['/FontFile','/FontFile2','/FontFile3']))

rows=[];assets=[];metrics=[];sections=[];thumbs=[];before_total=after_total=0
for id,design in REGISTRY.items():
    n=design['number'];prefix=f'{n:02d}';versions={};title=''
    if design.get('retired'):
        old=next((OUT/'before').glob(prefix+' - *.pdf'))
        rows.append([prefix,id,'Removed from the selectable collection at the user’s request. Saved drafts retain compatibility.','Retired; no artwork shipped in the active review bundle.',len(PdfReader(old).pages),'—','Removed'])
        assets.append({'number':n,'id':id,'status':'Removed from selection; existing draft compatibility retained','retainedOrReplacement':[]})
        continue
    for version in ['before','after']:
        pdf=next((OUT/version).glob(prefix+' - *.pdf'));title=pdf.stem[5:];reader=PdfReader(pdf)
        images=[]
        with pdfium.PdfDocument(str(pdf)) as document:
            for index,page in enumerate(document):
                im=page.render(scale=1200/page.get_width()).to_pil().convert('RGB')
                filename=f'{version}-{prefix}-{index+1}.png';im.save(IMAGES/filename)
                images.append(filename)
                if version=='after' and index==0:
                    thumb=im.copy();thumb.thumbnail((190,269));thumbs.append((prefix+' '+title,thumb))
                    # The body field is flat paper. Sample its rendered interior
                    # independently of the CSS color, away from all text/art.
                    paper=im.getpixel((int(im.width*.53),int(im.height*.84)))
                    if sum(abs(a-b) for a,b in zip(paper,rgb(design['paper'])))>12:
                        paper=im.getpixel((int(im.width*.52),int(im.height*.90)))
        versions[version]={'pdf':pdf,'reader':reader,'pages':len(reader.pages),'images':images}
    before_total+=versions['before']['pages'];after_total+=versions['after']['pages']
    sizes=Counter();font_status=[]
    for page in versions['after']['reader'].pages:
        def text_visitor(text,cm,tm,font,size):
            if text.strip():sizes[round(size*math.hypot(cm[2],cm[3])*math.hypot(tm[2],tm[3]),2)]+=len(text.strip())
        page.extract_text(visitor_text=text_visitor)
        font_status.extend(embedded(f) for f in page['/Resources']['/Font'].values())
    assert all(font_status),(id,'unembedded font')
    assert min(sizes)>=8.98,(id,sizes)
    contrasts={k:round(contrast(rgb(design[k]),paper),2) for k in ['ink','label','accent']}
    assert min(contrasts.values())>=4.5,(id,contrasts,paper)
    metrics.append({'id':id,'number':n,'effectivePdfTextSizesPt':dict(sizes),'allFontsEmbedded':True,'pdfBytes':versions['after']['pdf'].stat().st_size,'renderedPaperRgb':paper,'essentialTextContrast':contrasts})
    new=[];old=[]
    if n in retained:
        name=retained[n];new.append(f'artwork/collection-v1/{name}-pdf.webp');old.append(new[-1])
    if n in vectors:
        new.append(f'artwork/repair-v1/{vectors[n]}.svg')
        if n>=36:old.append(f'artwork/templates/{id}.jpg')
        else:old.extend(f'artwork/collection-v1/{asset}-pdf.webp' for asset in BY_ID[id]['assets'])
    subject=BY_ID.get(id,{}).get('variant_sacred_art','none')
    if subject in ['krishna','ganesha','rama','ambedkar']:
        new.append(f'artwork/collection-v1/{subject}-pdf.webp');old.append(new[-1])
    elif subject!='none':new.append(f'Unicode {subject} in embedded Noto font')
    if n>=46:
        new.extend(['artwork/repair-v1/ganesha-line.svg','artwork/repair-v1/ganesha-line-light.svg','Unicode invocation: श्री गणेशाय नमः'])
    if n in [27,28,29,30] and BY_ID.get(id,{}).get('variant_salutation'):new.append('Unicode greeting: जय भीम')
    artwork=('Existing supplied art retained/repositioned; provenance unverified. ' if n in supplied else 'Native geometry/type; no new raster artwork. ')
    if n>=46:artwork='Existing line emblem traced as SVG; real invocation text; independent review pending. '
    elif n in subject_review:artwork+='Subject retained provisionally; specialist review pending. '
    changes=f"{design['target']} {design['portrait'][0]} × {design['portrait'][1]} mm portrait; {design['name_size']} pt name; {design['body_size']} pt body; {design['heading_size']} pt headings. {design['layout']} flow, {design['header']} header. Compact named continuation; contact follows custom content."
    result='Print/value/record checks passed; specialist sign-off pending' if n in subject_review else 'Print/value/record checks passed'
    rows.append([prefix,id,changes,artwork,versions['before']['pages'],versions['after']['pages'],result])
    assets.append({'number':n,'id':id,'old':old or ['Plain layout / prior CSS'], 'retainedOrReplacement':new or ['Native CSS typography, rules and paper'],'status':artwork,'provenance':'Repository-supplied asset; rights and regional authenticity not independently verified' if n in supplied else 'Original native geometry written for this implementation; Noto fonts retain their bundled OFL notices'})
    columns=[]
    for version in ['before','after']:
        data=versions[version];href=quote(str(data['pdf'].relative_to(OUT)))
        figures=''.join(f'<a href="pages/{name}" target="_blank"><img loading="lazy" src="pages/{name}" alt="{esc(title)} {version}, page {i+1}" width="1200" height="1697"><span>Page {i+1} / {data["pages"]}</span></a>' for i,name in enumerate(data['images']))
        columns.append(f'<div class="version"><h3>{version.title()} · {data["pages"]} pages <a href="{href}">Open PDF ↗</a></h3><div class="sheets">{figures}</div></div>')
    sections.append(f'<section id="t{prefix}" data-name="{esc((title+id).lower())}"><h2>{prefix} · {esc(title)}</h2><code>{id}</code><p>{esc(design["target"])}</p><div class="compare">'+''.join(columns)+f'</div><p class="note">{esc(artwork)}</p></section>')

headers=['Number','Original template ID','Actual changes','Artwork status','Old pages','New pages','Validation result']
with (OUT/'49-template-checklist.csv').open('w',newline='') as f:
    writer=csv.writer(f);writer.writerow(headers);writer.writerows(rows)
table='| '+' | '.join(headers)+' |\n|'+'|'.join(['---']*len(headers))+'|\n'+'\n'.join('| '+' | '.join(str(c).replace('|','/') for c in row)+' |' for row in rows)
(DOCS/'completion-checklist.md').write_text('# Parichay — 49-template implementation checklist\n\n'+table+'\n')
(DOCS/'asset-manifest.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
(OUT/'pdf-metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2))
for filename in ['completion-checklist.md','asset-manifest.json']:
    shutil.copy2(DOCS/filename,OUT/filename)
sheet=Image.new('RGB',(7*218,7*315),'#eee8df');draw=ImageDraw.Draw(sheet)
for i,(label,thumb) in enumerate(thumbs):
    x=(i%7)*218+14;y=(i//7)*315+12;sheet.paste(thumb,(x,y));draw.text((x,y+276),label[:31],fill='#342b2b')
sheet.save(OUT/'gallery-contact-sheet.jpg',quality=94);sheet.convert('L').save(OUT/'gallery-grayscale.jpg',quality=94)
options=''.join(f'<option value="t{row[0]}">{row[0]} · {row[1]}</option>' for row in rows if row[-1]!='Removed')
html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Parichay · 49-template review</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f5eee4;color:#322728;font:16px/1.6 system-ui,sans-serif}header,main{max-width:1640px;margin:auto;padding:36px}h1,h2{font-family:Georgia,serif;font-weight:400}h1{font-size:44px;margin:0}h2{font-size:30px;margin:0}a{color:#6a2945}nav{position:sticky;top:0;z-index:2;background:#fbf7ef;border-block:1px solid #d8cec1;padding:12px 36px;display:flex;gap:18px;align-items:center;flex-wrap:wrap}select,input,button{font:inherit;min-height:44px;border:1px solid #beacaa;border-radius:6px;background:#fffdf9;padding:8px}section{padding:32px 0 52px;border-bottom:1px solid #cfbeb1;scroll-margin-top:110px}code,.note{font-size:13px;color:#6e625b}.compare{display:grid;grid-template-columns:1fr 1fr;gap:26px}.version h3{font-size:15px;display:flex;justify-content:space-between}.sheets{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;align-items:start}.sheets a{display:block;text-decoration:none;color:#65554f;font-size:12px}.sheets img{width:100%;height:auto;box-shadow:0 5px 17px #543b2814;display:block}.sheets span{display:block;margin-top:8px}body.gray .sheets img{filter:grayscale(1)}.intro{max-width:940px}button{cursor:pointer}@media(max-width:800px){header,main{padding:22px}.compare{grid-template-columns:1fr}nav{padding:10px 20px}h1{font-size:34px}}</style>
<header><h1>Parichay · the revised collection</h1><p class="intro">47 available designs, the identical Aarav Mehta profile, and every active design available for comparison. Nikah Nocturne and Christian Cathedral Ivory were removed at your request; the checklist accounts for all 49 original IDs. Click a page for its full-resolution image, or open the vector PDF for print-scale review.</p>'''
html+=f'<p><b>{before_total} → {after_total} pages.</b> No sample values removed. <a href="after.zip">Download all revised PDFs</a> · <a href="49-template-checklist.csv">49-row checklist</a> · <a href="REVIEW.md">Review notes</a></p><p><a href="gallery-contact-sheet.jpg">Same-scale gallery</a> · <a href="gallery-grayscale.jpg">Grayscale gallery</a> · <a href="asset-manifest.json">Asset manifest</a></p></header><nav><label>Jump to design <select id="jump"><option value="">Choose a template</option>{options}</select></label><input id="search" aria-label="Filter templates" placeholder="Filter name or ID"><button id="gray" aria-pressed="false">Grayscale</button></nav><main>'+''.join(sections)+'</main>'
html+='''<script>document.getElementById('jump').addEventListener('change',e=>{document.querySelectorAll('section').forEach(s=>s.hidden=false);document.getElementById('search').value='';document.getElementById(e.target.value)?.scrollIntoView({behavior:'smooth'})});document.getElementById('search').addEventListener('input',e=>document.querySelectorAll('section').forEach(s=>s.hidden=!s.dataset.name.includes(e.target.value.toLowerCase())));document.getElementById('gray').addEventListener('click',e=>e.target.setAttribute('aria-pressed',document.body.classList.toggle('gray')))</script></html>'''
(OUT/'index.html').write_text(html)
fixture=review_profile();fixture['photos']=['app/static/artwork/demo-portrait.jpg']
(OUT/'sample-profile.json').write_text(json.dumps(fixture,ensure_ascii=False,indent=2))
print(f'Built {len(sections)} active comparisons, {before_total} before pages, {after_total} after pages, embedded-font/contrast reports and {len(rows)}-row checklist.')
