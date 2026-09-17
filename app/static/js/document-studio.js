/** Browser-rendered A4 previews. No server browser or PDF job is needed to edit. */
const A4_WIDTH=210*96/25.4;
const mounted=new WeakMap();
const observedHosts=new Set();
const pageResize=new ResizeObserver(entries=>entries.forEach(({target})=>{
 const frame=target.querySelector('iframe');
 if(frame)frame.style.transform=`scale(${target.clientWidth/A4_WIDTH})`;
}));

export function mountPreviewPage(host,result,index=0){
 if(!host||!result?.ready||!result.pages[index])return;
 for(const oldHost of observedHosts)if(!oldHost.isConnected){pageResize.unobserve(oldHost);observedHosts.delete(oldHost);}
 const old=mounted.get(host);
 if(old?.result===result&&old.index===index)return;
 const frame=document.createElement('iframe');
 // The parent may measure the same-origin document, but scripts, forms,
 // popups and navigation inside the document are not permitted.
 frame.setAttribute('sandbox','allow-same-origin');
 frame.tabIndex=-1;frame.setAttribute('aria-hidden','true');
 frame.title=`Biodata page ${index+1}`;
 frame.className='browser-preview-frame';
 frame.srcdoc=`<!doctype html><html lang="${result.language==='hi'?'hi':'en'}"><head>${result.head}<style>html,body{overflow:hidden}</style></head><body>${result.shell.replace('</main>',result.pages[index]+'</main>')}</body></html>`;
 host.replaceChildren(frame);host.classList.add('browser-preview-page');
 mounted.set(host,{result,index});pageResize.observe(host);observedHosts.add(host);
 frame.style.transform=`scale(${host.clientWidth/A4_WIDTH})`;
}

function paginateHTML(html,signal){
 return new Promise((resolve,reject)=>{
  const frame=document.createElement('iframe');
  frame.className='preview-measure-frame';frame.setAttribute('sandbox','allow-same-origin');
  frame.setAttribute('aria-hidden','true');frame.tabIndex=-1;frame.title='Preparing biodata';
  let settled=false;
  const finish=(error,value)=>{
   if(settled)return;settled=true;signal.removeEventListener('abort',cancel);frame.remove();
   error?reject(error):resolve(value);
  };
  const cancel=()=>finish(new DOMException('Preview superseded','AbortError'));
  signal.addEventListener('abort',cancel,{once:true});
  frame.onload=async()=>{
   try{
    const doc=frame.contentDocument;
    if(!doc?.querySelector('.repaired-document'))throw Error('Invalid preview document');
    // Load fonts actually used by the document and photos before measuring A4.
    await doc.fonts.ready;
    await Promise.all([...doc.images].map(image=>image.decode()));
    if(signal.aborted||settled)return;
    if(typeof window.paginateDocument!=='function')throw Error('Paginator unavailable');
    window.paginateDocument(doc);
    const root=doc.querySelector('.repaired-document');
    const pages=[...root.querySelectorAll(':scope > .r-page')].map(page=>page.outerHTML);
    if(!pages.length)throw Error('Empty preview');
    finish(null,{ready:true,head:doc.head.innerHTML,shell:root.cloneNode(false).outerHTML,
      language:doc.documentElement.lang,pages,pageCount:pages.length});
   }catch(error){finish(error);}
  };
  if(signal.aborted){cancel();return;}
  frame.srcdoc=html;document.body.append(frame);
 });
}

export class DocumentStudio {
 constructor({t,templates,onPaint}){
  this.t=t;this.templates=templates;this.onPaint=onPaint;
  this.cache=new Map();this.generation=0;this.page=0;
  document.getElementById('preview-previous').onclick=()=>this.turn(-1);
  document.getElementById('preview-next').onclick=()=>this.turn(1);
  document.getElementById('preview-retry').onclick=()=>{this.cache.delete(this.selected);this.ensure(this.selected);};
 }
 update(payload,{render=false,sample=false}={}){
  this.sample=sample;
  const identity=JSON.stringify({...payload,template:''});
  if(identity!==this.identity){this.identity=identity;this.generation++;this.cache.clear();this.controller?.abort();this.activeKey=null;}
  if(this.selected!==payload.template){this.page=0;this.controller?.abort();this.activeKey=null;}
  this.payload=payload;this.selected=payload.template;this.renderAllowed=render;
  this.hasData=Object.values(payload.sections).some(value=>(Array.isArray(value)?value:[value]).some(row=>Object.values(row).some(v=>String(v).trim())))||payload.customSections.some(s=>s.fields.some(f=>f.value));
  this.paint();this.paintThumbnails();
  if(render&&this.hasData)this.ensure(this.selected);
 }
 ensure(template){
  if(this.cache.get(template)?.ready)return;
  const key=`${this.generation}:${template}`;
  if(this.activeKey===key)return;
  this.controller?.abort();const controller=new AbortController();this.controller=controller;this.activeKey=key;
  this.run({template,generation:this.generation,payload:{...this.payload,template},controller,key});
 }
 async run(job){
  const {controller}=job,timeout=setTimeout(()=>controller.abort(),30000);
  try{
   const response=await fetch('/api/preview/html',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':document.querySelector('meta[name="csrf-token"]').content},body:JSON.stringify({profile:job.payload}),signal:controller.signal});
   if(!response.ok)throw Error('Preview unavailable');
   const data=await response.json();
   if(typeof data.html!=='string')throw Error('Invalid preview');
   const result=await paginateHTML(data.html,controller.signal);
   result.accessible=data.accessible;
   if(job.generation===this.generation&&!controller.signal.aborted){
    this.cache.set(job.template,result);
    // Bound document memory; untouched designs use instant fictional samples.
    for(const id of [...this.cache.keys()].slice(0,-3))if(id!==this.selected)this.cache.delete(id);
   }
  }catch{
   if(job.generation===this.generation&&job.key===this.activeKey)this.cache.set(job.template,{error:true});
  }finally{
   clearTimeout(timeout);
   if(job.key===this.activeKey){this.activeKey=null;this.paint();this.paintThumbnails();}
  }
 }
 paintThumbnails(){document.querySelectorAll('[data-thumbnail]').forEach(card=>this.paintThumbnail(card));}
 paintThumbnail(card){
  const result=this.cache.get(card.dataset.thumbnail),personalized=Boolean(result?.ready);
  card.dataset.state=personalized||this.sample?'ready':'sample';
  const image=card.querySelector('img'),note=card.querySelector('.thumbnail-note');
  let live=card.querySelector('.thumbnail-live');
  if(personalized){
   if(!live){live=document.createElement('div');live.className='thumbnail-live';card.prepend(live);}
   mountPreviewPage(live,result);image.hidden=true;
  }else{
   if(live){pageResize.unobserve(live);observedHosts.delete(live);live.remove();}
   const src=`/static/artwork/repair-gallery-v2/${this.payload?.gender==='female'?'female':'male'}-${this.payload?.language==='hi'?'hi':'en'}-${card.dataset.thumbnail}.webp`;
   if(image.getAttribute('src')!==src)image.src=src;
   image.loading='lazy';image.decoding='async';image.hidden=false;
  }
  note.textContent=this.payload?.language==='hi'?'नमूना · अपनी जानकारी देखने के लिए चुनें':'Sample · select to see your details';
  note.hidden=personalized||this.sample;
 }
 paint(){
  const result=this.cache.get(this.selected),ready=Boolean(result?.ready),error=Boolean(result?.error);
  const state=!this.hasData?'empty':error?'error':ready?'ready':this.renderAllowed?'loading':'idle';
  document.getElementById('document-preview').dataset.state=state;
  document.getElementById('preview-panel').setAttribute('aria-busy',String(state==='loading'));
  const host=document.getElementById('preview-page-image');host.hidden=!ready;
  document.getElementById('preview-message').hidden=ready;
  document.getElementById('preview-retry').hidden=!error;
  document.getElementById('preview-message-text').textContent=this.t(state==='empty'?'previewEmpty':state==='error'?'previewFailed':state==='idle'?'previewOpenHint':'previewLoading');
  const theme=this.templates.find(x=>x.id===this.selected);
  document.getElementById('template-name').textContent=this.payload?.language==='hi'?theme?.hi:theme?.name;
  document.getElementById('preview-page-controls').hidden=!ready;
  document.getElementById('preview-zoom').disabled=!ready;
  document.getElementById('page-count').textContent=ready?`A4 · ${result.pageCount} ${this.t(result.pageCount===1?'pageSingular':'pagePlural')}`:'A4';
  const accessible=document.getElementById('preview-text');accessible.replaceChildren();
  if(ready){
   this.page=Math.min(this.page,result.pageCount-1);mountPreviewPage(host,result,this.page);
   document.getElementById('preview-page-number').textContent=this.t('pageOf').replace('{page}',this.page+1).replace('{total}',result.pageCount);
   document.getElementById('preview-previous').disabled=this.page===0;
   document.getElementById('preview-next').disabled=this.page===result.pageCount-1;
   if(result.accessible){const heading=document.createElement('h1');heading.textContent=result.accessible.name;accessible.append(heading);for(const s of result.accessible.sections){const section=document.createElement('section'),title=document.createElement('h2');title.textContent=s.title;section.append(title);for(const group of s.groups)for(const row of group){const line=document.createElement('p');line.textContent=(row.label?row.label+': ':'')+row.value;section.append(line);}accessible.append(section);}}
  }else{host.replaceChildren();mounted.delete(host);}
  this.onPaint();
 }
 turn(direction){this.page+=direction;this.paint();document.querySelector('.preview-scroll').scrollTo({top:0,left:0});}
 // Downloads remain explicit server exports, independent of browser previews.
 pdf(){return null;}
 clear(){this.generation++;this.controller?.abort();this.activeKey=null;this.cache.clear();this.identity=null;this.page=0;}
}
