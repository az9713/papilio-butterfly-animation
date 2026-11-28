"""SVG-driven miniature films. Copy into a project's source/ to rebuild standalone.

Blender --background --factory-startup --python source/build_scene.py -- --preview
Blender --background source/scene.blend --render-anim
"""
from pathlib import Path
import argparse,datetime,hashlib,json,math,random,sys,xml.etree.ElementTree as ET
import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

SOURCE=Path(__file__).resolve().parent
P=SOURCE.parent
cfg=json.loads((SOURCE/'timeline.json').read_text(encoding='utf8'))
args=argparse.ArgumentParser();args.add_argument('--preview',action='store_true');args.add_argument('--render',action='store_true')
args.add_argument('--frame',type=int);args.add_argument('--width',type=int);args=args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
random.seed(cfg['seed'])
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=cfg['width'];s.render.resolution_y=cfg['height'];s.render.resolution_percentage=100
s.render.fps=cfg['fps'];s.frame_start=1;s.frame_end=round(cfg['duration']*cfg['fps'])
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.compression=15
s.render.filepath='//../frames/frame_';s.render.film_transparent=False
s.view_settings.view_transform='AgX'
if hasattr(s,'eevee'):
    s.eevee.taa_render_samples=16
s.world=bpy.data.worlds.new('Studio air');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.025,.035,.06,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
profiles={e.get('data-role'):[(float(p.split(',')[0]),-float(p.split(',')[1])) for p in e.get('points').split()] for e in ET.parse(SOURCE/'design.svg').iter() if e.get('data-role')}

def mat(name,color,metal=0,rough=.4,emit=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes['Principled BSDF'];n.inputs['Base Color'].default_value=(*color,1)
    n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough
    if emit:n.inputs['Emission Color'].default_value=(*color,1);n.inputs['Emission Strength'].default_value=emit
    return m

gold=mat('Brushed champagne brass',(.61,.32,.075),.8,.26)
dark=mat('Midnight lacquer',(.018,.035,.055),.3,.3)
ivory=mat('Warm ivory',(.9,.81,.6),0,.5)
teal=mat('Petrol enamel',(.018,.27,.3),.3,.26)
red=mat('Vermilion enamel',(.57,.055,.025),.2,.3)
wood=mat('Honey walnut',(.24,.085,.025),.1,.48)
black=mat('Carbon',(.009,.012,.016),.1,.45)

def finish(o,name,m):
    o.name=name
    if m:o.data.materials.append(m)
    if o.type=='MESH':
        for p in o.data.polygons:p.use_smooth=True
    return o

def cube(name,loc,dims,m,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Soft manufactured edges','BEVEL');mod.width=bevel;mod.segments=3
        mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return finish(o,name,m)

def sphere(name,loc,scale,m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,m)

def cyl(name,a,b,r,m):
    a,b=Vector(a),Vector(b);d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,name,m)

def line(name,points,m,r=.025,closed=False):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=2;c.bevel_depth=r;c.bevel_resolution=3
    sp=c.splines.new('POLY');sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points):p.co=(*co,1)
    sp.use_cyclic_u=closed;o=bpy.data.objects.new(name,c);s.collection.objects.link(o);return finish(o,name,m)

def outline(role,name,m,y=0,offset=(0,0),scale=1,r=.03):
    return line(name,[(x*scale+offset[0],y,z*scale+offset[1]) for x,z in profiles[role]],m,r)

def polygon(role,name,m,y=0,offset=(0,0),scale=1,depth=.1):
    points=[Vector((x*scale+offset[0],z*scale+offset[1],0)) for x,z in profiles[role]]
    if (points[0]-points[-1]).length<.0001:points.pop()
    tris=tessellate_polygon([points]);lookup={tuple(v):i for i,v in enumerate(points)};n=len(points)
    idx=[[v if isinstance(v,int) else lookup[tuple(v)] for v in tri] for tri in tris]
    verts=[(v.x,y+d,v.y) for d in [-depth/2,depth/2] for v in points]
    faces=[tuple(t) for t in idx]+[tuple(i+n for i in reversed(t)) for t in idx]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);s.collection.objects.link(o)
    finish(o,name,m)
    for face in mesh.polygons:face.use_smooth=False
    return o

def ring(name,loc,r,m,thick=.035):
    return line(name,[(loc[0]+r*math.cos(a*2*math.pi/96),loc[1],loc[2]+r*math.sin(a*2*math.pi/96)) for a in range(97)],m,thick)

def text(body,loc,size,m,name=None):
    c=bpy.data.curves.new(name or body,'FONT');c.body=body;c.align_x='CENTER';c.align_y='CENTER';c.size=size;c.extrude=.002;c.bevel_depth=.001
    o=bpy.data.objects.new(name or body,c);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);return finish(o,name or body,m)

def group(name,loc=(0,0,0)):
    o=bpy.data.objects.new(name,None);s.collection.objects.link(o);o.location=loc;return o

def parent(o,p):o.parent=p;return o

def clip_painted_scroll(o):
    for slot in o.material_slots:
        m=slot.material.copy();slot.material=m;n=m.node_tree.nodes;links=m.node_tree.links
        geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');absolute=n.new('ShaderNodeMath');absolute.operation='ABSOLUTE'
        inside=n.new('ShaderNodeMath');inside.operation='LESS_THAN';inside.inputs[1].default_value=3.52
        trans=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader')
        links.new(geo.outputs['Position'],sep.inputs[0]);links.new(sep.outputs['X'],absolute.inputs[0]);links.new(absolute.outputs[0],inside.inputs[0])
        links.new(inside.outputs[0],mix.inputs[0]);links.new(trans.outputs[0],mix.inputs[1]);links.new(n['Principled BSDF'].outputs[0],mix.inputs[2]);links.new(mix.outputs[0],n['Material Output'].inputs[0])

def k(o,t,loc=None,rot=None,scale=None):
    f=1+min(t,cfg['duration']-1/cfg['fps'])*cfg['fps']
    if loc is not None:o.location=loc;o.keyframe_insert(data_path='location',frame=f)
    if rot is not None:o.rotation_euler=rot;o.keyframe_insert(data_path='rotation_euler',frame=f)
    if scale is not None:
        o.scale=(scale,scale,scale) if isinstance(scale,(int,float)) else scale;o.keyframe_insert(data_path='scale',frame=f)

def visibility(o,t,visible):
    o.hide_render=not visible;o.keyframe_insert(data_path='hide_render',frame=1+t*cfg['fps'])

def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def cam(loc=(0,-19,7),target=(0,0,2),span=13,ortho=True):
    d=bpy.data.cameras.new('Story camera');o=bpy.data.objects.new('Story camera',d);s.collection.objects.link(o);o.location=loc;aim(o,target)
    d.type='ORTHO' if ortho else 'PERSP';d.ortho_scale=span;d.lens=42;s.camera=o;d.clip_end=200
    return o

def camera_key(o,t,loc,target):
    o.location=loc;aim(o,target);k(o,t,loc=loc,rot=o.rotation_euler.copy())

def light(name,loc,energy,color,size,target=(0,0,1)):
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.color=color;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;aim(o,target)

def stage(color=(.025,.04,.055),floor=-2):
    m=mat('Stage',color,.1,.44);cube('Ground',(0,2,floor-.2),(50,50,.4),m,.1)
    light('Large warm key',(-5,-7,10),1500,(1,.76,.52),7)
    light('Cool fill',(6,-2,6),1000,(.46,.72,1),5)
    light('Rim',(1,6,9),2000,(1,.53,.22),4)

def person(name,loc,coat=dark,scale=1):
    p=group(name,loc)
    parent(sphere(name+' head',(0,0,1.66),(.25,.23,.30),wood),p)
    parent(cube(name+' coat',(0,0,.96),(.65,.4,.93),coat,.15),p)
    for side in [-1,1]:
        parent(cyl(name+' leg',(.16*side,0,.55),(.16*side,0,.08),.085,dark),p)
        parent(sphere(name+' shoe',(.16*side,-.08,.05),(.13,.24,.10),black),p)
        parent(cyl(name+' arm',(.34*side,0,1.3),(.47*side,-.08,.7),.075,coat),p)
        parent(sphere(name+' hand',(.47*side,-.08,.66),(.09,.09,.13),wood),p)
        parent(sphere(name+' eye',(.085*side,-.217,1.71),(.035,.025,.04),ivory),p)
        parent(sphere(name+' pupil',(.085*side,-.24,1.71),(.014,.012,.023),black),p)
    p.scale=(scale,)*3;return p

def whale():
    stage((.012,.034,.045),-1.8)
    sea=mat('Cold dock water',(.008,.075,.10),.65,.21)
    cube('Dock water',(0,3,-1.53),(28,22,.05),sea)
    glow=mat('Limewashed scuffs',(.67,.94,.91),0,.4,1.1)
    hero=Vector((0,-18,5));points=[Vector((x,0,z+2.8)) for x,z in profiles['whale']]
    depths=[-3,2,-1,5,0,3]
    for i,depth in enumerate(depths):
        start=i*(len(points)-1)//6;end=(i+1)*(len(points)-1)//6
        projected=[hero+(p-hero)*((depth-hero.y)/(0-hero.y)) for p in points[start:end+1]]
        line('Anamorphic whale fragment '+str(i),projected,glow,.055)
        x=sum(p.x for p in projected)/len(projected)
        for xx in [x-.55,x+.55]:cube('Six gantry upright',(xx,depth+.16,1.6),(.13,.15,6.3),dark)
        cube('Gantry cross beam',(x,depth+.15,4.7),(1.4,.23,.22),gold)
        for p in projected:line('Painted steel brace',[(p.x,depth+.17,-1.45),(p.x,depth+.17,4.6)],dark,.035)
    eye=[(x,-.02,z+2.8) for x,z in profiles['eye']];line('Whale eye',eye,glow,.055)
    for side in [-1,1]:
        cube('Dry dock side',(side*6.6,2,-.8),(1,20,1.2),dark)
        for j in range(9):cube('Dock amber witness',(side*6.6,-6+j*2,-.1),(.1,.18,.08),gold)
    c=cam((5,-18,7),(0,1,2.2),ortho=False)
    for t,loc,target in [(0,(10,-14,7),(0,1,2.4)),(7,tuple(hero),(0,0,2.8)),(10,tuple(hero),(0,0,2.8)),(14,(-8,-15,6),(0,1,2.6))]:camera_key(c,t,loc,target)

def cyanotype():
    stage((.12,.17,.18),-2)
    paper=mat('Cyanotype exposed paper',(.86,.81,.65),0,.7)
    board=cube('Exposure paper',(0,0,1),(7,.12,5),paper)
    blue=paper.node_tree.nodes['Principled BSDF'].inputs['Base Color']
    for t,col in [(0,(.86,.81,.65,1)),(6,(.86,.81,.65,1)),(10,(.008,.06,.42,1)),(14,(.008,.06,.42,1))]:blue.default_value=col;blue.keyframe_insert(data_path='default_value',frame=1+t*24)
    leafmat=mat('Pressed fern',(.24,.35,.12),0,.7)
    for i,x in enumerate([-2,-.65,.8,2]):
        leaf=group('Pressed specimen '+str(i),(x,-.17,-.8+abs(x)*.12))
        a=parent(polygon('leaf','Pressed leaf',leafmat,scale=.67,depth=.025),leaf)
        parent(outline('stem','Stem',gold,scale=.65,r=.016),leaf)
        ghost=polygon('leaf','Exposed leaf impression',ivory,y=-.078,offset=(x,-.8+abs(x)*.12),scale=.67,depth=.01)
        visibility(ghost,0,False);visibility(ghost,7.5,True)
        k(leaf,0,rot=(0,.15*x,0));k(leaf,4,loc=tuple(leaf.location));k(leaf,7,loc=(x+6,-1,5+i*.4),rot=(0,.8,2+i))
    insect=group('Unexpected many legged impression',(1.35,-.09,-.9))
    parent(polygon('bug','Culprit body',ivory,scale=.7,depth=.02),insect)
    for j in range(5):
        for sign in [-1,1]:parent(line('Culprit legs',[(sign*.09,0,-.3+j*.15),(sign*.28,0,-.45+j*.15),(sign*.4,0,-.36+j*.15)],ivory,.022),insect)
    parent(line('Antennae',[(-.2,0,.65),(0,0,.4),(.2,0,.65)],ivory,.018),insect)
    visibility(insect,0,False);visibility(insect,9,True)
    for o in insect.children:visibility(o,0,False);visibility(o,9,True)
    rinse=mat('Blue rinse glints',(.18,.58,.9),.3,.18,1)
    for i in range(10):
        o=cube('Moving rinse edge',(-3.4+i*.76,-.22,4),(.035,.035,.75),rinse,.015)
        k(o,0,scale=.001);k(o,7,loc=(-3.4+i*.76,-.22,4),scale=1);k(o,10,loc=(-3.4+i*.76,-.22,-3));k(o,11,scale=.001)
    c=cam((0,-15,3),(0,0,1),10)
    for t,loc,target in [(0,(0,-15,3),(0,0,1)),(10,(0,-15,3),(0,0,1)),(14,(1,-12,1.5),(1.1,0,.3))]:camera_key(c,t,loc,target)

def astrolabe():
    stage((.008,.016,.04),-2.1)
    stars=mat('Starlight',(.57,.76,1),0,.2,4)
    for i in range(85):sphere('Background star',(random.uniform(-12,12),6,random.uniform(0,12)),(.018,)*3,stars)
    stand=cube('Astrolabe plinth',(0,.4,-1.6),(3,2,.4),wood)
    for x in [-.8,.8]:cyl('Brass foot',(x,0,-1.4),(x,0,0),.08,gold)
    ring('Outer mater',(0,0,2),3.2,gold,.11)
    ring('Latitude ring',(0,-.02,2),2.85,gold,.025)
    for i in range(72):
        a=i*2*math.pi/72;r=3.02
        line('Engraved angle',[(r*math.cos(a),-.13,2+r*math.sin(a)),((r+.1)*math.cos(a),-.13,2+(r+.1)*math.sin(a))],ivory,.013)
    rete=group('SVG pierced star map',(0,-.18,2));parent(outline('rete','Pierced rete',gold,r=.07),rete)
    for i,(x,z) in enumerate(profiles['rete'][:-1]):parent(sphere('Rete star index',(x,-.03,z),(.09,)*3,stars),rete)
    pointer=group('Predictive alidade',(0,-.38,2));parent(polygon('pointer','Alidade SVG',gold,depth=.06),pointer)
    parent(cyl('Pointer spindle',(0,-.15,0),(0,.15,0),.19,gold),pointer)
    for t,ang in [(0,-1.4),(5,.7),(7,.95),(14,.95)]:k(pointer,t,rot=(0,ang,0))
    for t,ang in [(0,.6),(7,-.4),(14,-.4)]:k(rete,t,rot=(0,ang,0))
    # Same declared angle determines the sky target and the pointer's endpoint.
    x,z=3.1*math.sin(.95),2+3.1*math.cos(.95)
    star=sphere('Predicted rising star',(x,-.4,-1),(.11,)*3,stars)
    for t,zz in [(0,-1),(7,-1),(10,z),(14,z)]:k(star,t,loc=(x,-.4,zz))
    horizon=line('Workshop roof horizon',[(-8,2,1.4),(8,2,1.4)],dark,.09)
    c=cam((.3,-17,5),(0,0,2),14.3)
    camera_key(c,0,(.3,-17,5),(0,0,2));camera_key(c,10,(0,-17,4),(0,0,2));camera_key(c,14,(.6,-20,5),(0,1,2.7))

def peacock():
    stage((.12,.12,.13),-1.8)
    shell=mat('Beetle shell iridescence',(.018,.02,.025),.85,.19)
    n=shell.node_tree.nodes;links=shell.node_tree.links
    geo=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT'
    absolute=n.new('ShaderNodeMath');absolute.operation='ABSOLUTE'
    facing=n.new('ShaderNodeMath');facing.operation='SUBTRACT';facing.inputs[0].default_value=1
    links.new(geo.outputs['Incoming'],dot.inputs[0]);links.new(geo.outputs['Normal'],dot.inputs[1]);links.new(dot.outputs['Value'],absolute.inputs[0]);links.new(absolute.outputs[0],facing.inputs[1])
    ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1]);ramp.color_ramp.elements[0].position=0;ramp.color_ramp.elements[0].color=(.008,.009,.015,1)
    for pos,col in [(.05,(.008,.009,.015,1)),(.10,(.015,.55,.19,1)),(.18,(.22,.015,.6,1)),(.3,(.015,.4,.5,1)),(.6,(.01,.3,.12,1)),(1,(.01,.015,.02,1))]:ramp.color_ramp.elements.new(pos).color=col
    links.new(facing.outputs[0],ramp.inputs[0]);links.new(ramp.outputs[0],n['Principled BSDF'].inputs['Base Color'])
    jacket=polygon('jacket','SVG beetle jacket',shell,offset=(0,1),scale=.92,depth=.65)
    outline('jacket','Gold jacket piping',gold,y=-.35,offset=(0,1),scale=.92,r=.018)
    polygon('lapel','Silk lapel',black,y=-.36,offset=(0,1),scale=.92,depth=.03)
    cyl('Mannequin spindle',(0,0,-1.5),(0,0,-.6),.07,gold);sphere('Display base',(0,0,-1.65),(1,.8,.12),black)
    sphere('Headless collar',(0,0,3.05),(.35,.28,.08),gold)
    a=person('Doorman',(-3,0,-1.7),dark,1.2);b=person('Hostess',(3,0,-1.7),ivory,1.2)
    for t in range(15):
        ang=-.8+1.6*min(t/8,1)
        k(a,t,loc=(-3*math.cos(ang),2*math.sin(ang),-1.7),rot=(0,0,-ang))
        k(b,t,loc=(3*math.cos(ang),-2*math.sin(ang),-1.7),rot=(0,0,ang))
    medal=sphere('Best dressed medal',(-.55,-.48,1.9),(.25,.07,.25),gold)
    k(medal,0,scale=.001);k(medal,9,scale=.001);k(medal,10,scale=1)
    tag=text('BEST',(-.55,-.57,1.9),.12,black);k(tag,0,scale=.001);k(tag,9,scale=.001);k(tag,10,scale=1)
    exit=text('EXIT  >',(3,-.8,1.55),.4,red);k(exit,0,scale=.001);k(exit,10,scale=.001);k(exit,11,scale=1)
    c=cam((-.2,-14,4),(0,0,.8),11)
    for t,loc in [(0,(-.2,-14,4)),(4,(-.2,-14,4)),(9,(7,-11,4)),(14,(7,-11,4))]:camera_key(c,t,loc,(0,0,.8))

def marbling():
    stage((.12,.035,.025),-2)
    cube('Gilded marbling tray',(0,.2,.5),(8,.3,5.7),gold,.18)
    cube('Dark pigment bath',(0,-.02,.52),(7.6,.12,5.3),teal,.1)
    pink=mat('Vermilion floating pigment',(.7,.07,.035),.2,.2)
    cream=mat('Cream floating pigment',(.85,.63,.32),.1,.25)
    ink=polygon('profile','Minister profile in pigment',pink,y=-.12,offset=(-.3,.6),scale=.85,depth=.025)
    for i in range(12):
        pts=[]
        for j in range(90):
            a=j/89*2*math.pi;r=.65+i*.19
            pts.append((r*math.cos(a)+.2*math.sin(3*a),-.14-i*.001,.6+r*.65*math.sin(a)))
        o=line('Combed pigment filament '+str(i),pts,cream if i%2 else pink,.022)
        for t,ang in [(0,0),(4,0),(5,.07*(-1)**i),(7,.04*(-1)**i),(14,.04*(-1)**i)]:k(o,t,rot=(0,ang,0))
    for i in range(3):
        chin=sphere('Accidental chin '+str(i),(1.0,-.18,-.1-i*.23),(.35,.035,.18),pink)
        k(chin,0,scale=.001);k(chin,4.3,scale=.001);k(chin,5+i*.15,scale=1)
    official=person('Offended minister',(4,1,-1.8),red,1.3)
    k(official,0,loc=(5.5,1,-1.8));k(official,7,loc=(5.5,1,-1.8));k(official,9,loc=(3.8,-.3,-1.8),rot=(.15,0,-.22))
    sheet=group('Lifted fixed print',(0,-.3,.5))
    parent(cube('Ivory impression',(0,0,0),(7,.08,4.8),ivory,.02),sheet)
    parent(polygon('profile','Fixed caricature',pink,y=-.08,offset=(-.3,0),scale=.85,depth=.02),sheet)
    for i in range(3):parent(sphere('Printed extra chin',(1,-.09,-.5-i*.23),(.35,.03,.18),pink),sheet)
    for t,loc,sc in [(0,(0,-.3,.5),.001),(9,(0,-.3,.5),.001),(10,(0,-.3,.5),1),(14,(0,-1,1.8),1)]:k(sheet,t,loc=loc,scale=sc)
    c=cam((0,-16,7),(0,0,.8),13)
    camera_key(c,0,(0,-16,7),(0,0,.8));camera_key(c,14,(1,-15,5),(.5,-.2,1.2))

def bronze():
    stage((.018,.022,.03),-2)
    mold=mat('Refractory cutaway',(.12,.15,.18),.2,.65)
    bronze=mat('Molten bronze',(.9,.17,.015),.55,.23,1.8)
    cool=mat('Finished bronze',(.5,.22,.065),.85,.25)
    polygon('horse','Horse negative volume rim',mold,y=.25,offset=(0,-.7),scale=1.15,depth=.65)
    outline('horse','Illuminated cavity contour',gold,y=-.12,offset=(0,-.7),scale=1.15,r=.045)
    casting=polygon('horse','Advancing bronze casting',bronze,y=-.18,offset=(0,-.7),scale=1.08,depth=.2)
    # A world-position mask exposes the same SVG cavity progressively.
    nodes=bronze.node_tree.nodes;links=bronze.node_tree.links
    geo=nodes.new('ShaderNodeNewGeometry');sep=nodes.new('ShaderNodeSeparateXYZ');less=nodes.new('ShaderNodeMath');less.operation='LESS_THAN'
    trans=nodes.new('ShaderNodeBsdfTransparent');mix=nodes.new('ShaderNodeMixShader');out=nodes['Material Output'];bsdf=nodes['Principled BSDF']
    links.new(geo.outputs['Position'],sep.inputs[0]);links.new(sep.outputs['Z'],less.inputs[0]);links.new(less.outputs[0],mix.inputs[0]);links.new(trans.outputs[0],mix.inputs[1]);links.new(bsdf.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs[0])
    for t,height in [(0,-2),(3,-1.7),(8,2.5),(10,3.6),(14,4)]:less.inputs[1].default_value=height;less.inputs[1].keyframe_insert(data_path='default_value',frame=1+t*24)
    vent=outline('vent','Ear air escape vent',ivory,y=-.2,offset=(0,-.7),scale=1.15,r=.07)
    bubble=sphere('Last trapped air pocket',(-1.8,-.45,-.1),(.18,.07,.18),ivory)
    for t,loc,sc in [(0,(-1.8,-.45,-.8),1),(4,(-1,-.45,.2),1),(7,(.2,-.45,1.2),1),(9,(1.4,-.45,3.1),.7),(10.5,(1.6,-.45,4.6),.2),(11,(1.6,-.45,5),.001)]:k(bubble,t,loc=loc,scale=sc)
    final=polygon('horse','Complete cooled horse',cool,y=-.3,offset=(0,-.7),scale=1.08,depth=.5)
    visibility(final,0,False);visibility(final,11.5,True)
    for t,loc in [(0,(0,0,0)),(11,(0,0,0)),(14,(0,2,0))]:k(s.objects['Horse negative volume rim'],t,loc=loc)
    cube('Foundry plinth',(0,0,-1.85),(7,3,.3),black)
    c=cam((.6,-16,6),(0,0,1.2),13.8)
    camera_key(c,0,(.6,-16,6),(0,0,1.2));camera_key(c,11,(0,-16,4),(0,0,1.4));camera_key(c,14,(2,-16,5),(0,0,1.2))

def panorama():
    stage((.055,.025,.018),-2)
    cube('Panorama mahogany box',(0,.4,1),(8,1.2,5.3),wood,.18)
    cube('Bare linen window',(0,-.25,1),(7,.08,4.1),ivory,.02)
    # Front side bars occlude the finite painted strip as it runs off the reel.
    scroll=group('Finite painted scroll',(0,-.34,1))
    sky=mat('Painted dusk',(.055,.19,.28),0,.7)
    parent(cube('Finite blue painted ground',(0,0,0),(16,.04,3.9),sky,.01),scroll)
    parent(outline('mountains','SVG painted mountain range',teal,y=-.05,scale=.85,r=.1),scroll)
    parent(outline('track','Railway horizon',gold,y=-.09,scale=.85,r=.022),scroll)
    for i in range(13):
        x=-7+i*1.1
        parent(cube('Painted track tie',(x,-.1,-1.5),(.035,.025,.22),ivory,.01),scroll)
    parent(cube('Their station',(-.5,-.08,-.3),(1.5,.04,1.1),ivory,.01),scroll)
    parent(outline('roof','Station roof',red,y=-.14,offset=(-.5,.25),r=.06),scroll)
    parent(text('STATION',(-.5,-.15,-.2),.18,dark),scroll)
    for i in range(20):parent(cube('Stitched last handspan',(8,-.12,-1.8+i*.19),(.045,.02,.08),wood,.01),scroll)
    for painted in scroll.children:clip_painted_scroll(painted)
    for t,x in [(0,-1),(5,-2),(9,-5),(12,-12),(14,-12)]:k(scroll,t,loc=(x,-.34,1))
    for x in [-4.3,4.3]:cube('Opaque panorama side',(x,-.5,1),(1.6,.6,5.3),wood,.12)
    for z in [-1.3,3.3]:cube('Panorama border',(0,-.6,z),(7.5,.45,.55),gold,.06)
    crank=group('Hand crank',(4.8,-.2,.2));parent(cyl('Crank axle',(0,0,0),(0,-.8,0),.12,gold),crank)
    parent(cyl('Crank arm',(0,-.8,0),(0,-.8,.65),.07,gold),crank);parent(sphere('Crank handle',(0,-1,.65),(.12,.3,.12),wood),crank)
    for t,a in [(0,0),(9,12),(12,14),(14,14)]:k(crank,t,rot=(0,a,0))
    viewer=person('Widow at the window',(-4.3,-1.4,-1.85),black,1.25)
    for t,ang in [(0,0),(8,-.12),(10,-.18),(14,0)]:k(viewer,t,rot=(ang,0,.1))
    c=cam((1,-18,5),(.3,0,1),13)
    camera_key(c,0,(1,-18,5),(.3,0,1));camera_key(c,14,(0,-17,4),(0,0,1))

def lenticular():
    stage((.07,.04,.065),-2)
    picture=group('Rocked lenticular family frame',(0,0,1.2))
    parent(cube('Portrait field',(0,0,0),(8,.18,5.7),dark),picture)
    for x in [-4.2,4.2]:parent(cube('Gilded portrait side',(x,-.15,0),(.35,.4,6.4),gold),picture)
    for z in [-3,3]:parent(cube('Gilded portrait top',(0,-.15,z),(8.7,.4,.35),gold),picture)
    for i,x in enumerate([-2.5,-.8,.8,2.5]):
        p=person('Approved adult '+str(i),(x,-.3,-2.1),teal if i%2 else red,1.2);parent(p,picture)
        for t,a in [(0,-.18),(5,.18),(8,-.18),(14,-.18)]:k(p,t,rot=(0,0,a*(-1)**i))
    child=group('Unauthorized SVG child',(0,-.8,-1.5));parent(child,picture)
    parent(polygon('child','Child SVG silhouette',ivory,scale=.75,depth=.2),child)
    parent(sphere('Child head',(0,-.01,.86),(.21,.18,.25),wood),child)
    for x in [-.14,.14]:parent(cyl('Child shoe',(x,0,-.8),(x,-.15,-.9),.08,black),child)
    for t,loc in [(0,(0,-.8,-1.5)),(8,(0,-.8,-1.5)),(10.5,(0,-1.0,-1.8)),(12,(.7,-1.3,-2.8)),(14,(1.5,-1.6,-3.3))]:k(child,t,loc=loc)
    # Actual cylindrical lenticular ribs catch alternating view highlights.
    rib=mat('Lenticular glass ribs',(.12,.2,.27),.5,.18)
    for i in range(55):parent(cyl('Lenticular optical rib',(-3.9+i*.144,-.52,-2.8),(-3.9+i*.144,-.52,2.8),.012,rib),picture)
    for t,a in [(0,-.20),(5,.20),(8,-.03),(11,.03),(14,.03)]:k(picture,t,rot=(0,0,a))
    cube('Table beyond the frame',(0,-1,-2.1),(12,4,.25),wood)
    hand=sphere('Cleaner rocking hand',(4.5,-.5,.1),(.55,.3,.2),wood)
    k(hand,0,loc=(6,-.5,.1));k(hand,7,loc=(4.5,-.5,.1));k(hand,14,loc=(4.5,-.5,.1))
    c=cam((-3,-18,5),(0,0,1),12.5)
    camera_key(c,0,(-3,-18,5),(0,0,1));camera_key(c,6,(3,-18,5),(0,0,1));camera_key(c,10,(0,-18,4),(0,0,1));camera_key(c,14,(0,-18,3),(0,-.5,.7))

def weaving():
    stage((.04,.05,.075),-2)
    indigo=mat('Indigo silk',(.025,.04,.19),.25,.36)
    copper=mat('Copper silk',(.72,.26,.055),.45,.3)
    for x in [-4.4,4.4]:cube('Loom upright',(x,.3,.5),(.35,.6,6),wood,.1)
    for z in [-2,3.2]:cyl('Loom roller',(-4.4,.2,z),(4.4,.2,z),.18,gold)
    cuff=group('One cloth front and reverse',(0,-.25,.8))
    for i in range(65):
        x=-3.7+i*.116
        parent(line('Continuous warp '+str(i),[(x,0,-2.2),(x,0,2.2)],indigo,.03),cuff)
    for j in range(40):
        z=-2.1+j*.108
        points=[(-3.75+i*.117,(-.035 if (i+j)%2 else .035),z) for i in range(65)]
        o=parent(line('Crossing weft '+str(j),points,copper if j%3==0 else indigo,.03),cuff)
        k(o,0,scale=.001);k(o,1+j*.16,scale=.001);k(o,1.25+j*.16,scale=1)
    for x in [-2.4,0,2.4]:parent(outline('flower','Regulation face flower',copper,y=-.075,offset=(x,.25),scale=.62,r=.025),cuff)
    for role,x in [('B',2.35),('Y',0),('E',-2.3)]:
        # Reverse float follows the same cloth as it turns, revealing the letters.
        o=line('Reverse floating letter '+role,[(x-.65*xx,.11,-.8+.65*zz) for xx,zz in profiles[role]],ivory,.045)
        parent(o,cuff)
    for t,a in [(0,0),(8,0),(11,math.pi),(14,math.pi)]:k(cuff,t,rot=(0,0,a))
    shuttle=cube('Ivory shuttle',(-4,-.5,1),(1,.28,.25),ivory,.1)
    for i in range(17):k(shuttle,i*.45,loc=((1 if i%2 else -1)*3.9,-.5,1))
    k(shuttle,9,loc=(4,-.5,1))
    for x,sign in [(-4,-1),(4,1)]:
        hand=sphere('Sister hand',(x,-1,-.5),(.65,.3,.22),wood)
        k(hand,0,loc=(x+sign*2,-1,-.5));k(hand,11,loc=(x+sign*2,-1,-.5));k(hand,14,loc=(x*.8,-1,-.5))
    c=cam((.3,-17,6),(0,0,.5),12)
    camera_key(c,0,(.3,-17,6),(0,0,.5));camera_key(c,14,(0,-16,4),(0,-.2,.5))

def water():
    stage((.12,.17,.2),-2)
    clay=mat('Terracotta',(.52,.16,.07),0,.67)
    plaster=[mat('Peach plaster',(.73,.39,.21),0,.8),mat('Sea blue plaster',(.12,.37,.43),0,.8),mat('Ochre plaster',(.57,.40,.13),0,.8)]
    aqua=mat('Water ribbon',(.025,.46,.65),.55,.17, .25)
    points=profiles['channel']
    for i,(x,z) in enumerate([(-3.2,3),(1,2),(-.4,.8)]):
        cube('Terraced retaining foundation '+str(i),(x,1,(z-1.15-2)/2),(3.2,2.4,z+.85),plaster[i],.05)
        cube('Terraced home '+str(i),(x,1,z-.35),(3.2,2.4,1.6),plaster[i],.08)
        cube('Balcony '+str(i),(x,-.65,z-.75),(3.6,1.2,.14),ivory,.04)
        for xx in [x-.65,x+.65]:cube('House window',(xx,-.23,z),(.4,.06,.6),dark,.03)
        person('Householder '+str(i),(x+1,-.8,z-.65),teal,.47)
    for i,(a,b) in enumerate(zip(points,points[1:])):
        x1,z1=a;x2,z2=b
        line('Clay water channel '+str(i),[(x1,-1.45,z1),(x2,-1.45,z2)],clay,.12)
        flow=line('Passing water '+str(i),[(x1,-1.58,z1+.03),(x2,-1.58,z2+.03)],aqua,.055)
        start=[1,2.5,3.3,4.5,5.3,6.5,7.3,8.1][i]
        for t,v in [(0,0),(start,0),(start+.65,1),(14,1)]:flow.data.bevel_factor_end=v;flow.data.keyframe_insert(data_path='bevel_factor_end',frame=1+t*24)
    for i,idx in enumerate([1,3,5]):
        x,z=points[idx];gate=cube('Independent tilted gate '+str(i),(x,-1.55,z+.12),(.55,.18,.08),clay,.03)
        for t,a in [(0,-.3),(2+i*2,-.3),(2.5+i*2,.5),(14,.5)]:k(gate,t,rot=(0,a,0))
    bath=sphere('Last balcony dry birdbath',(2,-1.5,-1.1),(.9,.65,.17),ivory)
    cyl('Birdbath stone pedestal',(2,-1.5,-2),(2,-1.5,-1.15),.15,ivory)
    pool=sphere('Filled birdbath',(2,-1.5,-.99),(.75,.53,.055),aqua)
    k(pool,0,scale=.001);k(pool,7.8,scale=.001);k(pool,9,scale=1)
    bird=group('Bird returns the gift',(2,-1.9,-.65));parent(polygon('bird','SVG bird',dark,scale=.5,depth=.17),bird)
    wing=parent(polygon('wing','SVG beating wing',teal,scale=.6,depth=.1),bird)
    for t in [i/6 for i in range(85)]:
        u=max(0,min((t-10.3)/3.7,1))
        k(bird,t,loc=(2-6*u,-1.9+.4*u,-.65+5*u),rot=(0,0,-.3*math.sin(t*2) if 9.3<t<10.3 else 0))
        k(wing,t,rot=(math.sin(t*12)*.7 if t>10.3 else 0,0,0))
    c=cam((2,-17,9),(0,0,1),12.5)
    camera_key(c,0,(2,-17,9),(-.5,0,1.5));camera_key(c,9,(2,-16,7),(0,0,.5));camera_key(c,14,(2,-17,9),(-.5,0,1.5))

{1:whale,3:cyanotype,4:astrolabe,7:peacock,9:marbling,15:bronze,19:panorama,25:lenticular,28:weaving,30:water}[cfg['concept_id']]()

# Save all animation and inputs. This scene needs no Python handler to play.
s['concept_id']=cfg['concept_id'];s['svg_sha256']=hashlib.sha256((SOURCE/'design.svg').read_bytes()).hexdigest()
s['timeline_sha256']=hashlib.sha256((SOURCE/'timeline.json').read_bytes()).hexdigest();s['story_beats']=json.dumps(cfg['story_beats'])
s.frame_set(1);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'scene.blend'))
receipt={'concept_id':cfg['concept_id'],'blender':bpy.app.version_string,'engine':s.render.engine,'frames':s.frame_end,'fps':s.render.fps,
         'resolution':[s.render.resolution_x,s.render.resolution_y],'svg_roles':list(profiles),'svg_sha256':s['svg_sha256'],
         'timeline_sha256':s['timeline_sha256'],'objects':len(s.objects),'scene_sha256':hashlib.sha256((SOURCE/'scene.blend').read_bytes()).hexdigest(),
         'scope':'Baked editable scene. Preview and encoded-film review are separate stages.'}
(P/'receipts/scene.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
if args.preview or args.frame is not None:
    s.render.resolution_x=args.width or 640;s.render.resolution_y=round(s.render.resolution_x*9/16)
    for f in ([args.frame] if args.frame else [1,97,169,241,336]):
        s.frame_set(f);s.render.filepath=str(P/'previews'/f'preview-{f:04}.png');bpy.ops.render.render(write_still=True)
elif args.render:
    if args.width:s.render.resolution_x=args.width;s.render.resolution_y=round(args.width*9/16)
    (P/'frames').mkdir(exist_ok=True);s.render.filepath=str(P/'frames'/'frame_');bpy.ops.render.render(animation=True)
print('ANTHOLOGY_SCENE_OK',cfg['concept_id'],flush=True)
