import json
from pathlib import Path

root=Path(__file__).parent
profiles={
 'upper':[(.02,.04),(.22,.63),(.65,1.34),(1.25,1.92),(1.88,2.16),(2.22,1.98),(2.35,1.52),(2.07,.92),(1.56,.42),(.75,.08),(.20,-.09)],
 'lower':[(.02,0),(.57,-.04),(1.32,-.34),(1.70,-.78),(1.63,-1.32),(1.21,-1.75),(.74,-1.70),(.36,-1.22),(.08,-.52)]
}
def point(p,origin): return (64+120*p[0],origin-120*p[1])
def fmt(p): return f'{p[0]:.4f},{p[1]:.4f}'
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="400" height="600" viewBox="0 0 400 600">','<title>Editable upper and lower wing profiles for Papilio</title>']
for name,points in profiles.items():
 origin=310 if name=='upper' else 350
 d=['M'+fmt(point(points[0],origin))]
 for i,p1 in enumerate(points):
  p0=points[(i-1)%len(points)];p2=points[(i+1)%len(points)];p3=points[(i+2)%len(points)]
  c1=tuple(p1[k]+(p2[k]-p0[k])/6 for k in range(2))
  c2=tuple(p2[k]-(p3[k]-p1[k])/6 for k in range(2))
  d.append('C'+fmt(point(c1,origin))+' '+fmt(point(c2,origin))+' '+fmt(point(p2,origin)))
 parts.append(f'<path id="{name}" data-origin-y="{origin}" d="'+ ' '.join(d)+' Z" fill="#219e9c" stroke="#b88b44" stroke-width="6" stroke-linejoin="round"/>')
parts.append('</svg>')
(root/'wing-profiles.svg').write_text('\n'.join(parts),encoding='utf-8')
(root/'profile-control-points.json').write_text(json.dumps(profiles,indent=2),encoding='utf-8')
print(root/'wing-profiles.svg')
