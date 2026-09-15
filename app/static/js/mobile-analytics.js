/** Optional integration hook. No transport, identifiers, profile values or persistence. */
const events=new Set(['landing_cta','start_completed','section_opened','section_completed','section_skipped','section_abandoned','optional_detail_added','template_selected','preview_opened','review_reached','download_started','download_successful','share_started']);
export function mobileEvent(event,{section,template}={}){
 if(!events.has(event)||!matchMedia('(max-width:767px)').matches)return;
 const detail={event,surface:'mobile'};
 if(Number.isInteger(section)&&section>=0&&section<=10)detail.section=section;
 if(typeof template==='string'&&/^[a-z-]{1,60}$/.test(template))detail.template=template;
 document.dispatchEvent(new CustomEvent('parichay:analytics',{detail:Object.freeze(detail)}));
}
