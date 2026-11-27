import argparse
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

root=Path(__file__).parent
sys.path.insert(0,str(root))
from pipeline_common import path_label,sha256,write_json
parser=argparse.ArgumentParser();parser.add_argument('blend');parser.add_argument('--output',required=True,type=Path);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
bpy.ops.wm.open_mainfile(filepath=str(Path(args.blend).resolve()))
scene=bpy.context.scene;camera=scene.camera
hinges=[o for o in scene.objects if o.get('role')=='Animated hinge pivot']
geometry=[o for o in scene.objects if o.type in ['MESH','CURVE'] and not o.name.startswith('Studio ')]
first,last=scene.frame_start,scene.frame_end
report={'scene':path_label(args.blend),'scene_sha256':sha256(args.blend),'fps':scene.render.fps/scene.render.fps_base,'frames':[first,last],'hinges':len(hinges),'framing_violations':[],'surface_intersections':[]}
camera_angles=[]
mins=[1,1];maxs=[0,0]
for frame in range(first,last+1):
 scene.frame_set(frame);bpy.context.view_layer.update()
 camera_angles.append(math.atan2(camera.location.y,camera.location.x))
 points=[world_to_camera_view(scene,camera,o.matrix_world@Vector(c)) for o in geometry for c in o.bound_box]
 bounds=(min(p.x for p in points),max(p.x for p in points),min(p.y for p in points),max(p.y for p in points))
 mins=[min(mins[0],bounds[0]),min(mins[1],bounds[2])];maxs=[max(maxs[0],bounds[1]),max(maxs[1],bounds[3])]
 if bounds[0]<.025 or bounds[1]>.975 or bounds[2]<.025 or bounds[3]>.975:report['framing_violations'].append({'frame':frame,'bounds':bounds})
report['all_frame_projected_bounds']={'min_x':mins[0],'max_x':maxs[0],'min_y':mins[1],'max_y':maxs[1]}
tracked=[camera]+hinges
def transforms(frame):
 scene.frame_set(frame);bpy.context.view_layer.update()
 return {o.name:o.matrix_world.copy() for o in tracked}
a=transforms(first);b=transforms(last+1)
camera_angles.append(math.atan2(camera.location.y,camera.location.x))
report['camera_orbits']=sum((b-a+math.pi)%(2*math.pi)-math.pi for a,b in zip(camera_angles,camera_angles[1:]))/(2*math.pi)
report['loop_matrix_max_error']=max(abs(a[n][r][c]-b[n][r][c]) for n in a for r in range(4) for c in range(4))
before=transforms(first-1);after=transforms(first+1);end_before=transforms(last);end_after=transforms(last+2)
report['loop_velocity_max_error']=max(abs((after[n][r][c]-before[n][r][c])-(end_after[n][r][c]-end_before[n][r][c]))/2 for n in a for r in range(4) for c in range(4))
plates=[o for o in scene.objects if 'brass wing plate' in o.name]
body=[o for o in scene.objects if o.name in ['Thorax machined housing','Head housing'] or o.name.startswith('Abdomen segment')]
def world_bvh(obj,dep):
 evaluated=obj.evaluated_get(dep);mesh=evaluated.to_mesh()
 tree=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons])
 evaluated.to_mesh_clear();return tree
step=max(1,round(scene.render.fps/scene.render.fps_base/2))
report['intersection_sample_step_frames']=step
for frame in range(first,last+1,step):
 scene.frame_set(frame);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get()
 trees={o.name:world_bvh(o,dep) for o in plates+body}
 for i,plate in enumerate(plates):
  for other in plates[i+1:]+body:
   hits=trees[plate.name].overlap(trees[other.name])
   if hits:report['surface_intersections'].append({'frame':frame,'objects':[plate.name,other.name],'triangle_pairs':len(hits)})
cfg=json.loads(scene.get('papilio_config_json','{}'))
quarter=first+cfg.get('wing_period_seconds',2)*scene.render.fps/scene.render.fps_base/4
scene.frame_set(math.floor(quarter),subframe=quarter%1)
report['upper_peak_angle_degrees']=[math.degrees(o.rotation_euler.y) for o in hinges if o.get('wing_kind')=='upper']
report['external_images']=[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file]
report['passed']=report['hinges']==4 and not report['framing_violations'] and not report['surface_intersections'] and report['loop_matrix_max_error']<1e-4 and report['loop_velocity_max_error']<1e-4 and not report['external_images']
write_json(args.output,report)
print('BUTTERFLY_AUDIT '+json.dumps(report),flush=True)
if not report['passed']:raise RuntimeError('Scene audit requires review')
