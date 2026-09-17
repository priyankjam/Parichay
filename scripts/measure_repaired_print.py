"""Check physical layout after fonts load, including whole sample records."""
import sys, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
from app import create_app
from app.models.profile import Profile
from app.models.repair import REGISTRY
from app.services.rendering import build_document_html
from scripts.review_fixture import review_profile
from playwright.sync_api import sync_playwright

app=create_app({'TESTING':True});results=[]
with app.app_context(),sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=app.config['CHROMIUM_EXECUTABLE'],chromium_sandbox=True)
    page=browser.new_page();page.emulate_media(media='print')
    for id,design in REGISTRY.items():
        raw=review_profile();raw['template']=id
        page.set_content(build_document_html(Profile.parse(raw).document()),wait_until='load');page.evaluate('document.fonts.ready')
        expected=page.locator('.r-source .r-row').count()
        pagination=page.evaluate((ROOT/'app/static/js/repaired-paginator.js').read_text())
        metrics=page.evaluate('''() => {
          const mm=96/25.4, pages=[...document.querySelectorAll('.r-page')];
          const box=e=>{const r=e.getBoundingClientRect();return {x:r.x/mm,y:r.y/mm,width:r.width/mm,height:r.height/mm}};
          const portrait=box(document.querySelector('.r-portrait'));
          const records={}; pages.forEach((p,i)=>p.querySelectorAll('[data-section="education"] .r-group,[data-section="career"] .r-group,[data-section="family"] .r-group').forEach(g=>(records[g.dataset.record] ||= []).push(i+1)));
          const overlap=(a,b)=>Math.min(a.right,b.right)-Math.max(a.left,b.left)>.5 && Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>.5;
          const intersections=[];
          pages.forEach((p,i)=>p.querySelectorAll('.r-sacred').forEach(s=>p.querySelectorAll('.r-row,.r-heading h1,.r-subtitle').forEach(t=>{if(overlap(s.getBoundingClientRect(),t.getBoundingClientRect()))intersections.push(i+1)})));
          return {portrait,records,intersections,rows:document.querySelectorAll('.r-page .r-row').length,pages:pages.map(p=>{
            const body=p.querySelector('.r-body').getBoundingClientRect(),rows=[...p.querySelectorAll('.r-row')];
            return {bodyHeightMm:body.height/mm,usedHeightMm:rows.length?(Math.max(...rows.map(r=>r.getBoundingClientRect().bottom))-body.top)/mm:0,bodySizePt:parseFloat(getComputedStyle(p.querySelector('.r-value')).fontSize)*.75,labelSizePt:parseFloat(getComputedStyle(p.querySelector('.r-label')).fontSize)*.75};
          })};
        }''')
        assert metrics['rows']==expected,(id,metrics['rows'],expected)
        assert all(len(pages)==1 for pages in metrics['records'].values()),(id,metrics['records'])
        assert not metrics['intersections'],(id,metrics['intersections'])
        assert abs(metrics['portrait']['width']-design['portrait'][0])<.1
        assert abs(metrics['portrait']['height']-design['portrait'][1])<.1
        assert all(p['bodySizePt']>=10.99 and p['labelSizePt']>=9.49 for p in metrics['pages'])
        results.append({'id':id,'number':design['number'],'status':'passed','pageCount':pagination['pages'],**metrics})
    browser.close()
(ROOT/'output/template-repair/print-geometry.json').write_text(json.dumps(results,indent=2))
print('49 layouts: physical portrait/type sizes, complete records and sacred-figure clearance passed.')
