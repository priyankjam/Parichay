/* Actual loaded-font geometry. All text originates in escaped server markup. */
window.paginateDocument = (targetDocument) => {
 const document=targetDocument || window.document;
 const getComputedStyle=document.defaultView.getComputedStyle.bind(document.defaultView);
 const root=document.querySelector('.repaired-document');if(!root)return null;
 const first=root.querySelector('.first-page').cloneNode(true),continuation=root.querySelector('#r-continuation').content.firstElementChild.cloneNode(true),source=root.querySelector('.r-source');
 const leadSource=[...source.querySelector('.r-lead-source').children],laneSources=[...source.querySelectorAll('.r-lane-source')].map(l=>[...l.children]),photos=[...(source.querySelector('.r-photo-source')?.children||[])];
 const clone=q=>q.map(el=>el.cloneNode(true));let operations=0;
 // Measure a fresh continuation once, at the real print width. A short record
 // moves there intact; only a record taller than that safe area may be split.
 const probe=continuation.cloneNode(true);probe.style.cssText='position:fixed;left:-10000px;top:0;visibility:hidden';root.append(probe);
 const freshHeight=probe.querySelector('.r-body').getBoundingClientRect().height;probe.remove();
 const run=ratio=>{
  root.querySelectorAll('.r-page').forEach(p=>p.remove());let lead=clone(leadSource),queues=laneSources.map(clone),photoQueue=clone(photos),pages=[];
  const addPage=()=>{if(pages.length>=20)throw Error('Document exceeds 20 pages');const p=(pages.length?continuation:first).cloneNode(true);root.insertBefore(p,source);pages.push(p);return p;};
  const pieces=text=>typeof Intl.Segmenter==='function'?[...new Intl.Segmenter(undefined,{granularity:'grapheme'}).segment(text)].map(x=>x.segment):Array.from(text);
  const partial=(section)=>{const part=section.cloneNode(false);part.append(section.querySelector('h2').cloneNode(true));const groups=document.createElement('div');groups.className='r-groups';part.append(groups);return part;};
  const continued=s=>{if(!s.querySelector('.r-continued')){const note=document.createElement('span');note.className='r-continued';note.textContent=' · '+root.dataset.continued;s.querySelector('h2').append(note);}return s;};
  function fill(host,queue,limit){
   let progressed=false;
   const fits=el=>el.getBoundingClientRect().bottom<=limit+.2;
   while(queue.length){
    if(++operations>6000)throw Error('Pagination did not converge');
    const section=queue[0];host.append(section);
    for(const label of section.querySelectorAll('.r-label')){
     const line=parseFloat(getComputedStyle(label).lineHeight);
     if(label.getBoundingClientRect().height>line*2+.5)label.closest('.r-row').classList.add('prose');
    }
    if(fits(section)){queue.shift();progressed=true;continue;}
    section.remove();if(limit-host.getBoundingClientRect().bottom<45)break;
    if(section.classList.contains('r-gallery'))break;
    const part=partial(section),partGroups=part.querySelector('.r-groups');host.append(part);
    const groups=[...section.querySelector('.r-groups').children];let used=0;
    for(const group of groups){
     partGroups.append(group);if(fits(part)){used+=group.querySelectorAll('.r-row').length;continue;}
     const recordHeight=group.getBoundingClientRect().height+part.querySelector('h2').getBoundingClientRect().height+16;
     group.remove();
     // Education/career records remain whole unless taller than a fresh lane.
     const record=['education','career','family'].includes(section.dataset.section);
     if(record&&(used>0||recordHeight<=freshHeight*ratio))break;
     const out=group.cloneNode(false);partGroups.append(out);
     for(const row of [...group.children]){
      out.append(row);if(fits(part)){used++;continue;}
      const rowHeight=row.getBoundingClientRect().height+part.querySelector('h2').getBoundingClientRect().height+16;
      row.remove();
      if(used){group.prepend(row);break;}
      if(rowHeight<=freshHeight*ratio){group.prepend(row);break;}
      out.append(row);const value=row.querySelector('.r-value'),text=value.textContent,chars=pieces(text);let lo=0,hi=chars.length;
      while(lo<hi){const mid=Math.ceil((lo+hi)/2);value.textContent=chars.slice(0,mid).join('');if(fits(part))lo=mid;else hi=mid-1;}
      // Keep a heading with at least two lines of substantive content.
      if(lo<Math.min(chars.length,48)){value.textContent=text;group.prepend(row);break;}
      let end=lo;for(let x=lo-1;x>Math.max(0,lo-70);x--)if(/\s/.test(chars[x])){end=x+1;break;}
      value.textContent=chars.slice(0,end).join('');const remainder=row.cloneNode(true);remainder.querySelector('.r-value').textContent=chars.slice(end).join('');group.prepend(remainder);used++;break;
     }
     if(!out.children.length)out.remove();
     if(group.children.length)break;
    }
    // Build the remainder from the original group order (nodes moved above).
    const remaining=groups.filter(g=>g.parentNode!==partGroups&&g.children.length);
    if(!used){section.querySelector('.r-groups').replaceChildren(...groups);part.remove();break;}
    const rest=section.querySelector('.r-groups');rest.replaceChildren(...remaining);queue.shift();if(remaining.length)queue.unshift(continued(section));progressed=true;break;
   }
   return progressed;
  }
  while(lead.length||queues.some(q=>q.length)||photoQueue.length){
   const page=addPage(),body=page.querySelector('.r-body'),leadHost=page.querySelector('.r-lead'),lanes=page.querySelector('.r-lanes'),rect=body.getBoundingClientRect();const limit=rect.top+rect.height*ratio;
   let progress=false;
   if(lead.length)progress=fill(leadHost,lead,limit)||progress;
   if(!lead.length){
    const activeQueues=queues.filter(q=>q.length);
    lanes.classList.toggle('one-lane',activeQueues.length===1);
    activeQueues.forEach(queue=>{const lane=document.createElement('div');lane.className='r-lane';lanes.append(lane);progress=fill(lane,queue,limit)||progress;});
    if(!queues.some(q=>q.length)&&photoQueue.length){const ph=document.createElement('div');ph.className='r-photo-flow';body.append(ph);progress=fill(ph,photoQueue,limit)||progress;}
   }
   if(!progress){
    if(pages.length===1)continue;
    throw Error('A heading or image cannot fit in the A4 content area');
   }
  }
  if(!pages.length)addPage();
  return pages;
 };
 let pages=run(1),natural=pages.length;
 // Reclaim a sparse final sheet by balancing actual heights, never font scaling.
 if(natural>1){
  let lastRatio=1;
  for(const ratio of [.90,.82,.74,.66]){
   operations=0;let candidate;
   try{candidate=run(ratio);}catch(error){
    // Balancing is optional. A large photo may fit the full safe area but
    // not the shorter trial area; retain the last complete arrangement.
    if(!/cannot fit|exceeds 20 pages/.test(error.message))throw error;
    operations=0;pages=run(lastRatio);break;
   }
   if(candidate.length>natural){operations=0;pages=run(lastRatio);break;}
   pages=candidate;lastRatio=ratio;
  }
 }
 source.remove();root.querySelector('#r-continuation').remove();
 const violations=[];
 pages.forEach((page,i)=>{
  page.querySelector('.r-page-number').textContent=`${root.dataset.pageWord} ${i+1} / ${pages.length}`;
  const body=page.querySelector('.r-body').getBoundingClientRect();
  for(const el of page.querySelectorAll('.r-row,.r-value,.r-section')){const r=el.getBoundingClientRect();if(r.bottom>body.bottom+.8||r.right>body.right+.8||r.left<body.left-.8)violations.push({page:i+1,kind:'text overflow'});}
  const header=page.querySelector('header').getBoundingClientRect();if(header.bottom>body.top+.8)violations.push({page:i+1,kind:'header overflow'});
 });
 if(violations.length)throw Error(JSON.stringify(violations));
 return {pages:pages.length,violations};
}
