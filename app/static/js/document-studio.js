/** Real PDF pages, separate preview and thumbnail lanes, and a private in-memory preview cache. */
export class DocumentStudio {
 constructor({t,templates,onPaint}) {
  this.t=t;this.templates=templates;this.onPaint=onPaint;
  this.running=new Set();this.cache=new Map();this.queue=[];this.pending=new Set();this.generation=0;this.page=0;
  this.observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
   if(entry.isIntersecting&&this.renderAllowed&&this.hasData&&!this.sample)this.ensure(entry.target.dataset.thumbnail,true);
  }),{rootMargin:'80px 0px'});
  document.getElementById('preview-previous').onclick=()=>this.turn(-1);
  document.getElementById('preview-next').onclick=()=>this.turn(1);
  document.getElementById('preview-retry').onclick=()=>{this.cache.delete(this.selected);this.ensure(this.selected,false,true);};
 }
 update(payload,{render=false,library=false,sample=false}={}) {
  this.sample=sample;
  const identity=JSON.stringify({...payload,template:''});
  if(identity!==this.identity){
   this.identity=identity;this.generation++;this.cache.clear();this.queue=[];this.pending.clear();
  }
  if(this.selected!==payload.template)this.page=0;
  this.payload=payload;this.selected=payload.template;this.renderAllowed=render;
  this.hasData=Object.values(payload.sections).some(value=>(Array.isArray(value)?value:[value]).some(row=>Object.values(row).some(v=>String(v).trim())))||payload.customSections.some(s=>s.fields.some(f=>f.value));
  this.paint();
  if(render&&this.hasData)this.ensure(this.selected,false);
  const visibleDesigns=new Set([...document.querySelectorAll('[data-thumbnail]')].map(el=>el.dataset.thumbnail));
  this.queue=this.queue.filter(job=>{
   if(job.thumbnail&&(!library||!visibleDesigns.has(job.template))){this.pending.delete(job.key);return false;}
   return true;
  });
  this.observer.disconnect();
  document.querySelectorAll('[data-thumbnail]').forEach(card=>{
   this.paintThumbnail(card);
   if(library&&!sample)this.observer.observe(card);
  });
 }
 ensure(template,thumbnail,front=false){
  const result=this.cache.get(template);
  if(result?.error&&thumbnail&&!front)return;
  if(result?.pages&& (thumbnail||result.pdf))return;
  const key=`${this.generation}:${template}:${thumbnail}`;
  if(thumbnail&&this.pending.has(`${this.generation}:${template}:false`))return;
  if(this.pending.has(key))return;
  this.pending.add(key);
  const job={key,generation:this.generation,template,thumbnail,payload:{...this.payload,template}};
  if(front||!thumbnail)this.queue.unshift(job);else this.queue.push(job);
  this.pump();
 }
 pump(){
  // One full preview and one thumbnail may render together. Keep within the
  // server's two render slots; scrolling cannot block the selected document.
  for(const lane of [false,true]){
   if(this.running.has(lane))continue;
   const index=this.queue.findIndex(job=>job.thumbnail===lane);
   if(index<0)continue;
   const job=this.queue.splice(index,1)[0],cached=this.cache.get(job.template);
   if(job.generation!==this.generation||(cached?.pages&&(job.thumbnail||cached.pdf))){this.pending.delete(job.key);this.pump();continue;}
   this.running.add(lane);this.run(job);
  }
 }
 async run(job){
  const abort=new AbortController(),timeout=setTimeout(()=>abort.abort(),60000);
  try{
   let response;
   for(let attempt=0;attempt<4;attempt++){
    if(job.generation!==this.generation)return;
    if(abort.signal.aborted)throw new Error('preview timeout');
    response=await fetch('/api/preview',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':document.querySelector('meta[name="csrf-token"]').content},body:JSON.stringify({profile:job.payload,thumbnail:job.thumbnail}),signal:abort.signal});
    const retryAfter=Number(response.headers.get('Retry-After'));
    if(response.status!==503||!Number.isFinite(retryAfter)||retryAfter<=0||attempt===3)break;
    // Only explicit temporary capacity errors retry. Keep the loading state,
    // back off between attempts, and abandon stale drafts before sending again.
    await new Promise(resolve=>setTimeout(resolve,Math.min(retryAfter,5)*1000*(attempt+1)));
   }
   if(!response.ok)throw new Error('preview unavailable');
   const result=await response.json();
   if(!Array.isArray(result.pages)||!result.pages.length||!Number.isInteger(result.pageCount))throw new Error('invalid preview');
   if(job.generation===this.generation){
    const existing=this.cache.get(job.template);
    if(!existing?.pdf||result.pdf)this.cache.set(job.template,result);
    // Retain at most three full PDFs; other designs keep only their first sheet.
    const full=[...this.cache].filter(([,value])=>value.pdf);
    for(const [id,value] of full.slice(0,-3))if(id!==this.selected)this.cache.set(id,{pages:[value.pages[0]],pageCount:value.pageCount});
   }
  }catch{
   if(job.generation===this.generation&&!this.cache.get(job.template)?.pdf)this.cache.set(job.template,{error:true});
  }finally{
   clearTimeout(timeout);this.running.delete(job.thumbnail);this.pending.delete(job.key);
   if(job.generation===this.generation){this.paint();document.querySelectorAll('[data-thumbnail]').forEach(el=>this.paintThumbnail(el));}
   this.pump();
  }
 }
 paintThumbnail(card){
  const result=this.cache.get(card.dataset.thumbnail),personalized=Boolean(result?.pages);
  const state=personalized||this.sample?'ready':'sample';
  card.dataset.state=state;
  const image=card.querySelector('img'),note=card.querySelector('.thumbnail-note');
  // Only fictional samples are public/cacheable. Personal pages stay in memory
  // and are cleared immediately when any profile value or visibility changes.
  const sample=`/static/artwork/${card.dataset.thumbnail.startsWith('craft-')?'collection-gallery-v1':'gallery-v1'}/${this.payload?.gender==='female'?'female':'male'}-${this.payload?.language==='hi'?'hi':'en'}-${card.dataset.thumbnail}.webp`;
  const src=personalized?'data:image/webp;base64,'+result.pages[0]:sample;
  if(image.getAttribute('src')!==src)image.src=src;
  image.loading='lazy';image.decoding='async';image.hidden=false;
  note.textContent=this.t(result?.error?'thumbnailSampleError':'thumbnailSampleUpdating');
  note.hidden=personalized||this.sample;
 }

 paint(){
  const result=this.cache.get(this.selected),ready=Boolean(result?.pdf),error=Boolean(result?.error);
  const state=!this.hasData?'empty':error?'error':ready?'ready':this.renderAllowed?'loading':'idle';
  const viewport=document.getElementById('document-preview');viewport.dataset.state=state;
  document.getElementById('preview-panel').setAttribute('aria-busy',String(state==='loading'));
  const img=document.getElementById('preview-page-image'),message=document.getElementById('preview-message');
  img.hidden=!ready;message.hidden=ready;
  document.getElementById('preview-retry').hidden=!error;
  document.getElementById('preview-message-text').textContent=this.t(state==='empty'?'previewEmpty':state==='error'?'previewFailed':state==='idle'?'previewOpenHint':'previewLoading');
  const theme=this.templates.find(x=>x.id===this.selected);
  document.getElementById('template-name').textContent=this.payload?.language==='hi'?theme?.hi:theme?.name;
  document.getElementById('preview-page-controls').hidden=!ready;
  document.getElementById('preview-zoom').disabled=!ready;
  document.getElementById('page-count').textContent=ready?`A4 · ${result.pageCount} ${this.t(result.pageCount===1?'pageSingular':'pagePlural')}`:'A4';
  if(ready){
   this.page=Math.min(this.page,result.pageCount-1);
   const src='data:image/webp;base64,'+result.pages[this.page];if(img.src!==src)img.src=src;
   const pageLabel=this.t('pageOf').replace('{page}',this.page+1).replace('{total}',result.pageCount);
   img.alt=pageLabel+' · '+(this.payload.language==='hi'?theme.hi:theme.name);
   document.getElementById('preview-page-number').textContent=pageLabel;
   document.getElementById('preview-previous').disabled=this.page===0;
   document.getElementById('preview-next').disabled=this.page===result.pageCount-1;
   const accessible=document.getElementById('preview-text');accessible.replaceChildren();
   if(result.accessible){const heading=document.createElement('h1');heading.textContent=result.accessible.name;accessible.append(heading);for(const s of result.accessible.sections){const section=document.createElement('section'),title=document.createElement('h2');title.textContent=s.title;section.append(title);for(const group of s.groups)for(const row of group){const line=document.createElement('p');line.textContent=(row.label?row.label+': ':'')+row.value;section.append(line);}accessible.append(section);}}else accessible.textContent=result.text||'';
  }else{img.removeAttribute('src');document.getElementById('preview-text').textContent='';}
  this.onPaint();
 }
 turn(direction){this.page+=direction;this.paint();document.querySelector('.preview-scroll').scrollTo({top:0,left:0});}
 pdf(payload){
  if(JSON.stringify({...payload,template:''})!==this.identity)return null;
  const result=this.cache.get(payload.template);if(!result?.pdf)return null;
  const bytes=Uint8Array.from(atob(result.pdf),c=>c.charCodeAt(0));
  return new Blob([bytes],{type:'application/pdf'});
 }
 clear(){this.generation++;this.queue=[];this.pending.clear();this.cache.clear();this.identity=null;this.page=0;}
}
