/** Presentation helpers: no profile persistence, network calls, or document layout. */
export const escapeHTML = (text='') => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const icon = (name) => `<svg class="ui-icon ${name.startsWith('arrow-')?'directional':''}" aria-hidden="true" focusable="false"><use href="/static/icons.svg#${escapeHTML(name)}"></use></svg>`;
export const localeDirection = (language) => ['ur','ar','fa'].includes(language.split('-')[0]) ? 'rtl' : 'ltr';
export const personalGroups = [
 {key:'basics',title:'basicDetails',fields:['name','age','height','motherTongue']},
 {key:'location',title:'whereYouLive',fields:['city','nativePlace']},
 {key:'morePersonal',title:'morePersonal',fields:['maritalStatus','nationality'],optional:true}
];
export const sectionSteps = {personal:3,contact:3,education:4,career:4,family:5,culture:6,astrology:6,about:7,partner:7,photos:8};
export function disclosure(key, title, content, open=false, hint=''){
 return `<details class="disclosure-group" data-disclosure="${escapeHTML(key)}" ${open?'open':''}><summary><span>${escapeHTML(title)}${hint?`<small>${escapeHTML(hint)}</small>`:''}</span><span class="disclosure-chevron" aria-hidden="true">${icon('plus')}</span></summary><div class="disclosure-content">${content}</div></details>`;
}
export function fieldError(key,value,t){
 if(!String(value).trim())return '';
 if(key==='age'&&(!/^\d+$/.test(value)||Number(value)<18||Number(value)>120))return t('ageError');
 if(key==='email'&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value))return t('emailError');
 if(key==='birthDate'){
  const date=new Date(value+'T00:00:00'),now=new Date();
  let age=now.getFullYear()-date.getFullYear();
  if(now.getMonth()<date.getMonth()||(now.getMonth()===date.getMonth()&&now.getDate()<date.getDate()))age--;
  if(Number.isNaN(date.getTime())||age<18||age>120)return t('birthError');
 }
 return '';
}
/** Move the row and its disclosure flags together; never attach hidden data to another row. */
export function moveEntry(profile,key,from,to){
 const rows=profile.sections[key];if(to<0||to>=rows.length)return;
 rows.splice(to,0,rows.splice(from,1)[0]);
 profile.hiddenFields=profile.hiddenFields.map(id=>{
  if(!id.startsWith(key+'.'))return id;
  const parts=id.split('.'),i=Number(parts[1]);
  if(i===from)parts[1]=String(to);
  else if(from<to&&i>from&&i<=to)parts[1]=String(i-1);
  else if(from>to&&i>=to&&i<from)parts[1]=String(i+1);
  return parts.join('.');
 });
}
