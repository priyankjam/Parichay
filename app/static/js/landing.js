/* Ephemeral fictional demos only: no storage, requests or user-data collection. */
const hi=document.documentElement.lang==='hi';
const names={editorial:['Minimal Editorial','मिनिमल एडिटोरियल'],professional:['Modern Professional','मॉडर्न प्रोफ़ेशनल'],ivory:['Premium Ivory','प्रीमियम आइवरी'],'figma-ganesha-ivory':['Ganesha Ivory','गणेश आइवरी']};
document.querySelectorAll('[data-design]').forEach(button=>button.addEventListener('click',()=>{
 const image=document.getElementById('collection-image'),name=names[button.dataset.design][hi?1:0];
 image.src=button.dataset.src;image.alt=(hi?'आरव मेहता का नमूना बायोडाटा: ':'Aarav Mehta sample biodata: ')+name;
 document.getElementById('collection-caption').textContent=name;
 const link=document.getElementById('use-design'),url=new URL(link.href);url.searchParams.set('design',button.dataset.design);link.href=url;
 document.querySelectorAll('[data-design]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
}));
document.querySelectorAll('[data-script]').forEach(button=>button.addEventListener('click',()=>{
 const hindi=button.dataset.script==='hi';document.querySelector('.language-sample').lang=button.dataset.script;
 document.getElementById('language-name').textContent=hindi?'आरव मेहता':'Aarav Mehta';
 document.getElementById('language-description').textContent=hindi?'मेरे बारे में':'A little about me';
 document.getElementById('language-body').textContent=hindi?'सुंदर चीज़ें बनाना। नई जगहें देखना। अपनों के करीब रहना।':'Designing thoughtful things. Exploring new places. Staying close to the people who matter.';
 document.querySelectorAll('[data-script]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
}));
document.querySelectorAll('[data-privacy]').forEach(input=>input.addEventListener('change',()=>{
 document.querySelector(`[data-private-row="${input.dataset.privacy}"]`).hidden=!input.checked;
 input.closest('label').querySelector('.toggle-label').textContent=input.checked?(hi?'शामिल':'Included'):(hi?'छिपा हुआ':'Hidden');
}));
// Mobile funnel event only; no profile values, user identifiers or network transport.
document.querySelectorAll('a[href*="/create"]').forEach(link=>link.addEventListener('click',()=>{
 if(matchMedia('(max-width:767px)').matches)document.dispatchEvent(new CustomEvent('parichay:analytics',{detail:Object.freeze({event:'landing_cta',surface:'mobile'})}));
}));
