"""Vendor OFL fonts used by the supplied Figma designs, with their licenses."""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import quote
from fontTools.ttLib import TTFont
FONTS={'inriasans':['InriaSans-Regular.ttf','InriaSans-Bold.ttf'],'figtree':['Figtree[wght].ttf'],'poppins':['Poppins-Medium.ttf','Poppins-SemiBold.ttf','Poppins-Bold.ttf'],'tirodevanagarisanskrit':['TiroDevanagariSanskrit-Regular.ttf'],'merriweather':['Merriweather-Italic[opsz,wdth,wght].ttf']}
root=Path('app/static/fonts')
for family,files in FONTS.items():
 for name in [*files,'OFL.txt']:
  with urlopen('https://raw.githubusercontent.com/google/fonts/main/ofl/'+family+'/'+quote(name),timeout=40) as r:data=r.read()
  target=root/('OFL-'+family+'.txt' if name=='OFL.txt' else name)
  target.write_bytes(data)
  if name.endswith('.ttf'):
   font=TTFont(target);font.flavor='woff2';font.save(target.with_suffix('.woff2'))
 print(family)
