import hashlib
import json
import zipfile
from pathlib import Path

root=Path(__file__).parent
selected=[]
for pattern in ['*.py','*.json','*.md','*.html','requirements-review.txt','wing-profiles.svg','wing-profiles.png','concept-v*.png']:
 selected.extend(root.glob(pattern))
for pattern in ['*.blend','config-used.json','report.json','*-views.jpg']:
 selected.extend((root/'stages').glob('*/'+pattern))
selected=sorted(set(selected))
manifest=[]
for path in selected:
 if path.name=='source-manifest.json':continue
 manifest.append({'path':path.relative_to(root).as_posix(),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(root/'source-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
selected=[p for p in selected if p.name!='source-manifest.json']+[root/'source-manifest.json']
archive=root/'papilio-editable-source.zip'
if archive.exists():raise RuntimeError('Preserve existing archive')
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as package:
 for path in selected:package.write(path,path.relative_to(root).as_posix())
with zipfile.ZipFile(archive) as package:
 assert package.testzip() is None
 assert 'stages/final-v01/final-v01.blend' in package.namelist()
 assert 'build_scene.py' in package.namelist()
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'files':len(selected),'under_page_upload_limit':archive.stat().st_size<=10*1024*1024}))
