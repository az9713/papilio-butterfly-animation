"""Compare preserved and rebuilt geometry with explicit numerical tolerance."""
import bpy
import json
from pathlib import Path
import sys

paths=[Path(value) for value in sys.argv[sys.argv.index('--')+1:]]
snapshots=[]
for path in paths:
    bpy.ops.wm.open_mainfile(filepath=str(path.resolve()))
    scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
    values={}
    for obj in scene.objects:
        if obj.type=='MESH':
            values[obj.name]={'type':obj.type,'points':[list(vertex.co) for vertex in obj.data.vertices],
                             'faces':[list(poly.vertices) for poly in obj.data.polygons],
                             'world_matrix':[list(row) for row in obj.matrix_world]}
        elif obj.type=='CURVE':
            values[obj.name]={'type':obj.type,'points':[list(point.co) for spline in obj.data.splines for point in spline.points],
                             'faces':[],'world_matrix':[list(row) for row in obj.matrix_world]}
    snapshots.append(values)
a,b=snapshots
def canonical_faces(faces):
    return sorted(min(tuple(face[i:]+face[:i]) for i in range(len(face))) for face in faces)
report={'same_objects':set(a)==set(b),'differences':[],'max_coordinate_error':0.,'max_world_matrix_error':0.}
for name in sorted(set(a)&set(b)):
    x,y=a[name],b[name]
    point_count=len(x['points'])==len(y['points'])
    error=max((abs(p-q) for u,v in zip(x['points'],y['points']) for p,q in zip(u,v)),default=0.) if point_count else None
    matrix=max(abs(p-q) for u,v in zip(x['world_matrix'],y['world_matrix']) for p,q in zip(u,v))
    faces=canonical_faces(x['faces'])==canonical_faces(y['faces'])
    if error is None or error or matrix or not faces:
        report['differences'].append({'object':name,'same_point_count':point_count,'same_faces':faces,
                                      'max_coordinate_error':error,'max_world_matrix_error':matrix})
    if error is not None:report['max_coordinate_error']=max(report['max_coordinate_error'],error)
    report['max_world_matrix_error']=max(report['max_world_matrix_error'],matrix)
report['equivalent_within_1e-5']=(report['same_objects'] and report['max_coordinate_error']<1e-5 and
    report['max_world_matrix_error']<1e-5 and all(d['same_point_count'] and d['same_faces'] for d in report['differences']))
print('GEOMETRY_COMPARISON '+json.dumps(report),flush=True)
