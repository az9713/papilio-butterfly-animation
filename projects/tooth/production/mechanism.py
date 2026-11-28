import bpy, math, sys, xml.etree.ElementTree as ET
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
def material(name,color,metal=0,rough=.4,grain=False):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 n=m.node_tree.nodes; link=m.node_tree.links.new;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if grain:
  tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=8;tex.inputs['Detail'].default_value=3
  ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=tuple(c*.32 for c in color)+(1,);ramp.color_ramp.elements[1].color=tuple(min(1,c*1.7) for c in color)+(1,);link(tex.outputs['Fac'],ramp.inputs[0]);link(ramp.outputs[0],p.inputs['Base Color'])
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.045;link(tex.outputs['Fac'],bump.inputs['Height']);link(bump.outputs[0],p.inputs['Normal'])
 return m
wal=material('Oiled walnut',(.15,.047,.018),0,.34,True); green=material('Petrol enamel',(.028,.085,.079),.36,.34,True); brass=material('Spun antique brass',(.58,.32,.085),.83,.27,True);rim=material('Polished lip',(.82,.52,.19),.83,.22);steel=material('Blued steel',(.18,.22,.23),.85,.33);copper=material('Repair copper',(.78,.23,.077),.75,.24);dark=material('Ink',(.012,.014,.014));ivory=material('Bone',(.84,.72,.5))
def finish(o,name,m,bev=0):
 o.name=name;o.data.materials.append(m)
 if bev:
  mod=o.modifiers.new('Rounded edges','BEVEL');mod.width=bev;mod.segments=3
  o.modifiers.new('Planar normals','WEIGHTED_NORMAL')
 return o
def cube(name,loc,dim,m,bev=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,m,bev)
def cyl(name,loc,r,depth,m,axis='X',bev=.012,verts=64):
 rot=(0,math.pi/2,0) if axis=='X' else ((math.pi/2,0,0) if axis=='Y' else (0,0,0))
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return finish(o,name,m,bev)
def par(o,p):
 w=o.matrix_world.copy();o.parent=p;o.matrix_world=w
def empty(name,loc):
 o=bpy.data.objects.new(name,None);s.collection.objects.link(o);o.location=loc;bpy.context.view_layer.update();return o
def area(name,loc,power,color,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.4))-o.location).to_track_quat('-Z','Y').to_euler()
cube('Workbench',(0,0,-.53),(60,60,.5),wal)
cube('Walnut case',(0,0,-.07),(6.6,4,.53),wal,.14);cube('Brass reveal',(0,0,.15),(6.38,3.78,.06),rim,.05);cube('Enamel bed',(0,0,.21),(6.27,3.67,.14),green,.08)
center=(0,.49,1.08);pivot=empty('Cylinder one turn per phrase',center)
par(cyl('Pinned brass drum',center,.67,4.88,brass),pivot)
for x in [-2.44,2.44]:par(cyl('Brass collar',(x,.49,1.08),.713,.09,rim),pivot)
for i in range(17):
 x=-2.28+i*.285;par(cyl('Register line',(x,.49,1.08),.675,.012,steel,bev=.002),pivot)
for x in [-2.72,2.72]:
 cube('Bearing foot',(x,.49,.65),(.3,1,.75),brass,.09);cyl('Bearing cap',(x,.49,1.08),.37,.34,green);cyl('Axle',(x,.49,1.08),.14,.56,rim)
cube('Comb rail',(0,-1.26,.61),(5.08,.46,.22),brass,.04)
last=None
teeth={}
for i in range(17):
 x=-2.28+i*.285
 o=cube('Comb tooth %02d'%i,(x,-.76,.78),(.16,.97,.055),copper if i==3 else steel,.017)
 if i==3:last=o
 teeth[i]=o
for x in [-2.32,-1.18,0,1.18,2.32]:
 cyl('Slotted screw',(x,-1.28,.75),.09,.04,rim,'Z');cube('Slot',(x,-1.28,.775),(.11,.018,.008),dark,.002)
events=[(float(e.get('data-beat')),int(e.get('data-midi')),e.get('data-cadence')=='1') for e in ET.parse(R/'score.svg').iter() if e.get('data-midi')]
for beat,n,goal in events:
 idx=3+round((n-62)*1.7);x=-2.28+idx*.285
 theta=math.pi+beat*2*math.pi/8+.35
 y=.49+.704*math.cos(theta);z=1.08+.704*math.sin(theta)
 o=cyl('Cadence pin' if goal else 'Note pin',(x,y,z),.055,.15,rim,'Z',.006,20);o.rotation_euler.x=theta-math.pi/2;bpy.context.view_layer.update();par(o,pivot)
for rep in range(3):
 for beat,n,goal in events:
  if goal and rep!=1:continue
  f=1+rep*60+beat*7.5;o=teeth[3+round((n-62)*1.7)]
  for offset,angle in [(-1,0),(0,-.09),(1,.06),(2,0)]:
   o.rotation_euler.x=angle;o.keyframe_insert(data_path='rotation_euler',frame=f+offset)
# Dial on the right of the case, engraved witness marks and winding lugs.
for i in range(32):
 a=i*2*math.pi/32;o=cube('End wheel knurl',(2.49,.49+.68*math.cos(a),1.08+.68*math.sin(a)),(.13,.07,.09),rim,.01);o.rotation_euler.x=a
cyl('Winding arbor',(3.02,.49,1.08),.10,.59,rim);cube('Winding key',(3.28,.49,1.08),(.11,.17,.73),brass,.06)
# Repairer's copper slider brings the missing tooth into the comb.
for f,dy,dz in [(1,-1.7,.7),(59,-1.7,.7),(67,0,0),(119,0,0),(125,0,0),(135,-1.7,.7),(173,-1.7,.7)]:
 last.location=(-2.28+3*.285,-.76+dy,.78+dz);last.keyframe_insert(data_path='location',frame=f)
for f,vis in [(1,True),(59,True),(60,False),(135,False),(136,True)]:
 last.hide_render=vis;last.keyframe_insert(data_path='hide_render',frame=f)
# Tapered steel forceps hold the copper insert for both changes.
tool=empty('Repairer forceps',(0,0,0))
for side in [-1,1]:
 x=-2.28+3*.285+side*.09
 o=cube('Forceps tapered arm',(x,-1.86,.94),(.035,1.7,.055),steel,.012);o.rotation_euler.x=-.21;bpy.context.view_layer.update();par(o,tool)
for f,y,z in [(1,-5,1),(59,-1.7,.7),(67,0,0),(70,0,0),(77,-5,1),(114,-5,1),(123,0,0),(125,0,0),(135,-1.7,.7),(139,-5,1),(173,-5,1)]:
 tool.location=(0,y,z);tool.keyframe_insert(data_path='location',frame=f)
for f in [1,61,121,181]:
 pivot.rotation_euler.x=-(f-1)*2*math.pi/60;pivot.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in pivot.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
 for kp in fc.keyframe_points:kp.interpolation='LINEAR'
area('Warm window',(-3,-2,6),520,(1,.78,.53),5);area('Cool shop fill',(2,4,5),760,(.60,.78,.84),4);area('Glint',(5,-3,3),310,(1,.85,.65),2.2)
s.world=bpy.data.worlds.new('Workshop ambient');s.world.color=(.22,.22,.22)
bpy.ops.object.camera_add(location=(3.45,-7.1,5.8));cam=bpy.context.object;s.camera=cam
def aim(pos,target):
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
aim((3.45,-7.1,5.8),(0,0,.71));cam.data.lens=39
s.render.engine='CYCLES';s.cycles.samples=6;s.cycles.use_denoising=True
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for dev in prefs.devices:dev.use=(dev.type=='OPTIX')
 if any(d.use for d in prefs.devices):s.cycles.device='GPU'
except Exception:pass
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.fps=12;s.frame_start=1;s.frame_end=172;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=94
s.view_settings.look='AgX - Medium High Contrast'
out=R/'mechanism-frames';out.mkdir(exist_ok=True)
s.frame_set(1);s.render.filepath='//mechanism-frames/';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(R/'mechanism.blend'))
def frame(f,path):
 s.frame_set(f);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
if 'preview' in sys.argv:
 frame(70,R/'mechanism-preview.jpg');aim((-3,-5,5),(0,0,.7));frame(70,R/'mechanism-alternate.jpg')
else:
 for f in range(1,173):
  if (f-1)%60<36 and not (out/f'{f:03}.jpg').exists():frame(f,out/f'{f:03}.jpg')
