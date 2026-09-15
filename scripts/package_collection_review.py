"""Build a local, self-contained collection review using actual export proofs."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/template-collection'
designs = json.loads((ROOT / 'app/biodata_templates/collection.json').read_text())
groups = [('contemporary', 'Contemporary', 'Quiet, confident documents with distinct editorial structures.'),
          ('regional', 'Regional', 'Original interpretations of Indian textile, architectural and botanical craft.'),
          ('cultural', 'Traditional & cultural', 'An expression you choose. Cultural artwork can be removed or personalized.')]


def group_key(design):
    return 'contemporary' if design['number'] <= 6 else 'regional' if design['number'] <= 11 else 'cultural'


sections = []
for key, title, description in groups:
    cards = []
    for design in [d for d in designs if group_key(d) == key]:
        name, slug = html.escape(design['name']), design['slug']
        folder = f'batch-{design["batch"]}'
        links = [('medium', 'PDF proof'), ('short', 'Short profile'), ('long', 'Long profile'),
                 ('no-photo', 'Without a photo'), ('missing', 'Hidden sections'),
                 ('multilingual', 'Multilingual'), ('rtl', 'Urdu / RTL')]
        proofs = ''.join(f'<a href="{folder}/{slug}-{case}.pdf" target="_blank" rel="noopener">{label} ↗</a>' for case, label in links)
        cards.append(f'''<article class="design">
          <a class="paper" href="{folder}/{slug}-medium.pdf" target="_blank" rel="noopener" aria-label="Open {name} PDF proof">
            <img src="{folder}/{slug}.png" alt="{name}, complete fictional biodata for Aarav Mehta" width="714" height="1010" loading="lazy" decoding="async">
          </a>
          <div class="card-copy"><span class="number">{design['number']:02d}</span><h3>{name}</h3>
            <p>{html.escape(design['photo_mode'].replace('-', ' ').capitalize())} portrait · {html.escape(design['layout_id'].replace('-', ' '))} layout</p>
            <details><summary>Review proofs & states</summary><div class="proofs">{proofs}
              <a href="{folder}/{slug}-grayscale.png" target="_blank" rel="noopener">Grayscale proof ↗</a>
              <a href="browser/{slug}-mobile.png" target="_blank" rel="noopener">Mobile preview ↗</a>
            </div></details>
          </div></article>''')
    sections.append(f'<section data-group="{key}"><div class="section-title"><h2>{title}</h2><p>{description}</p></div><div class="grid">{"".join(cards)}</div></section>')

page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Parichay · The new collection</title>
<style>
:root{color-scheme:light;--paper:#f6f1e7;--ink:#292624;--wine:#612b43;--muted:#685e57;--line:#d7cdbf}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:100px}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.6 system-ui,sans-serif}a{color:var(--wine);text-decoration-thickness:1px;text-underline-offset:4px}a:hover{color:#8b3e5f}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid var(--wine);outline-offset:4px}header{max-width:1440px;margin:auto;padding:35px 40px 50px}.masthead{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:68px}.brand{font:700 32px Georgia,serif;color:var(--wine)}.eyebrow{text-transform:uppercase;letter-spacing:.16em;font-size:11px;color:var(--wine)}h1{font:400 clamp(42px,5vw,74px)/1.1 Georgia,serif;letter-spacing:-.035em;max-width:840px;margin:20px 0}header p{max-width:660px;color:var(--muted);font-size:17px}nav{position:sticky;top:0;z-index:5;background:#f6f1e7f5;border-block:1px solid var(--line);padding:15px max(24px,calc((100vw - 1360px)/2));display:flex;gap:10px;overflow-x:auto}button{font:inherit;white-space:nowrap;border:1px solid var(--line);border-radius:30px;padding:10px 19px;background:transparent;color:var(--muted);cursor:pointer}button[aria-pressed=true]{background:var(--wine);border-color:var(--wine);color:#fff9ef}main{max-width:1440px;padding:0 40px 60px;margin:auto}section{padding-top:45px}.section-title{margin-bottom:25px}.section-title h2{font:400 34px/1.2 Georgia,serif;margin:0 0 8px}.section-title p{color:var(--muted);margin:0}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:34px 24px}.design{min-width:0}.paper{display:block;background:#fbf7ef;box-shadow:0 9px 25px #493d3012,0 2px 5px #493d3010;outline:1px solid #493d3012;transition:transform .2s}.paper:hover{transform:translateY(-4px)}.paper img{display:block;width:100%;height:auto;aspect-ratio:210/297}.card-copy{position:relative;padding-top:20px}.number{font-size:11px;color:var(--muted);float:right;margin-top:4px}h3{font-size:16px;line-height:1.4;margin:0 28px 5px 0}.card-copy p{color:var(--muted);font-size:12px;margin:0 0 13px}.card-copy summary{font-size:12px;cursor:pointer;color:var(--wine);min-height:34px}.proofs{display:flex;flex-wrap:wrap;gap:11px 15px;margin:4px 0 20px}.proofs a{font-size:12px}.notes{border-top:1px solid var(--line);margin-top:65px;padding-top:30px;max-width:850px}.notes h2{font:400 28px Georgia,serif}.notes p{color:var(--muted)}footer{max-width:1440px;margin:auto;padding:20px 40px 40px;color:var(--muted);font-size:12px}[hidden]{display:none!important}@media(max-width:1050px){.grid{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(max-width:760px){header{padding:24px 24px 35px}.masthead{margin-bottom:45px}.masthead a{font-size:13px}main{padding:0 24px 35px}.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:30px 18px}h3{font-size:14px}.section-title h2{font-size:29px}.number{display:none}}@media(max-width:460px){.grid{grid-template-columns:1fr;gap:35px}.paper{max-width:380px;margin:auto}.card-copy p{font-size:13px}h3{font-size:18px}.proofs a,.card-copy summary{font-size:14px}.masthead{align-items:baseline}header p{font-size:15px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.paper{transition:none}.paper:hover{transform:none}}
</style>
<header><div class="masthead"><div class="brand">parichay</div><a href="http://127.0.0.1:5050/create#section-9">Open the editor ↗</a></div>
<span class="eyebrow">The document collection · 20 new designs</span><h1>A thoughtful introduction.<br>A design that feels like you.</h1>
<p>Contemporary, regional and cultural biodatas, built around real information. Browse the finished designs, open an A4 proof, and compare how each handles a little—or a lot—to say.</p></header>
<nav aria-label="Filter the collection"><button data-filter="all" aria-pressed="true">All 20</button><button data-filter="contemporary" aria-pressed="false">Contemporary · 6</button><button data-filter="regional" aria-pressed="false">Regional · 5</button><button data-filter="cultural" aria-pressed="false">Traditional & cultural · 9</button></nav>
<main>''' + ''.join(sections) + '''<aside class="notes"><h2>About these proofs</h2><p>Every image comes from the same renderer used for live preview and export. The fictional medium profile is identical across designs; the short, long, missing-section and language variants test the same document system. Page two uses a quieter continuation layout.</p><p>Cultural identity remains your choice. Sikh and Christian symbols are off by default; devotional templates expose their compatible artwork plus a “None” option. Choosing “None” stays respected as you explore.</p><p>Reviewed in color and grayscale at A4, across nine screen sizes, with keyboard, emulated touch and reduced motion. Physical printer and community-member reviews have not been performed.</p><p><a href="review-notes.md">Read the validation notes ↗</a> · <a href="mobile-overview.jpg">All mobile previews ↗</a></p></aside></main>
<footer>Parichay · Original artwork, reusable layouts, editable text. Fictional sample information only.</footer>
<script>document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));document.querySelectorAll('[data-group]').forEach(section=>section.hidden=button.dataset.filter!=='all'&&section.dataset.group!==button.dataset.filter)}));</script></html>'''
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'index.html').write_text(page)
notes = ROOT / 'docs/template-collection/qa-report.md'
if notes.exists():
    (OUT / 'review-notes.md').write_text(notes.read_text())
print(OUT / 'index.html')
