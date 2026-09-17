"""Original native vector ornament; no rasterized lettering or profile content."""
from pathlib import Path
import math
OUT=Path('app/static/artwork/repair-v1')
def svg(name,body,w=210,h=297):
 (OUT/f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" fill="none" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')
def branch(x,y,scale=1,color='#71856e',angle=0,flowers=False):
 leaves=''.join(f'<path d="M0 {k} Q {-12 if i%2 else 12} {k-10} {(-14 if i%2 else 14)} {k-19} Q {(-2 if i%2 else 2)} {k-18} 0 {k}" fill="{color}" fill-opacity=".6" stroke="{color}" stroke-width=".4"/>' for i,k in enumerate([12,24,36,48,60]))
 blooms=''
 if flowers:
  for xx,yy in [(8,18),(-9,43),(7,61)]:
   blooms+=f'<g transform="translate({xx} {yy})">'+''.join(f'<ellipse rx="3.2" ry="6.3" transform="rotate({a}) translate(0 -4)" fill="#eed6c6" stroke="#b58375" stroke-width=".35"/>' for a in [0,60,120,180,240,300])+'<circle r="2" fill="#b48b52"/></g>'
 return f'<g transform="translate({x} {y}) rotate({angle}) scale({scale})"><path d="M0 0Q-5 33 1 75" stroke="{color}" stroke-width=".7"/>{leaves}{blooms}</g>'
svg('arch','<path d="M2 63V30C2 -7 56 -7 56 30V63" stroke="#984e33" stroke-width=".32"/>',58,65)
svg('emerald','<path d="M3 66V29Q3 9 32.5 2Q62 9 62 29V66M6 66V30Q6 12 32.5 5Q59 12 59 30V66" stroke="#355844" stroke-width=".8"/>',65,68)
svg('lancet','<path d="M1 61V24Q1 11 22 1Q43 11 43 24V61M3 61V25Q3 13 22 4Q41 13 41 25V61" stroke="#78603d" stroke-width=".6"/>',44,62)
svg('deco','<path d="M0 25V0H25M4 21V4H21" stroke="#b18b55" stroke-width=".5"/>',30,30)
# Continuous loop corners, with an unobstructed 18 mm body inset.
# A single woven loop; unlike superimposed circles its crossings remain legible.
points=[(12+10*math.sin(3*i*math.tau/360),12+10*math.sin(2*i*math.tau/360)) for i in range(361)]
path='M'+'L'.join(f'{x:.3f} {y:.3f}' for x,y in points)+'Z'
loop=f'<path d="{path}" stroke="#805e44" stroke-width=".32"/>'
svg('kolam',f'<g>{loop}</g><g transform="translate(174 260)">{loop}</g>',198,285)
for name,col in [('patola','#913d39'),('phulkari','#8b3651')]:
 tiles=''.join(f'<g transform="translate({i*8} 0)"><path d="M0 4L4 0L8 4L4 8Z" fill="{col}"/><path d="M2 4L4 2L6 4L4 6Z" fill="#d3a352"/><path d="M0 0L2 2M6 6L8 8" stroke="#345647" stroke-width=".7"/></g>' for i in range(22))
 if name=='patola':
  tile=f'<path d="M0 4L4 0L8 4L4 8Z" fill="{col}"/><path d="M2 4L4 2L6 4L4 6Z" fill="#d3a352"/>'
  svg(name,f'<defs><pattern id="woven" width="8" height="8" patternUnits="userSpaceOnUse">{tile}</pattern></defs><rect width="8" height="260" fill="url(#woven)"/>',8,260)
 else:svg(name,tiles,176,8)
for name,color in [('blue-frame','#244563'),('gold-frame','#a38648'),('maroon-frame','#d6b174')]:
 corners=''.join(f'<g transform="translate({x} {y}) rotate({a})"><path d="M0 10V0H10M2 8V2H8" stroke="{color}" stroke-width=".25"/></g>' for x,y,a in [(9,9,0),(201,9,90),(201,288,180),(9,288,270)])
 svg(name,corners)
# Perimeter foliage is composed outside the text safe zone, not a watermark.
svg('peach',branch(9,1,.42,'#819078',-30,True)+branch(203,289,.27,'#819078',150,True)+'<rect x="9" y="9" width="192" height="279" rx="1" stroke="#a4b29c" stroke-width=".25"/>')
svg('lavender',branch(8,2,.65,'#90819b',-8,True),20,55)
svg('blue',branch(204,289,.52,'#7d9eae',157,True))
svg('garden',branch(4,0,.35,'#577552',-20)+branch(207,287,.44,'#668154',163,True))
svg('amber',branch(6,2,.30,'#af884f',-70)+branch(167,4,.31,'#936d3b',75)+branch(29,1,.26,'#c4a569',-58)+branch(146,2,.25,'#9c7540',59),174,25)
# An open semicircle: central title rectangle is deliberately unpainted.
svg('wreath',branch(7,1,.42,'#72846c',-27,True)+branch(103,1,.42,'#83906b',27,True),110,40)
svg('blossom',''.join(branch(x,295,.20,'#a88388',175,True) for x in [8,34,63,95,129,163,199])+branch(3,1,.18,'#aa8e91',-20,True))
svg('blossom-soft',branch(4,33,.44,'#a29a86',165,True),35,35)
svg('rose',branch(5,0,.32,'#9c797d',-25,True)+branch(206,290,.26,'#96846c',160,True))
# Festive asset contains only drape and a low still-life; the invocation is text.
drape='<path d="M0 0H210V5Q160 15 108 3Q58 15 0 5Z" fill="#6a2b3e" stroke="#ba9460" stroke-width=".45"/>'
lamp='<g transform="translate(164 277)"><path d="M0 4Q9 15 18 4Z" fill="#c5a269" stroke="#e8cf92" stroke-width=".5"/><path d="M9 4Q3 -3 10 -9Q16 -3 9 4Z" fill="#ead2a1"/><path d="M9 10V15M4 15H14" stroke="#d4ad6c" stroke-width=".8"/></g>'
svg('festive',drape+lamp+branch(202,295,.22,'#909265',170,True))
print('Wrote',len(list(OUT.glob('*.svg'))),'vector assets')
# Reuse supplied floral illustrations through vector clipping windows. The source
# pixels are not recolored or stretched; native borders and page layout are separate.
import base64
from PIL import Image

def crop_art(template, box, placed):
 path=Path('app/static/artwork/templates')/f'{template}.jpg'
 with Image.open(path) as im:w,h=im.size
 x,y,cw,ch=[box[0]*w,box[1]*h,box[2]*w,box[3]*h]
 px,py,pw,ph=placed;data=base64.b64encode(path.read_bytes()).decode()
 return f'<svg x="{px}" y="{py}" width="{pw}" height="{ph}" viewBox="{x} {y} {cw} {ch}" preserveAspectRatio="xMidYMid meet"><image href="data:image/jpeg;base64,{data}" width="{w}" height="{h}"/></svg>'
svg('peach',crop_art('figma-peach-floral',(0,0,.28,.25),(0,0,35,40))+crop_art('figma-peach-floral',(.7,.76,.3,.24),(188,275,22,22))+'<rect x="9" y="9" width="192" height="279" stroke="#a4b29c" stroke-width=".25"/>')
svg('lavender',crop_art('figma-lavender-floral',(0,0,.27,.3),(0,0,18,55)),20,55)
svg('blue',crop_art('figma-blue-botanical',(.64,.65,.36,.35),(185,267,25,30)))
svg('garden',crop_art('figma-garden-corners',(0,0,.25,.2),(0,0,22,25))+crop_art('figma-garden-corners',(.70,.64,.3,.36),(180,252,30,45)))
svg('blossom',crop_art('figma-blossom',(0,0,1,.12),(0,0,210,18))+crop_art('figma-blossom',(0,.83,1,.17),(0,275,210,22)))
svg('blossom-soft',crop_art('figma-blossom-serif',(0,.75,.35,.25),(0,0,35,35)),35,35)
svg('rose',crop_art('figma-ganesha-rose',(0,0,.23,.18),(0,0,30,30)))

# Trace only the existing line emblem into native SVG contours. This is not a
# newly invented sacred figure: the supplied silhouette is retained, with its
# invocation and paper excluded. Source provenance still requires owner review.
source=Image.open('app/static/artwork/templates/figma-ganesha-ivory.jpg').convert('L')
mask=source.crop((548,100,642,207));w,h=mask.size
filled={(x,y) for y in range(h) for x in range(w) if mask.getpixel((x,y))<205}
edges={}
def edge(a,b):edges.setdefault(a,[]).append(b)
for x,y in filled:
 if (x,y-1) not in filled:edge((x,y),(x+1,y))
 if (x+1,y) not in filled:edge((x+1,y),(x+1,y+1))
 if (x,y+1) not in filled:edge((x+1,y+1),(x,y+1))
 if (x-1,y) not in filled:edge((x,y+1),(x,y))
contours=[]
while edges:
 start=next(iter(edges));point=start;path=[]
 while True:
  path.append(point);next_point=edges[point].pop()
  if not edges[point]:del edges[point]
  point=next_point
  if point==start:break
 if len(path)>10:contours.append(path)
paths=[]
def simplify(points,tolerance=.8):
 if len(points)<3:return points
 a,b=points[0],points[-1];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
 distances=[abs(dx*(a[1]-p[1])-(a[0]-p[0])*dy)/length if length else math.dist(a,p) for p in points]
 index=max(range(len(points)),key=lambda i:distances[i])
 if distances[index]<=tolerance:return [a,b]
 return simplify(points[:index+1],tolerance)[:-1]+simplify(points[index:],tolerance)
for points in contours:
 # Preserve the supplied contour while replacing pixel stair steps with
 # smooth native curves; no detail or additional anatomy is invented.
 middle=max(range(len(points)),key=lambda i:math.dist(points[0],points[i]))
 points=simplify(points[:middle+1])[:-1]+simplify(points[middle:]+points[:1])[:-1]
 midpoint=lambda a,b:((a[0]+b[0])/2,(a[1]+b[1])/2)
 begin=midpoint(points[-1],points[0]);d=f'M{begin[0]} {begin[1]}'
 for i,p in enumerate(points):
  end=midpoint(p,points[(i+1)%len(points)]);d+=f'Q{p[0]} {p[1]} {end[0]} {end[1]}'
 paths.append(d+'Z')
for color,name in [('#86652f','ganesha-line'),('#d6b174','ganesha-line-light')]:
 svg(name,f'<path fill="{color}" fill-rule="evenodd" d="'+''.join(paths)+'"/>',w,h)
