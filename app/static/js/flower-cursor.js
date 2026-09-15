/* Hero-only enhancement. No storage, network rendering, or motion dependencies. */
(() => {
 const hero=document.querySelector('.editorial-hero');if(!hero)return;
 const fine=matchMedia('(hover:hover) and (pointer:fine) and (forced-colors:none)'),reduced=matchMedia('(prefers-reduced-motion:reduce)');
 const cursor=document.createElement('div');cursor.className='craft-cursor';cursor.setAttribute('aria-hidden','true');cursor.innerHTML='<span class="craft-dot"></span><span class="craft-ring"></span><span class="craft-label"></span>';
 const label=cursor.querySelector('.craft-label');let active=false,raf=0,x=0,y=0,cx=0,cy=0,nx=0,ny=0;
 function hide(){active=false;cancelAnimationFrame(raf);raf=0;cursor.remove();hero.classList.remove('craft-pointer');hero.style.setProperty('--px','0');hero.style.setProperty('--py','0');}
 function frame(){raf=0;if(!active)return;const lag=reduced.matches?1:.25;cx+=(x-cx)*lag;cy+=(y-cy)*lag;cursor.style.transform=`translate3d(${cx}px,${cy}px,0)`;if(Math.abs(x-cx)+Math.abs(y-cy)>.15)raf=requestAnimationFrame(frame);}
 function move(e){
  if(!fine.matches||e.pointerType!=='mouse'){hide();return;}
  const target=e.target instanceof Element?e.target:null;if(!target||target.closest('input,textarea,select,[contenteditable=true]')){hide();return;}
  x=e.clientX;y=e.clientY;
  if(!active){active=true;cx=x;cy=y;document.body.append(cursor);hero.classList.add('craft-pointer');}
  const design=target.closest('[data-cursor-label]');label.textContent=design?.dataset.cursorLabel||'';cursor.classList.toggle('over-design',Boolean(design));cursor.classList.toggle('over-control',Boolean(target.closest('a,button')));
  if(!reduced.matches){const box=hero.getBoundingClientRect();nx=Math.max(-1,Math.min(1,2*(x-box.left)/box.width-1));ny=Math.max(-1,Math.min(1,2*(y-box.top)/box.height-1));hero.style.setProperty('--px',nx.toFixed(3));hero.style.setProperty('--py',ny.toFixed(3));const paper=hero.querySelector('.hero-collection').getBoundingClientRect();hero.style.setProperty('--light-x',`${Math.max(0,Math.min(100,(x-paper.left)/paper.width*100))}%`);hero.style.setProperty('--light-y',`${Math.max(0,Math.min(100,(y-paper.top)/paper.height*100))}%`);}
  if(!raf)raf=requestAnimationFrame(frame);
 }
 hero.addEventListener('pointermove',move,{passive:true});hero.addEventListener('pointerover',move,{passive:true});hero.addEventListener('pointerleave',hide);hero.addEventListener('pointerdown',e=>{if(e.pointerType!=='mouse')hide();},{passive:true});
 document.addEventListener('keydown',e=>{if(e.key==='Tab'||e.key==='Escape')hide();});window.addEventListener('blur',hide);window.addEventListener('scroll',hide,{passive:true});document.addEventListener('visibilitychange',()=>{if(document.hidden)hide();});fine.addEventListener('change',hide);reduced.addEventListener('change',hide);
 // The same fictional profile, changed only after an explicit button press.
 const buttons=[...hero.querySelectorAll('[data-hero-style]')],image=hero.querySelector('#hero-primary-image'),link=hero.querySelector('#hero-primary-design'),status=hero.querySelector('#hero-style-status');let request=0;
 buttons.forEach(button=>button.addEventListener('click',async()=>{
  const current=++request;const next=new Image();next.src=button.dataset.src;link.setAttribute('aria-busy','true');
  try{await next.decode();if(current!==request)return;image.src=next.src;image.alt=(document.documentElement.lang==='hi'?'आरव मेहता का काल्पनिक बायोडाटा — ':'Aarav Mehta’s fictional biodata — ')+button.dataset.name;const url=new URL(link.href);url.searchParams.set('design',button.dataset.heroStyle);link.href=url;
   buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));status.textContent=document.documentElement.lang==='hi'?`${button.dataset.name} · वही जानकारी, नया अंदाज़।`:`${button.dataset.name} · Same details, a new expression.`;
   if(!reduced.matches&&image.animate)image.animate([{opacity:.45},{opacity:1}],{duration:280,easing:'ease-out'});
  }catch{if(current===request)status.textContent=document.documentElement.lang==='hi'?'डिज़ाइन लोड नहीं हुआ। फिर से कोशिश करें।':'That design could not load. Please try again.';}finally{if(current===request)link.removeAttribute('aria-busy');}
 }));
})();
