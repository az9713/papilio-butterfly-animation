"""Resume the final render from its saved scene without rebuilding geometry."""
import bpy
import json
import hashlib
import time
from pathlib import Path

root=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(root/'stages'/'final-v01'/'final-v01.blend'))
scene=bpy.context.scene
scene.render.engine='CYCLES'
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
scene.cycles.device='GPU'
scene.render.use_persistent_data=True
scene.render.use_overwrite=False
folder=root/'final-frames'/'final-v01';folder.mkdir(parents=True,exist_ok=True)
fingerprint=hashlib.sha256((root/'stages'/'final-v01'/'final-v01.blend').read_bytes()).hexdigest()
manifest=folder/'source-scene-sha256.txt'
if manifest.exists() and manifest.read_text().strip()!=fingerprint:
 raise RuntimeError('The saved scene changed. Use a new output directory rather than mixing old and new frames.')
if not manifest.exists() and list(folder.glob('frame_*.png')):
 raise RuntimeError('Existing frames have no source manifest. Verify their source before resuming.')
manifest.write_text(fingerprint,encoding='utf-8')
scene.render.filepath=str(folder/'frame_')
started=time.perf_counter()
def progress(*unused):
 frame=scene.frame_current
 data={'frame':frame,'target':288,'elapsed_seconds':round(time.perf_counter()-started,2),'engine':scene.render.engine,'samples':scene.cycles.samples}
 tmp=root/'render-progress.tmp';tmp.write_text(json.dumps(data),encoding='utf-8');tmp.replace(root/'render-progress.json')
 if frame%24==0 or frame==1:print('BUTTERFLY_RENDER_PROGRESS '+json.dumps(data),flush=True)
bpy.app.handlers.render_write.append(progress)
bpy.ops.render.render(animation=True)
report={'frames':len(list(folder.glob('frame_*.png'))),'seconds':round(time.perf_counter()-started,3),'resolution':[scene.render.resolution_x,scene.render.resolution_y],'samples':scene.cycles.samples,'denoiser':scene.cycles.denoiser,'engine':scene.render.engine,'devices':[{'name':d.name,'type':d.type,'use':d.use} for d in prefs.devices]}
(root/'final-render-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('BUTTERFLY_FINAL_RENDER_COMPLETE '+json.dumps(report),flush=True)
if report['frames']!=288:raise RuntimeError('Incomplete final sequence')
