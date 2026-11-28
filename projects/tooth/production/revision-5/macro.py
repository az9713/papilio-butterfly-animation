"""Build the registered close-up plates from the original Blender mechanism."""
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import json

root = Path(__file__).resolve().parent
scene = bpy.context.scene
scene.frame_set(80)
camera = scene.camera
focus = Vector((-1.73, -.78, .79))
camera.location = focus + Vector((.17, -4.2, 5.1))
camera.rotation_euler = (focus-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.55
scene.render.resolution_x, scene.render.resolution_y = 960,540
scene.render.resolution_percentage = 100
scene.cycles.samples = 20
scene.cycles.use_denoising = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
tooth = scene.objects['Comb tooth 03']
tooth.animation_data_clear()
bpy.context.view_layer.update()
for obj in scene.objects:
    if 'forceps' in obj.name.lower(): obj.hide_render = True
metal = tooth.active_material.node_tree.nodes.get('Principled BSDF')
metal.inputs['Base Color'].default_value=(.95,.19,.055,1)
metal.inputs['Metallic'].default_value=.67
metal.inputs['Roughness'].default_value=.27
pos=tooth.matrix_world @ Vector((0,-.25,.028))
r=world_to_camera_view(scene,camera,pos)
(root/'registration.json').write_text(json.dumps({'grip_pixel':[round(r.x*960,2),round((1-r.y)*540,2)]}))
bpy.context.preferences.filepaths.save_version=0
scene.render.filepath='//macro-preview.png'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'macro.blend'))
def render(name):
    scene.render.filepath=str(root/name)
    bpy.ops.render.render(write_still=True)
tooth.hide_render=True
render('empty.png')
tooth.hide_render=False
for o in scene.objects:
    if o.type=='MESH' and o != tooth: o.hide_render=True
scene.render.film_transparent=True
render('tooth.png')
