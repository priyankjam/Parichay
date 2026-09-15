/* Trusted renderer code. User input remains escaped HTML; no source is evaluated. */
() => {
 const root=document.querySelector('.craft-document');if(!root)return null;
 const source=root.querySelector('.craft-source'),continuation=root.querySelector('#craft-continuation');
 let page=root.querySelector('.craft-page'),body=page.querySelector('.craft-body');
 const queue=[...source.children];let pages=1,operations=0;
 const nextPage=()=>{if(++pages>20)throw Error('Document exceeds 20 pages');page=continuation.content.firstElementChild.cloneNode(true);root.insertBefore(page,continuation);body=page.querySelector('.craft-body');};
 const fits=()=>{const edge=body.getBoundingClientRect().bottom;return [...body.children].every(el=>el.getBoundingClientRect().bottom<=edge+.3);};
 const wrap=section=>{const unit=document.createElement('div');unit.className='craft-unit';unit.append(section);return unit;};
 const continuationSection=section=>{
  const copy=section.cloneNode(false),heading=section.querySelector('h2').cloneNode(true),groups=document.createElement('div');groups.className='craft-groups';
  heading.querySelector('.continued-heading')?.remove();const note=document.createElement('span');note.className='continued-heading';note.textContent=' · '+root.dataset.continued;heading.append(note);copy.append(heading,groups);return copy;
 };
 // Whole sections fit together first; oversized sections split at group/row,
 // then Unicode grapheme boundaries as a last resort. Never reduce body type.
 const splitSection=section=>{
  const originalRows=[...section.querySelectorAll('.craft-group')].map(group=>[...group.children]);
  const part=section.cloneNode(false);part.append(section.querySelector('h2').cloneNode(true));
  const groups=document.createElement('div');groups.className='craft-groups';part.append(groups);const unit=wrap(part);body.append(unit);
  for(let gi=0;gi<originalRows.length;gi++){
   const group=document.createElement('div');group.className='craft-group';groups.append(group);
   for(let ri=0;ri<originalRows[gi].length;ri++){
    const row=originalRows[gi][ri];group.append(row);
    if(fits())continue;
    row.remove();
    // Preserve rows when there is already useful content on the page.
    let remainder=row;
    if(!groups.querySelector('.craft-row')){
     group.append(row);const value=row.querySelector('.craft-value'),text=value.textContent;
     const pieces=typeof Intl.Segmenter==='function'?[...new Intl.Segmenter(undefined,{granularity:'grapheme'}).segment(text)].map(x=>x.segment):Array.from(text);
     let lo=0,hi=pieces.length;
     while(lo<hi){const mid=Math.ceil((lo+hi)/2);value.textContent=pieces.slice(0,mid).join('');if(fits())lo=mid;else hi=mid-1;}
     if(lo===0)throw Error('A field heading cannot fit on a page');
     // Prefer the final whitespace boundary where it does not waste most of a line.
     let end=lo;for(let i=lo-1;i>Math.max(0,lo-55);i--)if(/\s/.test(pieces[i])){end=i+1;break;}
     value.textContent=pieces.slice(0,end).join('');remainder=row.cloneNode(true);remainder.querySelector('.craft-value').textContent=pieces.slice(end).join('');
    }
    if(!groups.querySelector('.craft-row')){unit.remove();throw Error('Empty split');}
    const rest=continuationSection(section),restGroups=rest.querySelector('.craft-groups');
    const newGroup=document.createElement('div');newGroup.className='craft-group';newGroup.append(remainder,...originalRows[gi].slice(ri+1));restGroups.append(newGroup);
    for(const later of originalRows.slice(gi+1)){const g=document.createElement('div');g.className='craft-group';g.append(...later);restGroups.append(g);}
    queue.unshift(wrap(rest));return;
   }
  }
 };
 while(queue.length){
  if(++operations>500)throw Error('Pagination did not converge');
  const unit=queue.shift();body.append(unit);if(fits())continue;unit.remove();
  // Independent columns avoid artificial row gaps. If a whole spread cannot
  // fit, expose its sections to the same section-aware continuation system.
  if(unit.classList.contains('spread')){
   const columns=[...unit.children],removed=columns.map(()=>[]);body.append(unit);
   while(!fits() && columns.some(c=>c.children.length)){
    const heights=columns.map(c=>c.lastElementChild?.getBoundingClientRect().bottom||0),index=heights[0]>=heights[1]?0:1;
    const last=columns[index].lastElementChild;if(!last)break;removed[index].unshift(last);last.remove();
   }
   const retained=columns.some(c=>c.children.length);
   if(retained&&fits()){
    if(removed.every(c=>c.length)){const rest=unit.cloneNode(false);for(const items of removed){const col=document.createElement('div');col.className='craft-column';col.append(...items);rest.append(col);}queue.unshift(rest);}
    else queue.unshift(...removed.flat().map(wrap));
    continue;
   }
   unit.remove();columns.forEach((c,i)=>removed[i].unshift(...c.children));const sections=[];while(removed.some(c=>c.length))for(const c of removed)if(c.length)sections.push(c.shift());queue.unshift(...sections.map(wrap));continue;
  }
  if(body.children.length){nextPage();body.append(unit);if(fits())continue;unit.remove();}
  // A large first-page header must not force splitting a section that fits page 2.
  else if(page.classList.contains('first-page')){nextPage();body.append(unit);if(fits())continue;unit.remove();}
  if(unit.classList.contains('paired')){queue.unshift(...[...unit.children].map(wrap));continue;}
  const section=unit.querySelector('.craft-section');if(!section)throw Error('An image exceeds the print area');splitSection(section);
  if(queue.length)nextPage();
 }
 source.remove();continuation.remove();
 const all=[...root.querySelectorAll('.craft-page')];all.forEach((p,i)=>p.querySelector('.craft-page-number').textContent=`${String(i+1).padStart(2,'0')} / ${String(all.length).padStart(2,'0')}`);
 const violations=[];
 all.forEach((p,i)=>{
  const b=p.querySelector('.craft-body').getBoundingClientRect();
  for(const el of p.querySelectorAll('.craft-row,.craft-value,.craft-unit')){
   const r=el.getBoundingClientRect();if(r.bottom>b.bottom+.5||r.left<b.left-.5||r.right>b.right+.5)violations.push({page:i+1,kind:'overflow'});
  }
  const h=p.querySelector('header').getBoundingClientRect();if(h.bottom>b.top+.5)violations.push({page:i+1,kind:'header overlap'});
 });
 if(violations.length)throw Error(JSON.stringify(violations));
 return {pages:all.length,violations};
}
