"""Independent observations of a saved Blender scene for integration receipts."""
import bpy
import hashlib
import json
import math
from pathlib import Path
import sys

path = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(path))
scene = bpy.context.scene
angles = []
observations=[]
for frame in range(scene.frame_start, scene.frame_end + 2):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    angles.append(math.atan2(scene.camera.location.y, scene.camera.location.x))
    observations.append({'frame':frame,'camera':list(scene.camera.location),
                         'wings':{obj.name:math.degrees(obj.rotation_euler.y) for obj in scene.objects
                                  if obj.get('role')=='Animated hinge pivot'},
                         'key_light_energy':bpy.data.lights['Large warm key'].energy})
orbits = sum((b - a + math.pi) % (2 * math.pi) - math.pi
             for a, b in zip(angles, angles[1:])) / (2 * math.pi)
config = json.loads(scene.get('papilio_config_json', '{}'))
quarter = scene.frame_start + config.get('wing_period_seconds', 2) * scene.render.fps / 4
scene.frame_set(math.floor(quarter), subframe=quarter % 1)
hinges = [obj for obj in scene.objects if obj.get('role') == 'Animated hinge pivot']
upper_peak=[math.degrees(obj.rotation_euler.y) for obj in hinges if obj.get('wing_kind')=='upper']
scene.frame_set(scene.frame_start)
camera=scene.camera
forward=camera.rotation_quaternion @ __import__('mathutils').Vector((0,0,-1))
distance=-(camera.location.x*forward.x+camera.location.y*forward.y)/(forward.x**2+forward.y**2)
target_height=camera.location.z+distance*forward.z
root=scene.objects['Sculpture root']
def roughness(name):
    node=next(node for node in bpy.data.materials[name].node_tree.nodes if node.type=='BSDF_PRINCIPLED')
    return node.inputs['Roughness'].default_value
geometry = []
def canonical_faces(faces):
    return sorted(min(tuple(face[i:]+face[:i]) for i in range(len(face))) for face in faces)
for obj in sorted(scene.objects, key=lambda obj: obj.name):
    if obj.type == 'MESH':
        geometry.append([obj.name, [list(vertex.co) for vertex in obj.data.vertices],
                         canonical_faces([list(poly.vertices) for poly in obj.data.polygons])])
    elif obj.type == 'CURVE':
        geometry.append([obj.name, [[[float(v) for v in point.co] for point in spline.points]
                                   for spline in obj.data.splines]])
report = {'checkpoint': path.name, 'project_title': scene.get('papilio_title'),
          'objects': len(scene.objects), 'hinges': len(hinges),
          'resolution': [scene.render.resolution_x, scene.render.resolution_y],
          'samples': scene.cycles.samples, 'camera_orbits': orbits,
          'upper_peak_degrees': upper_peak,
          'fps': scene.render.fps, 'frame_range': [scene.frame_start, scene.frame_end],
          'geometry_sha256': hashlib.sha256(json.dumps(geometry).encode()).hexdigest(),
          'embedded_config': config,
          'root_height':root.location.z,'root_tilt_degrees':math.degrees(root.rotation_euler.x),
          'camera_lens_mm':camera.data.lens,'camera_radius':math.hypot(camera.location.x,camera.location.y),
          'camera_height':camera.location.z,'camera_target_height':target_height,
          'camera_start_degrees':math.degrees(math.atan2(camera.location.y,camera.location.x)),
          'metal_roughness':roughness('Satin machined brass'),
          'enamel_roughness':roughness('Turquoise vitreous enamel'),
          'lighting_revision':2 if scene.objects.get('Rear soft fill') and scene.objects.get('Studio backdrop') else 1,
          'observations':observations,
          'external_images': [image.filepath for image in bpy.data.images
                              if image.source == 'FILE' and not image.packed_file]}
print('RELIABILITY_INSPECTION ' + json.dumps(report), flush=True)
