"""Run in a separate Blender process. All outputs stay beside this script.

Example: blender --background --factory-startup --python-exit-code 1 --python build_scene.py -- --stage blockout --render stills
SVG M/C paths are the source of the extruded wing geometry. All motion is baked into the saved scene.
"""
import argparse
import ast
import json
import math
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).parent
parser=argparse.ArgumentParser()
parser.add_argument('--stage',choices=['blockout','geometry','lookdev','motion','final'],default='blockout')
parser.add_argument('--revision',type=int,default=1)
parser.add_argument('--render',choices=['none','stills','preview','final'],default='stills')
parser.add_argument('--views',nargs='+',default=['hero','front','rear','side'])
parser.add_argument('--samples',type=int,default=24)
parser.add_argument('--res',nargs=2,type=int,default=[960,540])
parser.add_argument('--config',type=Path,default=ROOT/'config.json')
parser.add_argument('--tag',help='Unique checkpoint folder name; existing scenes are preserved')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
cfg=json.loads(args.config.read_text())
tag=args.tag or f'{args.stage}-v{args.revision:02d}'
out=ROOT/'stages'/tag
out.mkdir(parents=True,exist_ok=True)
if (out/f'{tag}.blend').exists():
 raise RuntimeError('Checkpoint already exists. Choose a new --revision or --tag to preserve the last good scene.')
(out/'config-used.json').write_text(json.dumps(cfg,indent=2))
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.render.fps=cfg['fps']
scene.frame_start=1
scene.frame_end=round(cfg['duration_seconds']*cfg['fps'])
scene.render.resolution_x=args.res[0]
scene.render.resolution_y=args.res[1]
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGB'
scene.render.image_settings.compression=35
clay=args.stage in ['blockout','geometry']
report={'stage':args.stage,'revision':args.revision,'blender':bpy.app.version_string,'renders':[]}

def material(name,color,metallic=0,roughness=.4):
 m=bpy.data.materials.new(name);m.use_nodes=True
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 p.inputs['Base Color'].default_value=(*color,1)
 p.inputs['Metallic'].default_value=metallic
 p.inputs['Roughness'].default_value=roughness
 return m,p

gold,gold_node=material('Satin machined brass',(.57,.31,.095),.82,cfg['metal_roughness'])
dark_gold,_=material('Recessed antique brass',(.15,.078,.022),.75,.36)
bright_gold,_=material('Polished brass edges',(.72,.43,.16),.86,.23)
enamel,enamel_node=material('Turquoise vitreous enamel',(.012,.32,.29),.04,cfg['enamel_roughness'])
if 'Coat Weight' in enamel_node.inputs: enamel_node.inputs['Coat Weight'].default_value=.18
if 'Coat Roughness' in enamel_node.inputs: enamel_node.inputs['Coat Roughness'].default_value=.25
if 'Specular IOR Level' in enamel_node.inputs: enamel_node.inputs['Specular IOR Level'].default_value=.30
noise=enamel.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7
noise.inputs['Detail'].default_value=2
ramp=enamel.node_tree.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(.004,.09,.085,1)
ramp.color_ramp.elements[1].position=.84;ramp.color_ramp.elements[1].color=(.012,.28,.23,1)
enamel.node_tree.links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
enamel.node_tree.links.new(ramp.outputs['Color'],enamel_node.inputs['Base Color'])
eye,_=material('Obsidian turquoise lenses',(.004,.025,.028),.35,.15)
stone,stone_node=material('Fine basalt pedestal',(.018,.022,.025),.10,.40)
stone_noise=stone.node_tree.nodes.new('ShaderNodeTexNoise');stone_noise.inputs['Scale'].default_value=38
bump=stone.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.035
stone.node_tree.links.new(stone_noise.outputs['Fac'],bump.inputs['Height']);stone.node_tree.links.new(bump.outputs['Normal'],stone_node.inputs['Normal'])
floor,_=material('Charcoal studio floor',(.012,.016,.020),.10,.32)
claymat,_=material('Neutral clay review',(.35,.38,.40),.05,.48)

def finish(obj,name,mat,parent=None):
 obj.name=name
 if parent is not None: obj.parent=parent
 if hasattr(obj.data,'materials'): obj.data.materials.append(mat)
 if obj.type=='MESH':
  for p in obj.data.polygons:p.use_smooth=True
 return obj

def sphere(name,loc,scale,mat,parent=None,segments=24,rings=12):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings)
 obj=finish(bpy.context.object,name,mat,parent);obj.location=loc;obj.scale=scale
 return obj

def cylinder(name,loc,radius,depth,mat,parent=None,axis=(0,0,1),vertices=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth)
 obj=finish(bpy.context.object,name,mat,parent);obj.location=loc
 obj.rotation_mode='QUATERNION';obj.rotation_quaternion=Vector(axis).to_track_quat('Z','Y')
 bevel=obj.modifiers.new('Machined edge radius','BEVEL');bevel.width=min(.025,radius*.13);bevel.segments=3
 return obj

def tube(name,points,radius,mat,parent=None,closed=False):
 data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=12;data.bevel_depth=radius;data.bevel_resolution=3
 spline=data.splines.new('POLY');spline.points.add(len(points)-1)
 for point,co in zip(spline.points,points):point.co=(*co,1)
 spline.use_cyclic_u=closed
 obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);finish(obj,name,mat,parent)
 return obj

def bezier(points,steps=24):
 a,b,c,d=map(Vector,points)
 return [tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d) for t in [i/steps for i in range(steps+1)]]

def read_profiles():
 profiles={}
 for path in ET.parse(ROOT/'wing-profiles.svg').getroot():
  if not path.tag.endswith('path'):continue
  tokens=re.findall(r'[MCZ]|[-+]?(?:\d*\.)?\d+(?:[eE][-+]?\d+)?',path.attrib['d'])
  cursor=0;current=None;sampled=[]
  while cursor<len(tokens):
   command=tokens[cursor];cursor+=1
   if command=='Z':break
   if command=='M':
    current=Vector((float(tokens[cursor]),float(tokens[cursor+1]),0));cursor+=2;sampled.append(current.copy())
   elif command=='C':
    values=list(map(float,tokens[cursor:cursor+6]));cursor+=6
    b=Vector((values[0],values[1],0));c=Vector((values[2],values[3],0));d=Vector((values[4],values[5],0))
    for j in range(1,13):
     t=j/12;sampled.append((1-t)**3*current+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d)
    current=d
   else:raise RuntimeError('Unsupported profile command '+command)
  if (sampled[0]-sampled[-1]).length<1e-5:sampled.pop()
  origin=float(path.attrib['data-origin-y'])
  profiles[path.attrib['id']]=[((v.x-64)/120,(origin-v.y)/120) for v in sampled]
 return profiles

profiles=read_profiles()
def height(x,y):return .045*(x/2.3)**2+.018*math.sin(y*1.2)

def shell(name,points,offset,thickness,mat,parent):
 if sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))<0:
  points=list(reversed(points))
 poly=[Vector((x,y,0)) for x,y in points]
 lut={tuple(v):i for i,v in enumerate(poly)};n=len(poly)
 tris=[[int(v) if isinstance(v,int) else lut[tuple(v)] for v in tri] for tri in tessellate_polygon([poly])]
 vertices=[(x,y,height(x,y)+offset+side*thickness/2) for side in [1,-1] for x,y in points]
 faces=[tuple(t) for t in tris]+[tuple(i+n for i in reversed(t)) for t in tris]+[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
 obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj);finish(obj,name,mat,parent)
 bevel=obj.modifiers.new('Soft plate edges','BEVEL');bevel.width=.009;bevel.segments=2;bevel.limit_method='ANGLE'
 return obj

root=bpy.data.objects.new('Sculpture root',None);scene.collection.objects.link(root)
root.location=(0,0,cfg['root_height']);root.rotation_euler.x=math.radians(cfg['root_tilt_degrees'])
hinges=[]
for side,label in [(-1,'Left'),(1,'Right')]:
 for kind,yroot in [('upper',.23),('lower',-.27)]:
  hinge=bpy.data.objects.new(f'{label} {kind} wing hinge CONTROL',None);scene.collection.objects.link(hinge);hinge.parent=root;hinge.location=(side*.35,yroot,0)
  hinge['role']='Animated hinge pivot';hinge['side']=side;hinge['wing_kind']=kind
  hinges.append((hinge,side,kind))
  points=profiles[kind]
  if args.stage=='blockout':points=points[::12]
  points=[(x*side,y) for x,y in points]
  # Mirroring reverses orientation; tessellation handles both contour directions.
  shell(f'{label} {kind} brass wing plate',points,0,.065,gold,hinge)
  if args.stage!='blockout':
   cx=sum(x for x,y in points)/len(points);cy=sum(y for x,y in points)/len(points)
   inner=[(cx+(x-cx)*.922,cy+(y-cy)*.922) for x,y in points]
   for face in [-1,1]:
    shell(f'{label} {kind} enamel face {face}',inner,face*.044,.022,enamel,hinge)
    rim=[(x,y,height(x,y)+face*.052) for x,y in points]
    tube(f'{label} {kind} raised rim {face}',rim,.032,bright_gold,hinge,closed=True)
    fractions=[.27,.41,.56,.70,.82] if kind=='upper' else [.24,.43,.61,.77]
    for k,f in enumerate(fractions):
     tx,ty=points[round(f*(len(points)-1))]
     start=(side*.10,.025 if kind=='upper' else -.04)
     q=[]
     for j in range(25):
      u=j/24;x=(1-u)*start[0]+u*tx;y=(1-u)*start[1]+u*ty
      y+=.05*math.sin(math.pi*u)*(1 if kind=='upper' else -1)
      q.append((x,y,height(x,y)+face*.066))
     tube(f'{label} {kind} cloisonne rib {face} {k}',q,.018,bright_gold,hinge)
    for j in range(8,len(points)-8,12):
     x,y=points[j]
     sphere(f'{label} {kind} rim pin {face} {j}',(x*.98,y*.98,height(x,y)+face*.075),(.023,.023,.018),bright_gold,hinge,12,6)
  cylinder(f'{label} {kind} hinge barrel',(side*.35,yroot,0),.090,.35,gold,root,axis=(0,1,0),vertices=32)
  for band in [-.14,.0,.14]:
   cylinder(f'{label} {kind} hinge collar {band}',(side*.35,yroot+band,0),.104,.035,dark_gold,root,axis=(0,1,0),vertices=32)
  cylinder(f'{label} {kind} body connector',(side*.25,yroot,0),.057,.22,gold,root,axis=(1,0,0),vertices=24)
  for ybolt in [-.09,.09]:
   sphere(f'{label} {kind} bracket fastener',(side*.26,yroot+ybolt,.12),(.027,.027,.02),bright_gold,root,12,6)

sphere('Thorax machined housing',(0,.20,.015),(.27,.54,.235),gold,root)
sphere('Head housing',(0,.88,.025),(.27,.27,.24),gold,root)
for side in [-1,1]:
 sphere(f'Lens {side}',(side*.145,.92,.205),(.105,.115,.072),eye,root)
 antenna=bezier([(side*.10,1.04,.03),(side*.12,1.30,.06),(side*.36,1.68,.11),(side*.55,1.76,.12)])
 tube(f'Antenna {side}',antenna,.024,gold,root)
 sphere(f'Antenna terminal {side}',antenna[-1],(.072,.072,.072),bright_gold,root,20,10)
for i in range(5):
 y=-.40-i*.18;r=.205*(1-.13*i)
 sphere(f'Abdomen segment {i}',(0,y,.005),(r,.15,r*.85),gold,root)
 if i<4:
  cylinder(f'Abdomen seam {i}',(0,y-.12,.005),r*.83,.025,dark_gold,root,axis=(0,1,0),vertices=32)
sphere('Abdomen terminal',(0,-1.17,0),(.074,.13,.065),gold,root)

for z,rad,depth,mat,name in [(.23,1.22,.40,stone,'Basalt plinth'),(.048,1.23,.045,dark_gold,'Lower brass foot'),(.10,1.225,.024,enamel,'Turquoise plinth accent')]:
 cylinder(name,(0,0,z),rad,depth,mat)
tube('Narrow upper brass rim',[(1.22*math.cos(a),1.22*math.sin(a),.442) for a in [2*math.pi*i/128 for i in range(128)]],.022,bright_gold,closed=True)
bpy.context.view_layer.update()
tip=root.matrix_world@Vector((0,-1.25,0))
support=bezier([(.12,.03,.46),(.45,.04,1.00),(.25,tip.y+.10,1.72),tuple(tip)],40)
tube('Continuous curved brass support',support,.070,gold)
cylinder('Support pedestal socket',(.12,.03,.47),.15,.08,bright_gold)
sphere('Support body ferrule',tuple(tip),(.09,.09,.09),gold)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0))
finish(bpy.context.object,'Studio floor',floor)
if cfg['lighting_revision']>=2:
 vertices=[];faces=[];segments=128
 cross=[(20+10*math.sin(t),10*(1-math.cos(t))) for t in [math.pi*.5*i/18 for i in range(19)]]+[(30,25)]
 for radius,z in cross:
  vertices.extend((radius*math.cos(2*math.pi*i/segments),radius*math.sin(2*math.pi*i/segments),z) for i in range(segments))
 for j in range(len(cross)-1):
  for i in range(segments):faces.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
 mesh=bpy.data.meshes.new('Seamless curved studio');mesh.from_pydata(vertices,[],faces);mesh.update()
 obj=bpy.data.objects.new('Studio backdrop',mesh);scene.collection.objects.link(obj);finish(obj,'Studio backdrop',floor)

world=bpy.data.worlds.new('Dark studio environment');world.use_nodes=True;scene.world=world
background=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');background.inputs['Color'].default_value=(.10,.13,.16,1);background.inputs['Strength'].default_value=.22
lights=[]
def area(name,pos,energy,size,color=(1,1,1),target=(0,0,3)):
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;data.color=color
 obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=pos;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler();lights.append((obj,energy));return obj
area('Large warm key',(4,-6,8),1200,5,(1,.85,.66))
area('Cool broad fill',(-5,-2,5),700,5,(.63,.85,1))
area('Rear rim',(2,5,7),1500,4,(1,.84,.65))
area('Top softbox',(0,0,9),900,5,(.86,.94,1))
if cfg['lighting_revision']>=2:
 area('Rear soft fill',(-4,4,4),450,5,(.68,.9,1))
 scene.view_settings.exposure=-.35

camdata=bpy.data.cameras.new('Orbit camera');camera=bpy.data.objects.new('Orbit camera',camdata);scene.collection.objects.link(camera);scene.camera=camera
camdata.lens=cfg['camera_lens_mm'];camdata.clip_end=300
target=Vector((0,0,cfg['camera_target_height']))
camera.rotation_mode='QUATERNION'
def pose_camera(angle):
 camera.location=(cfg['camera_radius']*math.cos(angle),cfg['camera_radius']*math.sin(angle),cfg['camera_height'])
 camera.rotation_quaternion=(target-camera.location).to_track_quat('-Z','Y')

if args.stage in ['motion','final']:
 previous=None
 for frame in range(-2,scene.frame_end+4):
  t=(frame-1)/cfg['fps']
  for hinge,side,kind in hinges:
   factor=cfg['lower_wing_amplitude_factor'] if kind=='lower' else 1
   angle=cfg['wing_rest_degrees']+cfg['wing_amplitude_degrees']*factor*math.sin(2*math.pi*t/cfg['wing_period_seconds'])
   hinge.rotation_euler.y=-side*math.radians(angle)
   hinge.keyframe_insert(data_path='rotation_euler',frame=frame)
  angle=math.radians(cfg['camera_start_degrees'])+2*math.pi*t/cfg['duration_seconds']
  pose_camera(angle)
  q=camera.rotation_quaternion.copy()
  if previous is not None and previous.dot(q)<0:q.negate()
  camera.rotation_quaternion=q;previous=q.copy()
  camera.keyframe_insert(data_path='location',frame=frame);camera.keyframe_insert(data_path='rotation_quaternion',frame=frame)
  for obj,energy in lights:
   obj.data.energy=energy*(1+cfg['light_breath_fraction']*math.sin(2*math.pi*t/cfg['light_period_seconds']))
   obj.data.keyframe_insert(data_path='energy',frame=frame)
else:
 for hinge,side,kind in hinges:hinge.rotation_euler.y=-side*math.radians(cfg['wing_rest_degrees'])
 pose_camera(math.radians(cfg['camera_start_degrees']))
scene.frame_set(1)

if clay or args.render=='preview':
 scene.render.engine='BLENDER_EEVEE'
 if clay:scene.view_layers[0].material_override=claymat
else:
 scene.render.engine='CYCLES'
 prefs=bpy.context.preferences.addons['cycles'].preferences
 prefs.compute_device_type='OPTIX';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type=='OPTIX'
 scene.cycles.device='GPU';scene.cycles.samples=args.samples
 scene.cycles.use_denoising=True
 scene.cycles.seed=42
 if hasattr(scene.cycles,'use_animated_seed'):scene.cycles.use_animated_seed=False
 try:scene.cycles.denoiser='OPTIX'
 except TypeError:pass
 scene.cycles.adaptive_threshold=.045
 scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=2;scene.cycles.glossy_bounces=4
 report['cycles_devices']=[{'name':d.name,'type':d.type,'use':d.use} for d in prefs.devices]
 report['denoiser']=scene.cycles.denoiser
scene.render.use_persistent_data=True
report['engine']=scene.render.engine

scene.render.film_transparent=False
scene.render.filepath=str(out/'frame_')
report['objects']=len(scene.objects)
report['mesh_vertices']=sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH')
report['wing_controls']=[o.name for o,_,_ in hinges]
if args.stage in ['motion','final']:
 sample_frames=[1,49,97,145,193,241,289]
 extent=[]
 for f in sample_frames:
  scene.frame_set(f);bpy.context.view_layer.update()
  projected=[]
  for obj in scene.objects:
   if obj.type not in ['MESH','CURVE'] or obj.name.startswith('Studio '):continue
   for co in obj.bound_box:
    projected.append(world_to_camera_view(scene,camera,obj.matrix_world@Vector(co)))
  extent.append({'frame':f,'min_x':min(p.x for p in projected),'max_x':max(p.x for p in projected),'min_y':min(p.y for p in projected),'max_y':max(p.y for p in projected)})
 report['framing_samples']=extent
 scene.frame_set(1);bpy.context.view_layer.update()
 transforms={o.name:[list(row) for row in o.matrix_world] for o in [camera]+[h for h,_,_ in hinges]}
 scene.frame_set(289);bpy.context.view_layer.update()
 report['loop_matrix_max_error']=max(abs(o.matrix_world[r][c]-transforms[o.name][r][c]) for o in [camera]+[h for h,_,_ in hinges] for r in range(4) for c in range(4))
 scene.frame_set(1)

blend=out/f'{tag}.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
report['blend']=str(blend)
if args.render=='stills':
 angles={'hero':cfg['camera_start_degrees'],'front':-90,'rear':90,'side':0}
 if camera.animation_data:camera.animation_data_clear()
 for view in args.views:
  pose_camera(math.radians(angles[view]));bpy.context.view_layer.update()
  scene.render.filepath=str(out/f'{tag}-{view}.png')
  start=time.perf_counter();bpy.ops.render.render(write_still=True)
  report['renders'].append({'view':view,'path':scene.render.filepath,'seconds':round(time.perf_counter()-start,3)})
elif args.render in ['preview','final']:
 directory=ROOT/('preview-frames' if args.render=='preview' else 'final-frames')/tag
 directory.mkdir(parents=True,exist_ok=True)
 scene.render.filepath=str(directory/'frame_')
 scene.render.use_overwrite=False
 start=time.perf_counter();bpy.ops.render.render(animation=True)
 report['renders'].append({'frames':str(directory),'seconds':round(time.perf_counter()-start,3),'count':len(list(directory.glob('frame_*.png')))})
(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('BUTTERFLY_STAGE_COMPLETE '+json.dumps(report),flush=True)
