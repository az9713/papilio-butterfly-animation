"""Render an explicitly selected saved scene; never infer the desired revision."""
import argparse
import bpy
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from pipeline_common import (configure_device, sha256, path_label, png_size,
                             receipt, receipt_path, write_json)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--device',choices=['auto','cpu','optix','cuda','hip','metal','oneapi'],default='auto')
    parser.add_argument('--engine',choices=['CYCLES','BLENDER_EEVEE'])
    parser.add_argument('--samples',type=int)
    parser.add_argument('--frame-start',type=int)
    parser.add_argument('--frame-end',type=int)
    parser.add_argument('--plan',action='store_true',help='Inspect selection and effective settings without writing outputs')
    args=parser.parse_args(argv)
    source=args.scene.resolve()
    if not source.is_file() or source.suffix.lower()!='.blend':
        parser.error('--scene must identify an existing .blend file')
    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene=bpy.context.scene
    original_range=[scene.frame_start,scene.frame_end]
    start=args.frame_start if args.frame_start is not None else original_range[0]
    end=args.frame_end if args.frame_end is not None else original_range[1]
    if not original_range[0]<=start<=end<=original_range[1]:
        parser.error('Requested frames must be within the selected scene range')
    if args.engine:scene.render.engine=args.engine
    if args.samples is not None:
        if args.samples<1:parser.error('--samples must be positive')
        scene.cycles.samples=args.samples
    device=configure_device(scene,args.device)
    spec={'schema_version':1,'scene':path_label(source),'scene_sha256':sha256(source),
          'revision':scene.get('papilio_revision',source.stem),
          'frame_range':original_range,'fps':scene.render.fps/scene.render.fps_base,
          'resolution':[round(scene.render.resolution_x*scene.render.resolution_percentage/100),
                        round(scene.render.resolution_y*scene.render.resolution_percentage/100)],
          'engine':scene.render.engine,'samples':scene.cycles.samples,
          'device':device,'denoiser':scene.cycles.denoiser,
          'seed':scene.cycles.seed,'color_mode':'RGB','color_depth':'8'}
    if args.plan:
        report=receipt('render-plan',render_spec=spec,requested_frame_range=[start,end],
                       output=path_label(args.output))
        print('PAPILIO_RENDER_PLAN '+json.dumps(report),flush=True)
        return report
    folder=args.output.resolve()
    folder.mkdir(parents=True,exist_ok=True)
    manifest=folder/'render-manifest.json'
    existing=list(folder.glob('frame_*.png'))
    if manifest.exists():
        if json.loads(manifest.read_text())!=spec:
            raise RuntimeError('Source scene or render settings changed; use a distinct output directory.')
    elif existing:
        raise RuntimeError('Existing frames have no render manifest; use a distinct output directory.')
    else:write_json(manifest,spec)
    allowed={f'frame_{frame:04d}.png' for frame in range(original_range[0],original_range[1]+1)}
    for path in existing:
        if path.name not in allowed or png_size(path)!=spec['resolution']:
            raise RuntimeError('Existing frame is invalid for the selected scene: '+path.name)
    scene.frame_start=start;scene.frame_end=end
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
    scene.render.use_overwrite=False;scene.render.use_persistent_data=True
    scene.render.filepath=str(folder/'frame_')
    started=time.perf_counter()
    bpy.ops.render.render(animation=True)
    frames=[]
    for frame in range(start,end+1):
        path=folder/f'frame_{frame:04d}.png'
        if not path.is_file() or png_size(path)!=spec['resolution']:
            raise RuntimeError('Rendered sequence is incomplete or invalid: '+path.name)
        frames.append({'file':path.name,'sha256':sha256(path),'bytes':path.stat().st_size})
    report=receipt('render',render_spec=spec,requested_frame_range=[start,end],
                   seconds=round(time.perf_counter()-started,3),
                   previously_present_frames=len(existing),frames=frames,passed=True)
    write_json(receipt_path(folder/'receipts','render'),report)
    print('PAPILIO_RENDER_COMPLETE '+json.dumps(report),flush=True)
    return report


if __name__=='__main__':
    main(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
