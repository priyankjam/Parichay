/** IndexedDB stores photos without blocking the main thread or localStorage quotas. */
export function openDraftStore(){
 return new Promise((resolve,reject)=>{
  if(!globalThis.indexedDB){reject(new Error('Storage unavailable'));return;}
  const request=indexedDB.open('parichay-local');
  request.onupgradeneeded=()=>request.result.createObjectStore('drafts');
  request.onerror=()=>reject(request.error);
  request.onblocked=()=>reject(new Error('Storage blocked by another tab'));
  request.onsuccess=()=>{
   const db=request.result;
   db.onversionchange=()=>db.close();
   const operation=(mode,action)=>new Promise((done,fail)=>{
    const tx=db.transaction('drafts',mode),r=action(tx.objectStore('drafts'));
    tx.oncomplete=()=>done(r.result);tx.onerror=()=>fail(tx.error);tx.onabort=()=>fail(tx.error);
   });
   resolve({get:()=>operation('readonly',s=>s.get('current')),put:value=>operation('readwrite',s=>s.put(value,'current')),clear:()=>operation('readwrite',s=>s.delete('current'))});
  };
 });
}
