"""Copy approved generation masters, preserve alpha, make bounded print/web derivatives."""
import json,sys,shutil
from pathlib import Path
from PIL import Image
root=Path('app/static/artwork/collection-v1'); masters=Path('artwork-masters/collection-v1')
root.mkdir(parents=True,exist_ok=True);masters.mkdir(parents=True,exist_ok=True)
manifest_path=Path('docs/template-collection/artwork-manifest.json')
manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
for name,source in json.loads(Path(sys.argv[1]).read_text()).items():
    target=masters/(name+'.png')
    if Path(source).resolve()!=target.resolve():shutil.copy2(source,target)
    with Image.open(target) as im:
        im=im.convert('RGBA')
        if im.getchannel('A').getextrema()[0]==255:raise ValueError(f'{name}: transparency missing')
        variants={}
        # Match source pixels to the actual print placement (roughly 450–600 dpi).
        # Chromium losslessly embeds transparent images; oversized tiny icons bloat PDFs.
        pdf_size={'sage-branch':750,'deco-corner':400,'ink-leaf':450,'kolam-corner':400,'alpana-ornament':600,'paithani-peacock':750,'miniature-pavilion':750,'braj-lotus':450,'krishna':800,'ganesha':750,'rama':900,'ahimsa-geometry':600,'dhamma-lotus':450,'ambedkar':700}.get(name,1400)
        for kind,size,quality in [('pdf',pdf_size,92),('preview',min(700,pdf_size),88),('thumb',240,82)]:
            image=im.copy();image.thumbnail((size,size),Image.Resampling.LANCZOS)
            dest=root/f'{name}-{kind}.webp';image.save(dest,'WEBP',quality=quality,method=6)
            variants[kind]={'path':str(dest),'bytes':dest.stat().st_size,'size':list(image.size)}
        generation_asset=manifest.get(name,{}).get('generation_asset',Path(source).name)
        manifest[name]={'generator':'OpenAI built-in imagegen','source':str(target),'generation_asset':generation_asset,'master':str(target),'prompt':f'docs/template-collection/prompts/{name}.txt','variants':variants,'review':'Manually reviewed before integration; no lettering or unrelated symbols.'}
manifest_path.write_text(json.dumps(manifest,indent=2))
