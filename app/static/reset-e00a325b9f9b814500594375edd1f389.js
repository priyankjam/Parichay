const status=document.getElementById('status');
function open(version){return new Promise((resolve,reject)=>{const r=version?indexedDB.open('parichay-local',version):indexedDB.open('parichay-local');r.onupgradeneeded=()=>{if(!r.result.objectStoreNames.contains('drafts'))r.result.createObjectStore('drafts');};r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);r.onblocked=()=>{status.textContent='Close other Parichay editor tabs to finish clearing this draft.';};});}
try{
 const previous=await open();const version=previous.version+1;previous.close();
 // Upgrading closes old editor connections so stale tabs cannot save the deleted draft again.
 const db=await open(version);
 await new Promise((resolve,reject)=>{const tx=db.transaction('drafts','readwrite');tx.objectStore('drafts').clear();tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);});db.close();
 status.textContent='Your saved biodata and photos have been removed.';
 await fetch('/static/reset-complete-e00a325b9f9b814500594375edd1f389.txt',{cache:'no-store'});
 location.replace('/?fresh=e00a325b9f9b814500594375edd1f389');
}catch{status.textContent='The draft could not be cleared. Please reload this reset page to try again.';}
