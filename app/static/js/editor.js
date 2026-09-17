import {createMobileProduct, isMobileProduct, mobileSteps} from './mobile-product.js';
import { hobbies, hobbyLabel, selectedHobbies, hobbyText } from './hobbies.js';
import { DocumentStudio, mountPreviewPage } from './document-studio.js';
import { escapeHTML, disclosure, personalGroups, sectionSteps, fieldError, moveEntry, icon, localeDirection } from './editor-ui.js';
import { words } from './locales.js';
import { migrateProfile } from './migrations.js';
import { openDraftStore } from './storage.js';

const config = JSON.parse(document.getElementById('app-config').textContent);
const $ = (id) => document.getElementById(id);
const esc = escapeHTML;
const clone = value => structuredClone(value);
let profile = clone(config.empty), step = 0, visited = new Set([0]), store, previewTimer, previewDeadline, noticeTimer, exporting = false, savedFile = null;
let saving = false, saveVersion = 0;
let exportingRevision = 0, revision = 0, cropSource = null, rotation = 0, cropIndex = -1;
let failedStorage = false, restoring = true, recoveryBlocked = false, deleting = false;
let previewFocus = null, replacementPhoto = -1;
let previewZoom = false, designFilter='all', spotlight=false;
let studio, mobile;
const demoPortraits=new Map();
let genderChange=0;
async function demoPortrait(gender=profile.gender){
 const key=gender==='female'?'female':'male';
 if(!demoPortraits.has(key))demoPortraits.set(key,fetch(config.demoPhotos[key]).then(r=>{if(!r.ok)throw new Error('Sample photo unavailable');return r.blob();}).then(blob=>new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=reject;reader.readAsDataURL(blob);})).catch(e=>{demoPortraits.delete(key);throw e;}));
 return demoPortraits.get(key);
}
async function sampleProfile(){
 const sample=clone(config.demo);sample.gender=profile.gender;sample.language=profile.language;sample.template=profile.template;sample.presentation=clone(profile.presentation);
 if(profile.gender==='female'){sample.sections.personal.name=profile.language==='hi'?'अनन्या मेहता':'Ananya Mehta';sample.sections.contact={name:sample.sections.personal.name,email:'ananya@example.com'};}else if(profile.language==='hi'){sample.sections.personal.name='आरव मेहता';sample.sections.contact.name='आरव मेहता';}
 sample.photos=[await demoPortrait(sample.gender)];return sample;
}
const disclosureState=new Map(), activeEntries=new Map();
const previewHome = document.createComment('Desktop preview position');
$('preview-panel').before(previewHome);


const steps = [
 ['A thoughtful beginning.','Let’s get started.','Choose your gender and preferred language to get started.','शुरुआत एक परिचय से।','आइए शुरुआत करें।','शुरुआत करने के लिए अपना लिंग और पसंदीदा भाषा चुनें।'],
 ['FIND YOUR EXPRESSION','A style that feels right.','Choose a starting point. You can change designs at any time.','अपनी शैली चुनें','आपकी पसंद की शैली।','यह शुरुआत है। आप डिज़ाइन कभी भी बदल सकते हैं।'],
 ['IN YOUR OWN WORDS','A familiar language.','Create comfortably in the language you prefer.','आपकी अपनी भाषा में','एक परिचित भाषा।','अपनी पसंद की भाषा में सहजता से बायोडाटा बनाएँ।'],
 ['THE ESSENTIALS','Let’s start with you.','Just the details you’d like someone to know. Everything is optional.','ज़रूरी बातें','शुरुआत आपके बारे में।','केवल वह जानकारी भरें जो आप बताना चाहते हैं। सब वैकल्पिक है।'],
 ['YOUR JOURNEY','Education and work.','Add qualifications and work experience for this biodata.','आपकी यात्रा','शिक्षा और काम।','जिनका बायोडाटा है, उनकी पढ़ाई और काम के बारे में बताएँ।'],
 ['THE PEOPLE AROUND YOU','A little about family.','Add the family details you want this biodata to include.','आपके अपने','परिवार के बारे में।','जिनका बायोडाटा है, उनके परिवार का परिचय दें।'],
 ['YOUR ROOTS, YOUR CHOICE','Traditions, if they matter to you.','These details are entirely optional. Leave anything out, or skip this step.','आपकी जड़ें, आपकी पसंद','परंपराएँ, यदि आप चाहें।','ये विवरण पूरी तरह वैकल्पिक हैं। आप यह चरण छोड़ सकते हैं।'],
 ['BEYOND THE BASICS','The things that make you, you.','A few honest lines often say more than a long list of facts.','जानकारी से आगे','जो आपको आप बनाता है।','कुछ सच्चे शब्द लंबी सूची से अधिक कह सकते हैं।'],
 ['PUT A FACE TO THE NAME','A face to your story.','A natural photo is all you need. Add up to five, or let your words do the talking.','आपकी एक झलक','आपकी कहानी, आपकी तस्वीर।','एक स्वाभाविक फ़ोटो पर्याप्त है। पाँच तक जोड़ें, या बिना फ़ोटो आगे बढ़ें।'],
 ['YOUR DESIGN','Choose a style.','Compare designs with your details. Find the one that feels right.','आपका डिज़ाइन','अपनी पसंद का डिज़ाइन चुनें।','अपनी जानकारी के साथ डिज़ाइन देखें और मनपसंद चुनें।'],
 ['A NEW BEGINNING','Ready to make an introduction.','Take one last look. Then choose the format that works for you.','एक नई शुरुआत','परिचय के लिए तैयार।','एक बार फिर देख लें। फिर अपनी पसंद का प्रारूप चुनें।']
];
const navNames = {en:['Gender & language','Style preference','Language','Personal & contact','Education & career','Family','Culture & birth details','About you','Photos','Design & preview','Download & share'],hi:['लिंग और भाषा','शैली','भाषा','व्यक्तिगत और संपर्क','शिक्षा और करियर','परिवार','संस्कृति और जन्म विवरण','आपके बारे में','फ़ोटो','डिज़ाइन और प्रीव्यू','डाउनलोड और साझा करें']};
// Keep section IDs stable for existing drafts and bookmarked editor links.
const stepOrder=[0,1,3,4,5,6,7,8,9,10];
const normalizeStep=id=>id===2?0:isMobileProduct()&&id===1?9:Math.max(0,Math.min(10,id));
const adjacentStep=direction=>{const order=isMobileProduct()?mobileSteps:stepOrder;return order[Math.max(0,Math.min(order.length-1,order.indexOf(step)+direction))];};
const t = key => {
 if(mobile?.active&&profile.language==='en'&&key==='thumbnailSampleUpdating')return 'Preparing your design…';
 if(mobile?.active&&profile.language==='en'&&key==='thumbnailSampleError')return 'Couldn’t load. Tap a design, then Preview to retry.';
 return words[profile.language][key] || words.en[key] || key;
};
const label = item => item.label[profile.language];
const title = item => item.title[profile.language];

function translatePage(){
 document.documentElement.lang=profile.language; document.documentElement.dir=localeDirection(profile.language); $('language').value=profile.language;
 document.querySelectorAll('[data-i18n]').forEach(el=>el.textContent=t(el.dataset.i18n));
 $('mobile-preview').textContent=t('previewShort');
 $('mobile-next').textContent=step===10?t('pdf'):step===9?t('nextExport'):t('continue');
 $('expand-preview').textContent=t($('preview-dialog').open?'backToEditing':'readPreview');
 $('expand-preview').setAttribute('aria-label', $('expand-preview').textContent);
 $('preview-zoom').textContent=t(previewZoom?'fitPreview':'zoomIn');
 for(const [id,key] of Object.entries({language:'languageLabel','more-button':'draftOptions',steps:'stepsLabel','info-dialog':'draftInformation','preview-panel':'preview'}))$(id).setAttribute('aria-label',t(key));
 document.querySelector('.skip-link').textContent=t('skipEditor');
 $('preview-previous').setAttribute('aria-label',t('previousPage'));$('preview-next').setAttribute('aria-label',t('nextPage'));$('preview-text').setAttribute('aria-label',t('biodataText'));
 document.querySelector('#info-dialog .dialog-close').setAttribute('aria-label',t('closeDialog'));
 document.querySelector('#crop-dialog .dialog-close').setAttribute('aria-label',t('cancelCrop'));mobile?.decorateDialogs();
}
function hasContent(){return Object.values(profile.sections).some(v=>JSON.stringify(v).replace(/[\[\]{},:"\s]/g,'').length>0 && (Array.isArray(v)?v:[v]).some(row=>Object.values(row).some(Boolean))) || profile.photos.length || profile.customSections.some(s=>s.fields.some(f=>f.value));}
function updateStatus(){ const state=failedStorage?'error':saving?'saving':!navigator.onLine?'offline':hasContent()?'saved':'ready';$('save-status').dataset.state=state;$('save-status').textContent=t(state==='error'?'savedError':state);$('storage-warning').hidden=!failedStorage;mobile?.sync(); }
function change(){
 revision++; savedFile=null;mobile?.changed();clearTimeout(previewTimer);
 // Start the durable transaction in this event, before a refresh can cancel a timer.
 // IndexedDB handles photos asynchronously; only visual rendering is debounced.
 save();
 const refresh=()=>{clearTimeout(previewTimer);clearTimeout(previewDeadline);previewDeadline=null;renderPreview();renderNav();};
 previewTimer=setTimeout(refresh,500);
 // A continuous stream of keystrokes must not postpone the preview indefinitely.
 if(!previewDeadline)previewDeadline=setTimeout(refresh,1500);
}
async function save(){
 if(restoring||recoveryBlocked||deleting)return;
 const version=++saveVersion;saving=true;updateStatus();
 try{if(!store)throw new Error();await store.put({profile:clone(profile),step,visited:[...visited],mobile:mobile?.snapshot()});if(version===saveVersion)failedStorage=false;}
 catch{if(version===saveVersion)failedStorage=true;}
 finally{if(version===saveVersion){saving=false;updateStatus();}}
}
function toast(message){clearTimeout(noticeTimer);$('toast').textContent=message;$('toast').hidden=false;noticeTimer=setTimeout(()=>$('toast').hidden=true,5000);}
function error(message,focus=false){const note=$('form-error');note.textContent=message;note.hidden=!message;if(message&&focus){note.tabIndex=-1;note.focus({preventScroll:true});note.scrollIntoView({block:'center',behavior:'instant'});}}
function heading(){
 const s=steps[step],o=profile.language==='hi'?3:0;
 return `<p class="step-eyebrow">${s[o]}</p><h1 class="step-heading">${s[o+1]}</h1><p class="step-description">${s[o+2]}</p>`;
}
function sectionHasDetails(key){
 if(key==='photos')return profile.photos.length>0;
 return (Array.isArray(profile.sections[key])?profile.sections[key]:[profile.sections[key]||{}]).some(row=>Object.values(row).some(v=>String(v).trim()));
}
function stepHasDetails(i){return Object.entries(sectionSteps).some(([key,target])=>target===i&&sectionHasDetails(key));}
function renderNav(){
 const complete=i=>i!==step&&visited.has(i);
 $('section-jump').innerHTML=stepOrder.map((i,position)=>`<option value="${i}" ${i===step?'selected':''}>${String(position+1).padStart(2,'0')}${complete(i)?' ✓':''} · ${navNames[profile.language][i]}</option>`).join('');
 $('steps').innerHTML=stepOrder.map((i,position)=>`<button class="step-link ${i===step?'active':''} ${complete(i)?'visited':''}" data-step="${i}" ${i===step?'aria-current="step"':''}><span class="step-number" aria-hidden="true">${String(position+1).padStart(2,'0')}</span><span class="step-label">${navNames[profile.language][i]}</span>${complete(i)?`<span class="step-check" aria-hidden="true">${icon('check')}</span><span class="sr-only">${t('stepReviewed')}</span>`:''}</button>`).join('');
 $('step-count').textContent=`${t('stepLabel')} ${String(stepOrder.indexOf(step)+1).padStart(2,'0')} / ${stepOrder.length}`;
 const count=[3,4,5,6,7,8].filter(stepHasDetails).length;
 $('progress-fill').style.width=`${count/6*100}%`;$('content-progress').textContent=`${count} / 6 ${t('withDetails')}`;
}
function languageChoices(){return `<div class="choice-grid">${[['en','English','Create in English'],['hi','हिन्दी','हिन्दी में बनाएँ']].map(([id,name,desc])=>`<button class="choice-card ${profile.language===id?'selected':''}" data-language="${id}" aria-pressed="${profile.language===id}"><span class="choice-icon">${id==='hi'?'अ':'A'}</span><strong>${name}</strong><small>${desc}</small>${profile.language===id?`<span class="selection-tick">${icon('check')}</span>`:''}</button>`).join('')}</div><div class="help-card"><span>अ</span><p>${t('languageNote')}</p></div>`;}
function startChoices(){
 return `<section class="setup-group"><h2>${t('genderLabel')}</h2><div class="choice-grid gender-choices" role="group" aria-label="${t('genderLabel')}">${[['male','male'],['female','female']].map(([id,key])=>`<button class="choice-card ${profile.gender===id?'selected':''}" data-gender="${id}" aria-pressed="${profile.gender===id}"><span class="choice-icon" aria-hidden="true">${icon('user')}</span><strong>${t(key)}</strong><small>${t('sampleGenderHint')}</small>${profile.gender===id?`<span class="selection-tick">${icon('check')}</span>`:''}</button>`).join('')}</div><p class="muted-note">${t('genderOptional')}</p></section><section class="setup-group setup-language"><h2>${profile.language==='hi'?'भाषा':'Language'}</h2>${languageChoices()}</section><button class="text-button start-details" data-step="3">${t('startDetails')} ${icon('arrow-right')}</button><button id="use-demo" class="demo-button">${t('demo')}</button>`;
}
function designCategory(item){
 if(item.category?.includes('Contemporary'))return 'contemporary';
 if(item.category?.includes('Regional'))return 'regional';
 if(item.category?.includes('Traditional / Cultural'))return 'cultural';
 return 'originals';
}
function designChoices(){
 const groups=['all','contemporary','regional','cultural','originals'];
 const designs=config.templates.filter(d=>!d.retired&&(step===9&&spotlight||designFilter==='all'||designCategory(d)===designFilter));
 return `<div class="design-library"><div class="design-filters" role="group" aria-label="${t('designCategories')}">${groups.map(id=>`<button class="design-filter" data-design-filter="${id}" aria-pressed="${designFilter===id}">${t('category_'+id)}</button>`).join('')}</div><p class="library-caption">${t(hasContent()?'yourDetailsInDesigns':'sampleDesigns')}</p><div class="design-grid">${designs.map(item=>`<button class="design-card ${profile.template===item.id?'selected':''}" data-template="${item.id}" aria-pressed="${profile.template===item.id}"><div class="design-thumbnail" data-thumbnail="${item.id}" data-state="loading" aria-hidden="true"><img alt="" width="300" height="424" hidden><span class="thumbnail-note">${t('previewLoading')}</span></div><div class="design-card-title"><strong>${esc(profile.language==='hi'?item.hi:item.name)}</strong></div><div class="design-card-meta"><small>${esc(item.designSubtitle||t('category_'+designCategory(item)))}</small><span class="selected-label" ${profile.template===item.id?'':'hidden'}>${icon('check')} ${t('selectedDesign')}</span></div></button>`).join('')}</div></div>`;
}
function fieldVisibility(id,name){
 if(mobile?.active)return '';
 const excluded=profile.hiddenFields.includes(id);
 return `<button type="button" class="field-toggle" data-field-visibility="${esc(id)}" data-field-name="${esc(name)}" aria-label="${esc(name)}: ${t(excluded?'restoreBiodata':'removeBiodata')}" title="${t(excluded?'restoreBiodata':'removeBiodata')}">${icon(excluded?'eye':'eye-off')}<span>${t(excluded?'addBack':'remove')}</span></button>`;
}
function fieldMarkup(section,field,entry,index){
 const id=`${section.key}.${index}.${field.key}`, value=entry[field.key]||'', isArea=field.type==='textarea'&&(section.key!=='family'||value.includes('\n')||value.length>200);
 if(section.key==='about'&&field.key==='interests')return hobbiesMarkup(id,value);
 const hint=field.key==='height'?t('heightHelp'):field.key==='introduction'?t('aboutHelp'):field.key==='income'?t('incomeHelp'):field.sensitive?t('sensitiveHelp'):'';
 const placeholder=section.key==='family'?t('family_'+field.key):field.key==='name'?(profile.language==='hi'?'जैसे, आरव मेहता':'e.g. Aarav Mehta'):field.key==='height'?'178 cm':field.key==='introduction'?(profile.language==='hi'?'आपके स्वभाव, खुशियों और मूल्यों के बारे में…':'What brings you joy? What do you value? What does a good weekend look like?'):'';
 return `<div class="field ${profile.hiddenFields.includes(id)?'field-excluded':''} ${isArea||section.key==='family'&&field.key==='siblings'?'wide':''}"><div class="field-heading"><label for="${id}">${esc(label(field))}${field.sensitive?`<span class="sensitive-tag">${t('optional')}</span>`:''}</label>${fieldVisibility(id,label(field))}</div>${isArea?`<textarea id="${id}" data-field="${id}" aria-describedby="${id}-error${hint?' '+id+'-hint':''}" maxlength="${field.limit}" placeholder="${esc(placeholder)}" rows="${field.key==='introduction'?5:3}">${esc(value)}</textarea>`:`<input id="${id}" data-field="${id}" aria-describedby="${id}-error${hint?' '+id+'-hint':''}" type="${field.type==='textarea'?'text':field.type}" enterkeyhint="next" value="${esc(value)}" maxlength="${field.limit}" ${field.type==='number'?'min="18" max="120" inputmode="numeric"':''} ${field.type==='email'?'autocomplete="email"':field.type==='tel'?'autocomplete="tel"':section.key==='personal'&&field.key==='name'?'autocomplete="name"':''} placeholder="${esc(placeholder)}">`}${hint?`<p class="field-hint" id="${id}-hint">${esc(hint)}</p>`:''}<p class="inline-error" id="${id}-error" hidden></p></div>`;
}
function hobbiesMarkup(id,value){
 const chosen=selectedHobbies(value),extra=chosen.filter(v=>!hobbies.some(h=>h[0]===v));
 const choices=[...hobbies.map(h=>h[0]),...extra];
 return `<div class="field wide hobby-field ${profile.hiddenFields.includes(id)?'field-excluded':''}"><div class="hobby-heading"><span id="hobby-label">${t('hobbiesLabel')}</span><span id="hobby-count" role="status">${chosen.length} / 5</span>${fieldVisibility(id,t('hobbiesLabel'))}</div><p class="field-hint" id="hobby-help">${t('hobbiesHelp')}</p><div class="hobby-options" role="group" aria-labelledby="hobby-label" aria-describedby="hobby-help">${choices.map(v=>`<button class="hobby-chip" data-hobby="${esc(v)}" aria-pressed="${chosen.includes(v)}" ${chosen.length>=5&&!chosen.includes(v)?'disabled':''}>${chosen.includes(v)?icon('check'):''}${esc(hobbyLabel(v,profile.language))}</button>`).join('')}</div><div class="custom-hobby"><label class="sr-only" for="custom-hobby">${t('customHobby')}</label><input id="custom-hobby" maxlength="80" placeholder="${t('customHobby')}" ${chosen.length>=5?'disabled':''}><button class="button secondary" id="add-hobby" ${chosen.length>=5?'disabled':''}>${t('addHobby')}</button></div></div>`;
}
function updateHobbies(values,focusValue){
 profile.sections.about.interests=hobbyText(values,profile.language);change();
 const container=document.querySelector('.hobby-field');container.outerHTML=hobbiesMarkup('about.0.interests',profile.sections.about.interests);
 const button=[...document.querySelectorAll('[data-hobby]')].find(b=>b.dataset.hobby===focusValue);
 (button||$('custom-hobby'))?.focus({preventScroll:true});
}
function addCustomHobby(){
 const value=$('custom-hobby').value.trim(),chosen=selectedHobbies(profile.sections.about.interests);
 if(!value||value.length>80||chosen.length>=5)return;
 const normalized=selectedHobbies(value);
 if(normalized.length!==1){toast(t('oneHobby'));return;}
 if(!chosen.includes(normalized[0]))chosen.push(normalized[0]);
 updateHobbies(chosen,normalized[0]);
}
function optionalEditor(key,hint=t('optionalGroup')){
 const spec=config.sections.find(s=>s.key===key);
 return disclosure(key,title(spec),sectionEditor(key),disclosureState.get(key)??sectionHasDetails(key),hint);
}
function entryName(key,entry,i){return entry.degree||entry.role||entry.institution||entry.company||`${t('newEntry')} ${i+1}`;}
function sectionEditor(key){
 const spec=config.sections.find(s=>s.key===key),hidden=profile.hiddenSections.includes(key),value=profile.sections[key];
 const entries=spec.repeat?value:[value];
 const grid=(fields,entry,i)=>`<div class="field-grid">${fields.map(f=>fieldMarkup(spec,f,entry,i)).join('')}</div>`;
 return `<section class="section-editor" data-section="${key}"><div class="section-editor-header"><h2>${title(spec)}</h2><label class="hide-section"><input type="checkbox" data-hide="${key}" ${hidden?'checked':''}>${t('hide')}</label></div><p class="muted-note section-hidden-note" ${hidden?'':'hidden'}>${t('sectionHidden')}</p>${entries.map((entry,i)=>{
 let fields;
 if(key==='personal')fields=personalGroups.map(g=>{const markup=grid(spec.fields.filter(f=>g.fields.includes(f.key)),entry,i);return g.optional?disclosure(g.key,t(g.title),markup,disclosureState.get(g.key)??g.fields.some(k=>entry[k]),t('optionalGroup')):`<div class="field-group"><h3>${t(g.title)}</h3>${markup}</div>`;}).join('');
 else if(key==='career')fields=grid(spec.fields.filter(f=>!['income','description'].includes(f.key)),entry,i)+disclosure(`work-${i}`,profile.language==='hi'?'काम और आय के बारे में और':'More about your work & income',grid(spec.fields.filter(f=>['income','description'].includes(f.key)),entry,i),disclosureState.get(`work-${i}`)??Boolean(entry.income||entry.description),t('optionalGroup'));
 else fields=grid(spec.fields,entry,i);
 if(!spec.repeat)return fields;
 return `<details class="entry-card" data-entry="${key}:${i}" ${(activeEntries.get(key)??0)===i?'open':''}><summary><span><small>${title(spec)} ${i+1}</small><strong class="entry-name">${esc(entryName(key,entry,i))}</strong></span><span class="disclosure-chevron" aria-hidden="true">${icon('plus')}</span></summary><div class="entry-content">${fields}<div class="entry-actions"><button class="text-button" data-move-entry="${key}:${i}:-1" ${i===0?'disabled':''}>${icon('arrow-up')} ${t('moveUp')}</button><button class="text-button" data-move-entry="${key}:${i}:1" ${i===entries.length-1?'disabled':''}>${icon('arrow-down')} ${t('moveDown')}</button><button class="remove-entry" data-remove-entry="${key}:${i}">${t('remove')}</button></div></div></details>`;
 }).join('')}${spec.repeat&&entries.length<12?`<button class="add-entry" data-add-entry="${key}">${icon('plus')} ${t(key==='education'?'addEducation':'addCareer')}</button>`:''}</section>`;
}
function customEditor(){return `<div class="section-divider"></div><h3>${t('custom')}</h3><p class="muted-note">${t('customHint')}</p>${profile.customSections.map(s=>`<section class="custom-editor"><div class="section-editor-header"><label class="hide-section"><input type="checkbox" data-hide="${s.id}" ${profile.hiddenSections.includes(s.id)?'checked':''}>${t('hide')}</label><button class="remove-entry" data-remove-custom="${s.id}">${t('remove')}</button></div><label class="field"><span class="muted-note">${t('sectionName')}</span><input class="custom-title" aria-label="${t('sectionName')}" data-custom-title="${s.id}" value="${esc(s.title)}" maxlength="120"></label>${s.fields.map((f,i)=>`<div class="custom-row"><div class="field-grid"><div class="field ${profile.hiddenFields.includes(`${s.id}.${i}`)?'field-excluded':''}"><div class="field-heading"><label for="${s.id}-label-${i}">${t('fieldName')}</label>${fieldVisibility(`${s.id}.${i}`,f.label||t('fieldName'))}</div><input id="${s.id}-label-${i}" data-custom="${s.id}:${i}:label" value="${esc(f.label)}" maxlength="120"></div><div class="field ${profile.hiddenFields.includes(`${s.id}.${i}`)?'field-excluded':''}"><div class="field-heading"><label for="${s.id}-value-${i}">${t('fieldValue')}</label>${fieldVisibility(`${s.id}.${i}`,f.label||t('fieldValue'))}</div><textarea id="${s.id}-value-${i}" data-custom="${s.id}:${i}:value" maxlength="3000" rows="2">${esc(f.value)}</textarea></div></div><div class="entry-header"><button class="remove-entry" data-remove-field="${s.id}:${i}">${t('remove')}</button></div></div>`).join('')}${s.fields.length<12?`<button class="add-entry" data-add-field="${s.id}">${t('addField')}</button>`:''}</section>`).join('')}<button id="add-custom" class="add-entry" ${profile.customSections.length>=8?'disabled':''}>${t('addSection')}</button>`;}
function photosEditor(){return `<label class="hide-section"><input type="checkbox" data-hide="photos" ${profile.hiddenSections.includes('photos')?'checked':''}>${t('hidePhotos')}</label><div class="photo-grid">${profile.photos.map((photo,i)=>`<div class="photo-card"><img src="${photo}" alt="${t('photos')} ${i+1}">${i===0?`<span class="photo-badge">${t('photoPrimary')}</span>`:''}<div class="photo-actions"><button data-crop="${i}">${t('edit')}</button><button data-replace-photo="${i}">${t('replacePhoto')}</button><button data-remove-photo="${i}">${t('remove')}</button></div>${i>0?`<button data-main-photo="${i}">${t('makeMain')}</button>`:''}</div>`).join('')}</div>${profile.photos.length<5?`<button id="add-photo" class="upload-card"><span aria-hidden="true">${icon('image')}</span><strong>${t('upload')}</strong><small>${t('uploadNote')}</small></button>`:''}<p class="muted-note">${t('photoPrivate')}</p><div class="help-card"><span aria-hidden="true">${icon('image')}</span><p>${t('photoTip')}</p></div>`;}
function exportEditor(){
 const doc=buildDocument(profile),theme=config.templates.find(x=>x.id===profile.template);
 const option=kind=>`<button class="export-option" data-export="${kind}" disabled><span class="file-icon">${icon('file')}<span>${kind.toUpperCase()}</span></span><span><strong>${t(kind)}</strong><small>${t(kind+'Note')}</small></span><span class="arrow">${icon('download')}</span></button>`;
 return `<section class="export-review"><h2>${t('reviewDetails')}</h2><p>${esc(profile.language==='hi'?theme.hi:theme.name)} · ${profile.language==='hi'?'हिन्दी':'English'}</p><ul class="review-list">${[...(doc.name&&!doc.sections.some(x=>x.key==='personal')?[{key:'personal',title:t('details')}]:[]),...doc.sections,...(doc.photos.length?[{key:'photos',title:t('photos')+' · '+doc.photos.length}]:[])].map(section=>`<li><span>${esc(section.title)}</span><button class="text-button" data-step="${sectionSteps[section.key]??7}">${t('editSection')}<span class="sr-only"> ${esc(section.title)}</span> ${icon('arrow-right')}</button></li>`).join('')}</ul>${!doc.name&&!doc.sections.length?`<p class="muted-note">${t('noExportDetails')}</p><button class="button secondary" data-step="3">${t('startDetails')}</button>`:''}<button class="button secondary" data-open-preview>${t('reviewPreview')} ${icon('eye')}</button></section><div class="disclosure">${t('disclosure')}</div><label class="consent-row"><input type="checkbox" id="export-consent">${t('consent')}</label><p class="format-label">${t('recommendedPDF')}</p>${option('pdf')}${profile.template==='figma-ganesha-maroon'?`<button class="export-option" data-export="pdf" data-paper="light" disabled>${icon('file')}<span><strong>${profile.language==='hi'?'हल्के कागज़ पर PDF':'Light-paper PDF'}</strong><small>${profile.language==='hi'?'आइवरी कागज़, मैरून लिखावट':'Ivory paper with maroon text. Uses less ink.'}</small></span></button>`:''}${disclosure('image-formats',t('imageFormats'),option('jpg')+option('png'))}<div id="export-status" role="status" aria-live="polite"></div><div id="export-result" tabindex="-1" hidden><div class="message success" role="status">${t('downloadReady')}</div><p id="download-filename" class="download-filename"></p><div class="dialog-actions"><button id="download-again" class="button secondary">${t('downloadAgain')}</button><button id="share-file" class="button primary">${t('share')}</button></div><div id="share-help" class="help-card share-help" tabindex="-1" hidden><div><h3>${t('shareHelpTitle')}</h3><ol><li>${t('shareHelpOne')}</li><li>${t('shareHelpTwo')}</li><li>${t('shareHelpThree')}</li></ol><p>${t('shareImageHelp')}</p></div></div></div><p class="muted-note">${t('shareHint')}</p><p class="muted-note">${t('multiPage')}</p><button class="text-button" data-step="9">${icon('arrow-left')} ${t('changeDesign')}</button>`;
}
function placePreview(){
 const slot=step===9&&spotlight?$('spotlight-stage'):null;
 if(!$('preview-dialog').open){if(slot)slot.append($('preview-panel'));else previewHome.after($('preview-panel'));}
}
function centerSelectedDesign(){
 if(step!==9||!spotlight)return;
 const rail=document.querySelector('.design-grid'),card=rail?.querySelector('.selected');
 if(card){const vertical=getComputedStyle(rail).display==='grid';rail.scrollTo(vertical?{top:card.offsetTop-rail.offsetTop-(rail.clientHeight-card.clientHeight)/2,behavior:'instant'}:{left:card.offsetLeft-rail.offsetLeft-(rail.clientWidth-card.clientWidth)/2,behavior:'instant'});}
}
function renderStep(focus=false){
 if(mobile?.active){
  if(!$('preview-dialog').open)previewHome.after($('preview-panel'));
  spotlight=false;document.body.classList.remove('spotlight-mode');document.body.classList.toggle('design-stage',step===9);
  history.replaceState({...history.state,section:step},'',`#section-${step}`);
  translatePage();renderNav();error('');mobile.render();updateKeyHints();
  if(focus){$('step-content').querySelector('h1')?.focus({preventScroll:true});window.scrollTo(0,0);}
  renderPreview();updateStatus();return;
 }

 // Move the shared pane out before replacing the stage that may contain it.
 if(!$('preview-dialog').open)previewHome.after($('preview-panel'));
 document.body.classList.toggle('spotlight-mode',step===9&&spotlight);
 history.replaceState({...history.state,section:step},'',`#section-${step}`);
 document.body.classList.toggle('design-stage',step===1||step===9);
 const focused=document.activeElement,focusKey=focused?.dataset.template?'[data-template="'+focused.dataset.template+'"]':focused?.dataset.gender?'[data-gender="'+focused.dataset.gender+'"]':focused?.dataset.language?'[data-language="'+focused.dataset.language+'"]':null;
 translatePage();renderNav();error('');
 let content='';
 if(step===0)content=startChoices();
 if(step===1||step===9)content=(step===9&&spotlight?'<div id="spotlight-stage"></div>':'')+designChoices();
 if(step===3)content=sectionEditor('personal')+`<button class="text-button" data-birth-shortcut>${t('birthShortcut')} ${icon('arrow-right')}</button>`+optionalEditor('contact',t('contactHint'));
 if(step===4)content=sectionEditor('education')+sectionEditor('career');
 if(step===5)content=sectionEditor('family');
 if(step===6)content=sectionEditor('culture')+sectionEditor('astrology');
 if(step===7)content=sectionEditor('about')+optionalEditor('partner');
 if(step===8)content=photosEditor();
 if(step===7)content+=disclosure('custom',t('custom'),customEditor(),disclosureState.get('custom')??profile.customSections.length>0,t('customHint'));
 if(step===10)content=exportEditor();
 $('step-content').innerHTML=heading()+(step===9?`<button id="spotlight-toggle" class="button secondary design-mode-toggle" aria-pressed="${spotlight}">${t(spotlight?'galleryMode':'spotlightMode')}</button>`:'')+content;
 placePreview();
 $('step-content').querySelector('h1').tabIndex=-1;
 updateKeyHints();
 document.querySelectorAll('[data-disclosure]').forEach(el=>el.addEventListener('toggle',()=>disclosureState.set(el.dataset.disclosure,el.open)));
 document.querySelectorAll('[data-entry]').forEach(el=>el.addEventListener('toggle',()=>{if(el.open){const [key,i]=el.dataset.entry.split(':');activeEntries.set(key,Number(i));}}));
 $('back').disabled=step===0;$('skip').hidden=step>=9;$('next').hidden=step===10;
 $('next').innerHTML=`<span>${step===9?t('nextExport'):t('continue')}</span>${icon('arrow-right')}`;
 if(focus){$('step-content').querySelector('h1').focus({preventScroll:true});document.querySelector('.editor-main').scrollTo({top:0,behavior:'instant'});window.scrollTo({top:0,behavior:'instant'});}
 if(!focus&&focusKey)$('step-content').querySelector(focusKey)?.focus({preventScroll:true});
 renderPreview();updateStatus();syncMobileAction();scrollSelectedCategory();requestAnimationFrame(()=>{centerSelectedDesign();scalePreview();});
}
function buildDocument(p){
 const result=[], lang=p.language, hidden=new Set(p.hiddenFields);
 for(const spec of config.sections){
  if(p.hiddenSections.includes(spec.key))continue;
  const entries=spec.repeat?p.sections[spec.key]:[p.sections[spec.key]];
  const groups=entries.map((entry,i)=>spec.fields.filter(f=>entry[f.key]&&!hidden.has(`${spec.key}.${i}.${f.key}`)&&!(spec.key==='personal'&&f.key==='name')).map(f=>({label:f.label[lang],value:entry[f.key],prose:f.type==='textarea'}))).filter(g=>g.length);
  if(groups.length)result.push({key:spec.key,title:spec.title[lang],groups});
 }
 for(const s of p.customSections){
  if(p.hiddenSections.includes(s.id))continue;
  const rows=s.fields.filter((f,i)=>f.value&&!hidden.has(`${s.id}.${i}`)).map(f=>({label:f.label,value:f.value,prose:false}));
  if(rows.length)result.push({key:s.id,title:s.title||(lang==='en'?'More about me':'अन्य विवरण'),groups:[rows]});
 }
 return {name:!p.hiddenSections.includes('personal')&&!hidden.has('personal.0.name')?p.sections.personal.name||'':'',sections:result,photos:p.hiddenSections.includes('photos')?[]:p.photos,language:lang,template:p.template,eyebrow:lang==='en'?'A personal introduction':'एक व्यक्तिगत परिचय'};
}
let previewRequest=0;
async function renderPreview(){
 if(!studio)return;
 // Refresh the selected document on every step and at every viewport size.
 // The mobile viewer must already reflect edits when it opens.
 const request=++previewRequest,library=step===1||step===9;
 let payload=exportPayload();
 if(library&&!hasContent()){try{payload=exportPayload(await sampleProfile());}catch{if(request===previewRequest)toast(t('samplePhotoError'));}}
 if(request!==previewRequest)return;
 studio.update(payload,{render:true,library,sample:library&&!hasContent()});
}
function scalePreview(){
 mobile?.paint();
 const panel=$('preview-panel');if(getComputedStyle(panel).display==='none')return;
 const scroll=panel.querySelector('.preview-scroll'),modal=$('preview-dialog').open;
 let second=$('spotlight-next-page');
 if(!second){second=document.createElement('div');second.id='spotlight-next-page';second.hidden=true;scroll.append(second);}
 const result=studio?.cache.get(studio.selected);
 const spread=spotlight&&step===9&&!modal&&scroll.clientWidth>=580&&result?.ready&&studio.page+1<result.pageCount;
 second.hidden=!spread;
 const count=spread?2:1;
 let width=previewZoom&&modal?794:mobile?.active&&modal?Math.min(794,Math.max(1,scroll.clientWidth-16)):Math.min(794,Math.max(1,(scroll.clientWidth-16-(spread?24:0))/count),Math.max(1,scroll.clientHeight-16)*210/297);
 $('preview-scale').style.width=`${width}px`;
 $('preview-scale').style.height=`${width*297/210}px`;
 if(spread){
  mountPreviewPage(second,result,studio.page+1);
  second.style.width=`${width}px`;second.style.height=`${width*297/210}px`;
  second.setAttribute('aria-label',t('pageOf').replace('{page}',studio.page+2).replace('{total}',result.pageCount));
 }
 if(result?.ready)$('preview-page-number').textContent=t('pageOf').replace('{page}',spread?`${studio.page+1}–${studio.page+2}`:studio.page+1).replace('{total}',result.pageCount);
}

function goTo(index,push=true){
 const target=normalizeStep(index);
 mobile?.beforeNavigate();
 if(push&&target!==step)history.pushState({section:target,...(mobile?.active?{mobileDepth:(history.state?.mobileDepth||0)+1}:{})},'',`#section-${target}`);
 step=target;visited.add(step);savedFile=null;renderStep(true);save();
}
window.addEventListener('popstate',()=>{
 const match=location.hash.match(/^#section-(\d+)$/);if(!match)return;
 if(!history.state?.preview&&$('preview-dialog').open)$('preview-dialog').close();
 if(Number(match[1])!==step)goTo(Number(match[1]),false);
 if(history.state?.preview&&!$('preview-dialog').open)openPreview(false);
 if(mobile?.active)mobile.handlePop();
});
function syncMobileAction(){ if(mobile?.active){mobile.sync();return;} const button=$('mobile-next');button.disabled=step===10&&(!$('export-consent')?.checked||exporting);button.setAttribute('aria-busy',String(exporting&&step===10));button.textContent=step===10?t(exporting?'loading':'pdf'):step===9?t('nextExport'):t('continue'); }
function showFieldError(el){
 const key=el.dataset.field?.split('.').at(-1),message=fieldError(key,el.value,t);
 el.setCustomValidity(message);el.setAttribute('aria-invalid',String(Boolean(message)));
 const note=$(el.id+'-error');if(note){note.textContent=message;note.hidden=!message;}
 return message;
}
function focusField(el){
 for(let parent=el.parentElement;parent;parent=parent.parentElement)if(parent.tagName==='DETAILS')parent.open=true;
 el.focus();el.scrollIntoView({block:'center',behavior:'instant'});
}
function validateCurrent(){
 if(mobile?.active&&!mobile.validateHeight())return false;
 const invalid=[...$('step-content').querySelectorAll('[data-field]')].filter(el=>showFieldError(el));
 if(invalid.length){error(t('checkFields'));focusField(invalid[0]);return false;}return true;
}
function validateForExport(){
 const payload=exportPayload();
 for(const spec of config.sections){const rows=spec.repeat?payload.sections[spec.key]:[payload.sections[spec.key]];
  for(let i=0;i<rows.length;i++)for(const field of spec.fields){if(fieldError(field.key,rows[i][field.key]||'',t)){
   if(spec.repeat)activeEntries.set(spec.key,i);goTo(sectionSteps[spec.key]);const el=mobile?.active?mobile.reveal(spec.key,i,field.key):$(`${spec.key}.${i}.${field.key}`);showFieldError(el);error(t('checkFields'));focusField(el);return false;
  }}
 }
 const doc=buildDocument(profile);if(!doc.name&&!doc.sections.length){error(t('noExportDetails'));$('form-error').scrollIntoView({block:'center'});return false;}
 return true;
}
function removeSafely(hasValue,action){if(hasValue)confirmAction('removeTitle','removeBody','remove',action);else action();}
function focusEntry(key,i){const el=document.querySelector(`[data-entry="${key}:${i}"]`);if(el){el.open=true;el.querySelector('[data-field]')?.focus();}}

function toggleList(key,value,add){profile[key]=profile[key].filter(x=>x!==value);if(add)profile[key].push(value);change();}
function openInfo(html){$('dialog-content').innerHTML=html;$('info-dialog').showModal();}
function confirmAction(titleKey,bodyKey,buttonKey,action){openInfo(`<h2>${t(titleKey)}</h2><p>${t(bodyKey)}</p><div class="dialog-actions"><button id="confirm-cancel" class="button secondary">${t('cancel')}</button><button id="confirm-action" class="button ${['remove','clearConfirm'].includes(buttonKey)?'destructive':'primary'}">${t(buttonKey)}</button></div>`);$('confirm-cancel').onclick=()=>$('info-dialog').close();$('confirm-action').onclick=async()=>{$('confirm-action').disabled=true;try{await action();$('info-dialog').close();requestAnimationFrame(()=>{if(document.activeElement===document.body)$('step-content').querySelector('h1')?.focus({preventScroll:true});});}catch{toast(t('savedError'));$('confirm-action').disabled=false;}};}
function downloadBlob(blob,name){const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);}
function showPrivacy(){openInfo(`<h2>${t('privacyTitle')}</h2><p>${t('privacyBody')}</p><p>${t('privacyExport')}</p><p>${t('privacyThird')}</p>`);}
function togglePreview(){
 if($('preview-dialog').open){closePreview();return;}
 openPreview();
}
function closePreview(){
 // The history transition dismisses the popup. Never launch a delayed Back
 // from its close event, which could interrupt the user's next navigation.
 if(history.state?.preview)history.back();else $('preview-dialog').close();
}
function openPreview(push=true){
 const dialog=$('preview-dialog'),panel=$('preview-panel');
 if(push)history.pushState({section:step,preview:true,...(mobile?.active?{mobileDepth:(history.state?.mobileDepth||0)+1}:{})},'',location.href);
 previewFocus=document.activeElement;
 previewZoom=false;
 dialog.append(panel);
 const documentRegion=panel.querySelector('.preview-scroll');documentRegion.tabIndex=0;documentRegion.setAttribute('role','region');documentRegion.setAttribute('aria-label',t('preview'));
 document.body.classList.add('preview-open');
 $('expand-preview').innerHTML=icon('x');
 dialog.showModal();$('expand-preview').focus();renderPreview();
 translatePage();requestAnimationFrame(()=>{scalePreview();document.fonts.ready.then(scalePreview);});
}
$('preview-dialog').addEventListener('keydown',event=>{
 if(event.key!=='Tab'||event.ctrlKey||event.altKey||event.metaKey)return;
 const controls=[...event.currentTarget.querySelectorAll('button:not([disabled]),select:not([disabled]),[tabindex="0"]')].filter(el=>el.getClientRects().length);
 if(!controls.length)return;
 event.preventDefault();
 const index=controls.indexOf(document.activeElement),next=(index+(event.shiftKey?-1:1)+controls.length)%controls.length;
 controls[next].focus();
});
$('preview-dialog').addEventListener('close',()=>{
 if($('preview-dialog').open)return; // Ignore a queued close after rapid Forward.
 placePreview();$('preview-panel').querySelector('.preview-scroll').tabIndex=-1;
 document.body.classList.remove('preview-open');
 previewZoom=false;
 $('preview-zoom').setAttribute('aria-pressed','false');
 $('expand-preview').textContent=t('readPreview');
 translatePage();requestAnimationFrame(()=>{scalePreview();document.fonts.ready.then(scalePreview);});previewFocus?.focus({preventScroll:true});
});
$('preview-dialog').addEventListener('cancel',event=>{event.preventDefault();closePreview();});
$('preview-dialog').addEventListener('click',event=>{
 if(event.target!==$('preview-dialog'))return;
 const r=$('preview-dialog').getBoundingClientRect();
 if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)closePreview();
});
$('preview-zoom').onclick=()=>{
 previewZoom=!previewZoom;$('preview-zoom').setAttribute('aria-pressed',String(previewZoom));translatePage();scalePreview();
};
$('section-jump').onchange=event=>goTo(Number(event.target.value));

// One event path for reusable field components, including entries added at runtime.
function updateKeyHints(){
 const fields=[...$('step-content').querySelectorAll('[data-field]')].filter(el=>el.getClientRects().length);
 fields.forEach((el,i)=>el.setAttribute('enterkeyhint',i===fields.length-1?'done':'next'));
}
$('step-content').addEventListener('toggle',updateKeyHints,true);
$('step-content').addEventListener('input',event=>{
 const el=event.target;
 if(el.dataset.field){const [key,i,name]=el.dataset.field.split('.');const spec=config.sections.find(s=>s.key===key);(spec.repeat?profile.sections[key][Number(i)]:profile.sections[key])[name]=mobile?.active?mobile.inputValue(el):el.value;if(spec.repeat){const summary=el.closest('[data-entry]')?.querySelector('.entry-name');if(summary)summary.textContent=entryName(key,profile.sections[key][Number(i)],Number(i));}if(el.getAttribute('aria-invalid')==='true')showFieldError(el);change();}
 if(el.dataset.customTitle){profile.customSections.find(s=>s.id===el.dataset.customTitle).title=el.value;change();}
 if(el.dataset.custom){const [id,i,key]=el.dataset.custom.split(':');profile.customSections.find(s=>s.id===id).fields[Number(i)][key]=el.value;change();}
});
$('step-content').addEventListener('keydown',event=>{
 if(spotlight&&step===9&&event.target.matches('[data-template]')&&['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End'].includes(event.key)){
  event.preventDefault();const cards=[...document.querySelectorAll('[data-template]')],i=cards.indexOf(event.target);
  const next=event.key==='Home'?0:event.key==='End'?cards.length-1:Math.max(0,Math.min(cards.length-1,i+({ArrowRight:1,ArrowLeft:-1,ArrowDown:2,ArrowUp:-2}[event.key]||0)));
  cards[next].focus({preventScroll:true});cards[next].scrollIntoView({block:'nearest',inline:'center',behavior:'instant'});return;
 }
 if(event.key==='Enter'&&event.target.id==='custom-hobby'&&!event.isComposing){event.preventDefault();addCustomHobby();return;}
 if(event.key!=='Enter'||event.isComposing||event.ctrlKey||event.altKey||event.metaKey||!event.target.matches('input[data-field]:not([type=date]):not([type=time])'))return;
 const fields=[...$('step-content').querySelectorAll('[data-field]')].filter(el=>el.getClientRects().length),index=fields.indexOf(event.target);
 event.preventDefault();if(showFieldError(event.target))return;
 if(fields[index+1])focusField(fields[index+1]);else event.target.blur();
});
$('step-content').addEventListener('focusout',event=>{if(event.target.dataset.field)showFieldError(event.target);});
$('step-content').addEventListener('change',event=>{
 const el=event.target;
 if(el.dataset.hide){toggleList('hiddenSections',el.dataset.hide,el.checked);const note=el.closest('[data-section]')?.querySelector('.section-hidden-note');if(note)note.hidden=!el.checked;renderPreview();}
 if(el.id==='export-consent'){document.querySelectorAll('[data-export]').forEach(b=>b.disabled=!el.checked||exporting);syncMobileAction();}
});
document.addEventListener('click',async event=>{
 const b=event.target.closest('button');if(!b)return;
 if(b.dataset.step!==undefined)goTo(Number(b.dataset.step));
 if(b.hasAttribute('data-birth-shortcut')){disclosureState.set('astrology',true);goTo(6);focusField($('astrology.0.birthDate'));}
 if(b.id==='spotlight-toggle'){spotlight=!spotlight;renderStep();$('spotlight-toggle').focus({preventScroll:true});}
 if(b.dataset.designFilter){designFilter=b.dataset.designFilter;renderStep();document.querySelector(`[data-design-filter="${designFilter}"]`)?.focus({preventScroll:true});}
 if(b.dataset.gender){
  const token=++genderChange;profile.gender=b.dataset.gender;change();renderStep();
  if(profile.photos.length){try{
   const [male,female]=await Promise.all([demoPortrait('male'),demoPortrait('female')]);
   if(token!==genderChange)return;
   const replacement=profile.gender==='female'?female:male;
   if(profile.photos.some(p=>(p===male||p===female)&&p!==replacement)){
    profile.photos=profile.photos.map(p=>p===male||p===female?replacement:p);change();renderPreview();
   }
  }catch{toast(t('samplePhotoError'));}}
 }
 if(b.dataset.hobby){const chosen=selectedHobbies(profile.sections.about.interests),value=b.dataset.hobby;if(chosen.includes(value))updateHobbies(chosen.filter(v=>v!==value),value);else if(chosen.length<5)updateHobbies([...chosen,value],value);}
 if(b.id==='add-hobby')addCustomHobby();
 if(b.dataset.template){profile.presentation={sacred_art:'default',direction:'ltr',salutation:false};profile.template=b.dataset.template;change();document.querySelectorAll('[data-template]').forEach(card=>{const selected=card.dataset.template===profile.template;card.classList.toggle('selected',selected);card.setAttribute('aria-pressed',String(selected));card.querySelector('.selected-label').hidden=!selected;});renderPreview();centerSelectedDesign();}
 if(b.dataset.language){profile.language=b.dataset.language;change();renderStep();}
 if(b.hasAttribute('data-open-preview'))togglePreview();
 if(b.dataset.fieldVisibility){
  const id=b.dataset.fieldVisibility,excluded=!profile.hiddenFields.includes(id);
  toggleList('hiddenFields',id,excluded);
  document.querySelectorAll('[data-field-visibility]').forEach(control=>{
   if(control.dataset.fieldVisibility!==id)return;
   control.closest('.field')?.classList.toggle('field-excluded',excluded);
   const focused=document.activeElement===control,name=control.dataset.fieldName;
   control.innerHTML=`${icon(excluded?'eye':'eye-off')}<span>${t(excluded?'addBack':'remove')}</span>`;
   control.setAttribute('aria-label',`${name}: ${t(excluded?'restoreBiodata':'removeBiodata')}`);
   control.title=t(excluded?'restoreBiodata':'removeBiodata');
   if(focused)control.focus({preventScroll:true});
  });
  renderPreview();
 }
 if(b.dataset.addEntry){const key=b.dataset.addEntry,i=profile.sections[key].length;profile.sections[key].push({});activeEntries.set(key,i);change();renderStep();focusEntry(key,i);}
 if(b.dataset.moveEntry){const [key,index,direction]=b.dataset.moveEntry.split(':'),to=Number(index)+Number(direction);moveEntry(profile,key,Number(index),to);activeEntries.set(key,to);change();renderStep();focusEntry(key,to);}
 if(b.dataset.removeEntry){const [key,index]=b.dataset.removeEntry.split(':');removeSafely(Object.values(profile.sections[key][Number(index)]).some(Boolean),()=>{profile.sections[key].splice(Number(index),1);reindexHidden(key,Number(index));activeEntries.set(key,Math.max(0,Number(index)-1));change();renderStep();document.querySelector(`[data-add-entry="${key}"]`)?.focus();});}
 if(b.dataset.hide!==undefined)return;
 if(b.dataset.removeCustom)removeSafely(profile.customSections.some(s=>s.id===b.dataset.removeCustom&&(s.title||s.fields.some(f=>f.label||f.value))),()=>{profile.customSections=profile.customSections.filter(s=>s.id!==b.dataset.removeCustom);profile.hiddenSections=profile.hiddenSections.filter(id=>id!==b.dataset.removeCustom);profile.hiddenFields=profile.hiddenFields.filter(id=>!id.startsWith(b.dataset.removeCustom+'.'));change();renderStep();$('add-custom')?.focus();});
 if(b.dataset.addField){const fields=profile.customSections.find(s=>s.id===b.dataset.addField).fields;fields.push({label:'',value:''});change();renderStep();$(`${b.dataset.addField}-label-${fields.length-1}`)?.focus();}
 if(b.dataset.removeField){const [id,index]=b.dataset.removeField.split(':');removeSafely(Object.values(profile.customSections.find(s=>s.id===id).fields[Number(index)]).some(Boolean),()=>{profile.customSections.find(s=>s.id===id).fields.splice(Number(index),1);reindexHidden(id,Number(index));change();renderStep();});}
 if(b.id==='add-custom'){const id='custom-'+crypto.randomUUID();profile.customSections.push({id,title:'',fields:[{label:'',value:''}]});change();renderStep();document.querySelector(`[data-custom-title="${id}"]`)?.focus();}
 if(b.id==='use-demo')confirmAction('demoTitle','demoBody','demoConfirm',async()=>{profile=await sampleProfile();step=3;revision++;change();renderStep(true);});
 if(b.id==='add-photo'||b.dataset.replacePhoto!==undefined){replacementPhoto=b.dataset.replacePhoto===undefined?-1:Number(b.dataset.replacePhoto);$('photo-input').value='';$('photo-input').click();}
 if(b.dataset.crop!==undefined)openCrop(profile.photos[Number(b.dataset.crop)],Number(b.dataset.crop));
 if(b.dataset.removePhoto!==undefined)removeSafely(true,()=>{profile.photos.splice(Number(b.dataset.removePhoto),1);change();renderStep();$('add-photo')?.focus();});
 if(b.dataset.mainPhoto!==undefined){profile.photos.unshift(profile.photos.splice(Number(b.dataset.mainPhoto),1)[0]);change();renderStep();}
 if(b.dataset.export)await exportFile(b.dataset.export,b.dataset.paper);
 if(b.id==='download-again'&&savedFile)downloadBlob(savedFile,savedFile.name);
 if(b.id==='share-file'&&savedFile){try{if(navigator.canShare?.({files:[savedFile]}))await navigator.share({files:[savedFile],title:'Biodata'});else showShareHelp();}catch(e){if(e.name!=='AbortError')showShareHelp();}}
});
function reindexHidden(section,removed){profile.hiddenFields=profile.hiddenFields.flatMap(id=>{if(!id.startsWith(section+'.'))return[id];const parts=id.split('.'),i=Number(parts[1]);if(i===removed)return[];if(i>removed)parts[1]=String(i-1);return[parts.join('.')];});}
$('next').onclick=()=>{if(validateCurrent())goTo(adjacentStep(1));};
$('mobile-next').onclick=()=>{if(step===10)exportFile('pdf');else $('next').click();};
$('back').onclick=()=>goTo(adjacentStep(-1));$('skip').onclick=()=>goTo(adjacentStep(1));
$('language').onchange=e=>{profile.language=e.target.value;change();renderStep();};
$('mobile-preview').onclick=togglePreview;$('expand-preview').onclick=togglePreview;
function closeDraftMenu(){$('draft-menu').hidden=true;$('more-button').setAttribute('aria-expanded','false');}
 document.addEventListener('pointerdown',event=>{if(!event.target.closest('#draft-menu,#more-button'))closeDraftMenu();});
$('more-button').onclick=()=>{const menu=$('draft-menu');menu.hidden=!menu.hidden;$('more-button').setAttribute('aria-expanded',String(!menu.hidden));};
$('privacy-button').onclick=showPrivacy;$('menu-privacy').onclick=showPrivacy;
 $('storage-backup').onclick=()=>$('backup-button').click();
 $('import-button').onclick=()=>$('import-file').click();
$('backup-button').onclick=()=>{downloadBlob(new Blob([JSON.stringify(profile,null,2)],{type:'application/json'}),'parichay-private-backup.json');closeDraftMenu();};
$('clear-button').onclick=()=>{ closeDraftMenu();confirmAction('clearTitle','clearBody','clearConfirm',async()=>{deleting=true;studio.clear();try{await store?.clear();}catch{deleting=false;throw new Error('Delete failed');}profile=clone(config.empty);mobile?.reset();step=0;visited=new Set([0]);savedFile=null;recoveryBlocked=false;failedStorage=false;revision++;renderStep();updateStatus();deleting=false;});};
document.querySelectorAll('.dialog-close').forEach(b=>b.onclick=()=>b.closest('dialog').close());
document.addEventListener('keydown',event=>{
 if(event.key==='Escape')closeDraftMenu();
});
function scrollSelectedCategory(){const filter=document.querySelector('.design-filter[aria-pressed="true"]');if(filter)filter.parentElement.scrollLeft=filter.offsetLeft-4;}
const stepNavigation=document.querySelector('.mobile-step-navigation');
new ResizeObserver(()=>{document.body.style.setProperty('--step-nav-height',`${stepNavigation.getBoundingClientRect().height}px`);}).observe(stepNavigation);
window.addEventListener('resize',()=>{renderPreview();scalePreview();scrollSelectedCategory();});
 const keyboardState=()=>{
  const viewport=window.visualViewport,editing=document.activeElement?.matches('textarea,input:not([type=checkbox]):not([type=range]):not([type=file])');
  document.body.classList.toggle('keyboard-open',Boolean(editing&&viewport&&viewport.scale<1.05&&innerHeight-viewport.height>150));
 };
 window.visualViewport?.addEventListener('resize',keyboardState);
 document.addEventListener('focusin',keyboardState);document.addEventListener('focusout',()=>requestAnimationFrame(keyboardState));
 // Text enlargement can exhaust the fixed sidebar even at a wide viewport.
 // Reuse the compact workspace instead of clipping or adding a scrolling rail.
 const textProbe=document.createElement('span');textProbe.className='text-size-probe';textProbe.setAttribute('aria-hidden','true');document.body.append(textProbe);
 const textLayout=()=>{document.body.classList.toggle('compact-workspace',textProbe.getBoundingClientRect().height>18);scalePreview();};
 new ResizeObserver(textLayout).observe(textProbe);textLayout();
 window.addEventListener('offline',updateStatus);window.addEventListener('online',updateStatus);
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden')save();});

function showShareHelp(){if(mobile?.active){mobile.shareHelp();return;}const help=$('share-help');help.hidden=false;help.focus({preventScroll:true});help.scrollIntoView({block:'center',behavior:'instant'});}

async function exportFile(kind,paper='original'){
 if(exporting||!$('export-consent')?.checked)return;
 if(!validateForExport())return;
 exporting=true;exportingRevision=revision;$('export-result').hidden=true;document.querySelectorAll('[data-export]').forEach(b=>b.disabled=true);$('export-status').textContent=t('loading');$('step-content').setAttribute('aria-busy','true');syncMobileAction();error('');$('export-status').scrollIntoView({block:'nearest',behavior:'instant'});
 const abort=new AbortController(),timer=setTimeout(()=>abort.abort(),60000);
 try{
  let blob=kind==='pdf'&&paper==='original'?studio.pdf(exportPayload()):null,ext=kind;
  if(!blob){
   const response=await fetch('/api/export/'+kind+'?paper='+encodeURIComponent(paper),{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':document.querySelector('meta[name="csrf-token"]').content},body:JSON.stringify(exportPayload()),signal:abort.signal});
   if(!response.ok){const payload=await response.json().catch(()=>({error:t('errorNetwork')}));throw new Error(payload.error);}
   blob=await response.blob();ext=response.headers.get('Content-Type').includes('zip')?'zip':kind;
  }
  const name=buildDocument(profile).name.normalize('NFC').replace(/[^\p{L}\p{M}\p{N}-]+/gu,'-').replace(/^-|-$/g,'').slice(0,60);
  const file=new File([blob],`parichay${name?'-'+name:''}-biodata${paper==='light'?'-light-paper':''}.${ext}`,{type:blob.type});
  downloadBlob(file,file.name);
  if(revision===exportingRevision&&step===10){savedFile=file;$('export-result').hidden=false;$('download-filename').textContent=file.name;$('export-status').textContent='';$('export-result').focus({preventScroll:true});$('export-result').scrollIntoView({block:'center',behavior:'instant'});mobile?.active&&mobile.completedDownload();}
  else toast(t('downloadReady'));
 }catch(e){if(step===10){error(e.name==='TypeError'||e.name==='AbortError'?t('errorNetwork'):e.message);if($('export-status'))$('export-status').textContent='';const retry=document.createElement('button');retry.className='button secondary';retry.dataset.export=kind;retry.dataset.paper=paper;retry.textContent=t('tryAgain');$('form-error').append(retry);$('form-error').tabIndex=-1;$('form-error').focus({preventScroll:true});$('form-error').scrollIntoView({block:'center',behavior:'instant'});}else toast(t('errorNetwork'));}
 finally{clearTimeout(timer);exporting=false;$('step-content').removeAttribute('aria-busy');syncMobileAction();document.querySelectorAll('[data-export]').forEach(b=>b.disabled=!$('export-consent')?.checked);}
}

// Omit hidden values before transmission, not only before rendering on the server.
function exportPayload(source=profile){
 const p=clone(source);
 p.sections.about.interests=hobbyText(selectedHobbies(p.sections.about.interests),p.language);
 for(const spec of config.sections){
  const entries=spec.repeat?p.sections[spec.key]:[p.sections[spec.key]];
  entries.forEach((row,i)=>spec.fields.forEach(f=>{
   if(p.hiddenSections.includes(spec.key)||p.hiddenFields.includes(`${spec.key}.${i}.${f.key}`))row[f.key]='';
  }));
 }
 p.customSections.forEach(s=>s.fields.forEach((f,i)=>{if(p.hiddenSections.includes(s.id)||p.hiddenFields.includes(`${s.id}.${i}`)){f.label='';f.value='';}}));
 p.customSections=p.customSections.filter(s=>!p.hiddenSections.includes(s.id));
 if(p.hiddenSections.includes('photos'))p.photos=[];
 return p;
}

$('photo-input').onchange=async event=>{
 const file=event.target.files[0];if(!file)return;
 if(!['image/jpeg','image/png','image/webp'].includes(file.type)||file.size>8*1024*1024){error(t('photoTypeError'),true);return;}
 try{
  error('');toast(t('photoReading'));$('add-photo')?.setAttribute('disabled','');
  const bitmap=await createImageBitmap(file);if(bitmap.width*bitmap.height>24_000_000){bitmap.close();throw new Error('Please choose a photo under 24 megapixels.');}
  const lowQuality=bitmap.width<600||bitmap.height<750;
  const scale=Math.min(1,1600/Math.max(bitmap.width,bitmap.height)),canvas=document.createElement('canvas');canvas.width=Math.round(bitmap.width*scale);canvas.height=Math.round(bitmap.height*scale);const ctx=canvas.getContext('2d');ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(bitmap,0,0,canvas.width,canvas.height);bitmap.close();
  openCrop(canvas.toDataURL('image/jpeg',.9),replacementPhoto,lowQuality);
 }catch{error(t('photoError'),true);}finally{$('add-photo')?.removeAttribute('disabled');$('toast').hidden=true;}
};
function openCrop(src,index,lowQuality=false){$('crop-quality').textContent=t('lowPhoto');$('crop-quality').hidden=!lowQuality;cropIndex=index;rotation=0;cropSource=new Image();cropSource.onload=async()=>{
 $('crop-zoom').value='1';$('crop-x').value='0';$('crop-y').value='0';drawCrop();$('crop-dialog').showModal();
 // Optional browser-native detection stays on the device. Unsupported browsers
 // retain manual positioning; document frames contain the entire approved crop.
 if(!('FaceDetector' in window))return;
 const source=cropSource;
 try{const faces=await new FaceDetector({fastMode:true,maxDetectedFaces:1}).detect(source);if(source!==cropSource||!$('crop-dialog').open||rotation!==0||!faces.length||$('crop-zoom').value!=='1'||$('crop-x').value!=='0'||$('crop-y').value!=='0')return;
  const box=faces[0].boundingBox,scale=Math.max(600/source.width,750/source.height),dx=source.width*scale-600,dy=source.height*scale-750;
  const clamp=v=>Math.max(-1,Math.min(1,v));
  if(dx>0)$('crop-x').value=String(clamp((source.width/2-box.x-box.width/2)*scale*2/dx));
  if(dy>0)$('crop-y').value=String(clamp((source.height/2-box.y-box.height/2)*scale*2/dy));
  drawCrop();
 }catch{/* The manual crop remains available. */}
};cropSource.src=src;}
function drawCrop(){if(!cropSource)return;const canvas=$('crop-canvas'),ctx=canvas.getContext('2d'),swap=rotation%180!==0,w=swap?cropSource.height:cropSource.width,h=swap?cropSource.width:cropSource.height,scale=Math.max(600/w,750/h)*Number($('crop-zoom').value);ctx.fillStyle='#fff';ctx.fillRect(0,0,600,750);ctx.save();ctx.translate(300+Number($('crop-x').value)*(w*scale-600)/2,375+Number($('crop-y').value)*(h*scale-750)/2);ctx.rotate(rotation*Math.PI/180);ctx.scale(scale,scale);ctx.drawImage(cropSource,-cropSource.width/2,-cropSource.height/2);ctx.restore();}
['crop-zoom','crop-x','crop-y'].forEach(id=>$(id).oninput=drawCrop);
$('rotate-photo').onclick=()=>{rotation=(rotation+90)%360;drawCrop();};
$('apply-crop').onclick=()=>{const image=$('crop-canvas').toDataURL('image/jpeg',.92);if(cropIndex<0&&profile.photos.length<5)profile.photos.push(image);else if(cropIndex>=0)profile.photos[cropIndex]=image;$('crop-dialog').close();change();renderStep();toast(t(cropIndex<0?'photoAdded':'photoReplaced'));document.querySelector(`[data-crop="${cropIndex<0?profile.photos.length-1:cropIndex}"]`)?.focus();};

function validateBackup(raw){
 raw=migrateProfile(raw);
 if(!raw||raw.schemaVersion!==2||!['en','hi'].includes(raw.language)||!config.templates.some(x=>x.id===raw.template)||!['myself','son','daughter','sibling','relative','client','other'].includes(raw.forWhom))throw new Error(t('invalidBackup'));
 const p=clone(config.empty);if(!['','male','female'].includes(raw.gender??''))throw new Error(t('invalidBackup'));p.gender=raw.gender??'';p.language=raw.language;p.template=raw.template;p.forWhom=raw.forWhom;
 const settings=raw.presentation||{};if(typeof settings!=='object'||Array.isArray(settings)||!['default','none','krishna','ganesha','rama','ambedkar','ik-onkar','khanda','cross','dhamma-wheel'].includes(settings.sacred_art??'default')||!['auto','ltr','rtl'].includes(settings.direction??'auto')||typeof (settings.salutation??false)!=='boolean')throw new Error(t('invalidBackup'));
 const design=config.templates.find(d=>d.id===p.template);
 if(design?.base_template_id===p.template){
  const candidates=config.templates.filter(d=>d.base_template_id===p.template);
  const choice=candidates.some(d=>d.variant_sacred_art===settings.sacred_art)?settings.sacred_art:design.variant_sacred_art;
  const salutation=p.template==='craft-ambedkarite-blue'&&Boolean(settings.salutation);
  p.template=candidates.find(d=>d.variant_sacred_art===choice&&d.variant_salutation===salutation)?.id||p.template;
 }
 p.presentation={sacred_art:'default',direction:'ltr',salutation:false};
 const text=(s,limit)=>{if(typeof s!=='string'||s.length>limit)throw new Error(t('invalidBackup'));return s;};
 for(const spec of config.sections){const input=raw.sections?.[spec.key];const list=spec.repeat?input:[input];if(!Array.isArray(list)||list.length>12)throw new Error(t('invalidBackup'));const values=list.map(row=>{if(!row||typeof row!=='object'||Array.isArray(row))throw new Error(t('invalidBackup'));return Object.fromEntries(spec.fields.map(f=>[f.key,text(row[f.key]??'',f.limit)]));});p.sections[spec.key]=spec.repeat?values:values[0];}
 for(const key of ['hiddenFields','hiddenSections']){if(!Array.isArray(raw[key])||raw[key].length>300)throw new Error(t('invalidBackup'));p[key]=raw[key].map(x=>text(x,120));}
 if(!Array.isArray(raw.customSections)||raw.customSections.length>8)throw new Error(t('invalidBackup'));
 const ids=new Set();p.customSections=raw.customSections.map(s=>{if(!s||!/^custom-[a-zA-Z0-9-]+$/.test(s.id)||s.id.length>60||ids.has(s.id)||!Array.isArray(s.fields)||s.fields.length>12)throw new Error(t('invalidBackup'));ids.add(s.id);return{id:s.id,title:text(s.title,120),fields:s.fields.map(f=>({label:text(f.label,120),value:text(f.value,3000)}))};});
 if(!Array.isArray(raw.photos)||raw.photos.length>5)throw new Error(t('invalidBackup'));p.photos=raw.photos.map(image=>{if(typeof image!=='string'||image.length>12*1024*1024||!/^data:image\/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$/.test(image))throw new Error(t('invalidBackup'));return image;});
 if(JSON.stringify({...p,photos:[]}).length>150000)throw new Error(t('invalidBackup'));
 return p;
}
$('import-file').onchange=async event=>{const file=event.target.files[0];if(!file)return;try{if(file.size>18*1024*1024)throw new Error(t('invalidBackup'));const draft=validateBackup(JSON.parse(await file.text()));confirmAction('restoreTitle','restoreBody','restoreConfirm',()=>{profile=draft;mobile?.reset();step=3;visited=new Set([0,3]);recoveryBlocked=false;change();renderStep(true);});}catch(e){toast(e.message||t('invalidBackup'));}event.target.value='';closeDraftMenu();};

async function initialize(){
 try{store=await openDraftStore();const saved=await store.get();if(saved){mobile?.restore(saved.mobile);profile=validateBackup(saved.profile);step=Number.isInteger(saved.step)?normalizeStep(saved.step):0;visited=new Set(Array.isArray(saved.visited)?saved.visited.filter(i=>Number.isInteger(i)&&i>=0&&i<=10).map(normalizeStep):[0]);}}
 catch{failedStorage=true;recoveryBlocked=Boolean(store);}
 const preferredDesign=new URLSearchParams(location.search).get('design');
 if(config.templates.some(d=>!d.retired&&d.id===preferredDesign))profile.template=preferredDesign;
 const preferredLanguage=new URLSearchParams(location.search).get('lang');
 if(['en','hi'].includes(preferredLanguage))profile.language=preferredLanguage;
 // Refresh restarts the flow, not the draft. Normal return visits and browser
 // Back/Forward still retain their existing navigation behavior.
 const reloading=performance.getEntriesByType('navigation')[0]?.type==='reload';
 const sectionHash=location.hash.match(/^#section-(\d+)$/);
 if(reloading)step=0;else if(sectionHash)step=normalizeStep(Number(sectionHash[1]));
 const entryURL=new URL(location.href);entryURL.searchParams.delete('design');entryURL.searchParams.delete('lang');entryURL.hash=`section-${step}`;
 history.replaceState({section:step,...(isMobileProduct()?{mobileDepth:0}:{})},'',entryURL.pathname+entryURL.search+entryURL.hash);
 restoring=false;renderStep();
 if(reloading)window.scrollTo(0,0);
 if(failedStorage)toast(t('savedError'));
 if(recoveryBlocked){
  openInfo(`<h2>${profile.language==='hi'?'ड्राफ़्ट बहाल नहीं हो सका':'Your saved draft needs attention'}</h2><p>${profile.language==='hi'?'पुराने ड्राफ़्ट को बदला नहीं गया है। पहले उसकी प्रति डाउनलोड करें।':'Your existing draft has not been overwritten. Download a recovery copy before starting again.'}</p><div class="dialog-actions"><button id="recover-copy" class="button secondary">${t('backup')}</button><button id="recover-reset" class="button primary">${profile.language==='hi'?'नया ड्राफ़्ट शुरू करें':'Start a new draft'}</button></div>`);
  $('recover-copy').onclick=async()=>{const raw=await store.get();downloadBlob(new Blob([JSON.stringify(raw)],{type:'application/json'}),'parichay-recovery.json');};
  $('recover-reset').onclick=async()=>{await store.clear();recoveryBlocked=false;failedStorage=false;$('info-dialog').close();updateStatus();};
 }
 document.fonts.ready.then(scalePreview);
}
mobile=createMobileProduct({
 config,profile:()=>profile,step:()=>step,savedFile:()=>savedFile,exporting:()=>exporting,
 status:()=>$('save-status').dataset.state||'ready',previewResult:()=>studio?.cache.get(studio.selected),previewZoom:()=>previewZoom,
 document:()=>buildDocument(profile),hasContent,sectionHasDetails,stepHasDetails:i=>stepHasDetails(i)||i===7&&profile.customSections.some(s=>s.fields.some(f=>f.value)),change,save,goTo,render:renderStep,renderPreview,
 designChoices,hobbiesMarkup,customEditor,validateCurrent,openPreview,closePreview,openCrop,exportFile,reindexHidden,
 clearFile:()=>{savedFile=null;},confirmRemove:action=>removeSafely(true,action),
 replacePhoto:index=>{replacementPhoto=index;$('photo-input').value='';$('photo-input').click();},
 removePhoto:index=>removeSafely(true,()=>{profile.photos.splice(index,1);change();renderStep();}),
 loadSample:()=>confirmAction('demoTitle','demoBody','demoConfirm',async()=>{profile=await sampleProfile();mobile?.reset();step=3;revision++;change();renderStep(true);}),
 breakpoint:()=>{step=normalizeStep(step);spotlight=false;renderStep();}
});
studio=new DocumentStudio({t,templates:config.templates,onPaint:scalePreview});
initialize();
