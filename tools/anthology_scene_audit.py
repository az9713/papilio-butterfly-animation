"""Blender-side fingerprint of geometry and sampled baked motion."""
from pathlib import Path
import hashlib,json,sys
import bpy

args=sys.argv[sys.argv.index('--')+1:]
scene=bpy.context.scene
objects=[]
for o in sorted(scene.objects,key=lambda x:x.name):
    row={'name':o.name,'type':o.type}
    if o.type=='MESH':
        row['vertices']=[[round(v,6) for v in p.co] for p in o.data.vertices]
        faces=[]
        for poly in o.data.polygons:
            vertices=list(poly.vertices)
            canonical=min(tuple(vertices[i:]+vertices[:i]) for i in range(len(vertices)))
            faces.append((canonical,poly.material_index,poly.use_smooth))
        # Parallel primitive construction may reorder polygon storage. Compare
        # the same oriented faces and attributes, without depending on order.
        row['faces']=sorted(faces)
    if o.type=='CURVE':row['curves']=[[[round(v,6) for v in p.co] for p in spline.points] for spline in o.data.splines]
    row['samples']=[]
    objects.append(row)
ordered=sorted(scene.objects,key=lambda x:x.name)
for f in [1,169,336]:
    scene.frame_set(f)
    for o,row in zip(ordered,objects):
        row['samples'].append({'frame':f,'world_matrix':[[round(v,6) for v in r] for r in o.matrix_world],'hidden':o.hide_render})
source=Path(args[0]);svg=hashlib.sha256((source/'design.svg').read_bytes()).hexdigest();timeline=hashlib.sha256((source/'timeline.json').read_bytes()).hexdigest()
result={'geometry_and_motion_sha256':hashlib.sha256(json.dumps(objects,sort_keys=True).encode()).hexdigest(),
        'objects':len(objects),'frames':scene.frame_end,'fps':scene.render.fps,'resolution':[scene.render.resolution_x,scene.render.resolution_y],
        'svg_identity_matches':scene.get('svg_sha256')==svg,'timeline_identity_matches':scene.get('timeline_sha256')==timeline,
        'svg_sha256':svg,'timeline_sha256':timeline,'external_images':[i.name for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]}
Path(args[1]).write_text(json.dumps(result,indent=2),encoding='utf8')
Path(args[1]).with_name(Path(args[1]).stem+'-detail.json').write_text(json.dumps(objects),encoding='utf8')
assert result['frames']==336 and result['fps']==24 and result['resolution']==[1280,720]
assert result['svg_identity_matches'] and result['timeline_identity_matches']
assert not result['external_images']
print('SCENE_AUDIT_OK')
