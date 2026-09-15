"""Import source artwork from a private, temporary asset URL manifest.
The manifest stays outside the repo; shipped provenance contains hashes, not URLs.
"""
import concurrent.futures, hashlib, io, json, sys, urllib.request
from pathlib import Path
from PIL import Image

def fetch(item):
 name,record=item
 req=urllib.request.Request(record['url'],headers={'User-Agent':'Parichay asset import'})
 with urllib.request.urlopen(req,timeout=60) as r:data=r.read()
 Path('tmp/qa/figma',name).write_bytes(data)
 with Image.open(io.BytesIO(data)) as im:
  im.thumbnail((1800,2600));im=im.convert('RGB')
  target=Path('app/static/artwork',Path(name).stem+'.webp')
  im.save(target,'WEBP',quality=92,method=6)
  return {'asset':target.name,'sourceSha256':hashlib.sha256(data).hexdigest(),'width':im.width,'height':im.height,'bytes':target.stat().st_size}
if __name__=='__main__':
 manifest=json.loads(Path(sys.argv[1]).read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(fetch,manifest.items()))
 Path('app/static/artwork/provenance.json').write_text(json.dumps({'figmaFile':'ZdHTDaQEF4JXKcir1B7xsj','assets':records},indent=2))
 print(json.dumps({'downloaded':len(records),'totalWebpBytes':sum(r['bytes'] for r in records)}))
