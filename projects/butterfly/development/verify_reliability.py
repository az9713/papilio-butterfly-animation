"""Real Blender integration checks; artifacts stay in ignored .reliability-work."""
import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'development'))
from pipeline_common import sha256,write_json,verify_protected_assets
from record_step import run,save


def parse_marker(output,marker):
    return json.loads(next(line[len(marker):] for line in output.splitlines() if line.startswith(marker)))


def check_controls(observed,expected):
    assert observed['project_title']==expected['title']
    assert observed['embedded_config']==expected
    assert observed['resolution']==expected['resolution']
    assert observed['samples']==expected['final_samples']
    assert observed['fps']==expected['fps']
    assert observed['frame_range']==[1,round(expected['duration_seconds']*expected['fps'])]
    for key in ['camera_orbits','root_height','root_tilt_degrees','camera_lens_mm','camera_radius',
                'camera_height','camera_target_height','camera_start_degrees','metal_roughness',
                'enamel_roughness','lighting_revision']:
        assert math.isclose(observed[key],expected[key],abs_tol=1e-4),(key,observed[key],expected[key])
    for sample in observed['observations']:
        t=(sample['frame']-1)/expected['fps']
        for name,angle in sample['wings'].items():
            factor=expected['lower_wing_amplitude_factor'] if 'lower' in name else 1
            target=(expected['wing_rest_degrees']+expected['wing_amplitude_degrees']*factor*
                    math.sin(2*math.pi*t/expected['wing_period_seconds']))
            target=target if name.startswith('Left') else -target
            assert math.isclose(angle,target,abs_tol=1e-3),(name,angle,target)
        energy=1200*(1+expected['light_breath_fraction']*math.sin(2*math.pi*t/expected['light_period_seconds']))
        assert math.isclose(sample['key_light_energy'],energy,abs_tol=.001)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--blender',required=True,type=Path)
    parser.add_argument('--run-id',default='verification-01');args=parser.parse_args()
    work=ROOT/'.reliability-work'/args.run_id
    if work.exists():raise FileExistsError('Preserve previous verification; choose a new --run-id')
    work.mkdir(parents=True)
    counter=10
    def step(label,script,arguments,expect=0):
        nonlocal counter
        counter+=1
        return run(f'{args.run_id}-{counter:03d}-{label}',
                   [args.blender,'--background','--factory-startup','--python-exit-code','1',
                    '--python',ROOT/script,'--',*map(str,arguments)],expected_exit=expect)
    baseline=json.loads((ROOT/'config.json').read_text())
    variants={
        'baseline':baseline,
        'json-controls':{**baseline,'title':'Papilio control verification','duration_seconds':4,'fps':12,
                         'resolution':[320,180],'final_samples':8,'wing_period_seconds':1,
                         'wing_rest_degrees':10,'wing_amplitude_degrees':25,'lower_wing_amplitude_factor':.6,
                         'camera_orbits':2,'camera_radius':15,'camera_height':6.4,'camera_lens_mm':38,
                         'camera_target_height':2.9,'camera_start_degrees':-40,'light_period_seconds':2,
                         'light_breath_fraction':.05,'root_height':3.25,'root_tilt_degrees':68,
                         'metal_roughness':.33,'enamel_roughness':.36,'lighting_revision':1},
        'short-clip':{**baseline,'title':'Disposable verification clip','duration_seconds':2,'fps':6,
                      'resolution':[160,90],'final_samples':2,'wing_period_seconds':1,'light_period_seconds':1},
    }
    results={};scenes={}
    for name,config in variants.items():
        path=work/(name+'.json');write_json(path,config)
        step(name+'-build','build_scene.py',['--stage','final','--tag',name,'--config',path,
             '--output-root',work/'stages','--render','none','--device','cpu'])
        scene=work/'stages'/name/(name+'.blend');scenes[name]=scene
        result=step(name+'-inspect','development/inspect_scene.py',[scene])
        observed=parse_marker(result.stdout,'RELIABILITY_INSPECTION ');check_controls(observed,config)
        results[name]={'scene_sha256':sha256(scene),'observed':observed,'all_controls_passed':True}
    original=step('preserved-scene-inspect','development/inspect_scene.py',[ROOT/'stages/final-v01/final-v01.blend'])
    original=parse_marker(original.stdout,'RELIABILITY_INSPECTION ')
    assert original['geometry_sha256']==results['baseline']['observed']['geometry_sha256']
    overrides=['--res','128','72','--samples','4']
    step('cli-overrides-build','build_scene.py',['--stage','final','--tag','cli-overrides','--config',work/'json-controls.json',
         '--output-root',work/'stages','--render','none','--device','cpu',*overrides])
    override_scene=work/'stages/cli-overrides/cli-overrides.blend'
    result=step('cli-overrides-inspect','development/inspect_scene.py',[override_scene])
    check_controls(parse_marker(result.stdout,'RELIABILITY_INSPECTION '),
                   {**variants['json-controls'],'resolution':[128,72],'final_samples':4})
    invalid={**baseline,'camera_orbits':1.5};write_json(work/'invalid.json',invalid)
    step('invalid-config-rejected','build_scene.py',['--stage','final','--tag','invalid',
         '--config',work/'invalid.json','--output-root',work/'stages','--render','none'],expect=-1)
    assert not (work/'stages/invalid').exists()
    step('missing-revision-rejected','render_saved.py',['--output',work/'should-not-exist'],expect=-1)
    plans=[]
    for name in ['baseline','json-controls']:
        result=step(name+'-selection-plan','render_saved.py',['--scene',scenes[name],
             '--output',work/'plan-only','--device','cpu','--plan'])
        plans.append(parse_marker(result.stdout,'PAPILIO_RENDER_PLAN ')['render_spec'])
    assert plans[0]['scene_sha256']!=plans[1]['scene_sha256'] and not (work/'plan-only').exists()
    for name in ['baseline','json-controls','short-clip']:
        step(name+'-audit','audit_scene.py',[scenes[name],'--output',work/(name+'-audit.json')])
    frames=work/'frames'
    render_args=['--scene',scenes['short-clip'],'--output',frames,'--device','cpu','--samples','1']
    step('cpu-short-render','render_saved.py',render_args)
    before={p.name:sha256(p) for p in frames.glob('frame_*.png')}
    step('safe-resume','render_saved.py',render_args)
    assert before=={p.name:sha256(p) for p in frames.glob('frame_*.png')}
    step('mixed-revision-rejected','render_saved.py',['--scene',scenes['json-controls'],
         '--output',frames,'--device','cpu','--samples','1'],expect=-1)
    bad=work/'corrupt-frames';bad.mkdir()
    shutil.copy2(frames/'render-manifest.json',bad/'render-manifest.json')
    (bad/'frame_0001.png').write_bytes((frames/'frame_0001.png').read_bytes()[:100])
    step('corrupt-frame-rejected','render_saved.py',['--scene',scenes['short-clip'],
         '--output',bad,'--device','cpu','--samples','1'],expect=-1)
    encoded=run(args.run_id+'-040-encode-and-playback',[sys.executable,ROOT/'encode_review.py',frames,
                work/'verification.mp4','--browser-check'])
    movie=parse_marker(encoded.stdout,'PAPILIO_ENCODE_COMPLETE ')
    assert int(movie['metadata']['streams'][0]['nb_read_frames'])==12
    assert float(movie['metadata']['format']['duration'])==2
    run(args.run_id+'-041-existing-export-rejected',[sys.executable,ROOT/'encode_review.py',frames,
                work/'verification.mp4'],expected_exit=-1)
    baseline_receipt=json.loads((ROOT/'development/receipts/001-preserved-baseline.json').read_text())
    preservation=verify_protected_assets(ROOT,baseline_receipt)
    summary={'passed':True,'configuration_fields_checked':sorted(baseline),
             'default_geometry_matches_preserved_scene':True,'json_controls':True,'cli_overrides':True,
             'invalid_configuration_rejected':True,'explicit_revision_selection':True,
             'mixed_revision_resume_rejected':True,'corrupt_frame_rejected':True,
             'cpu_render_resume_and_encoding':True,'short_clip_frames':12,'short_clip_seconds':2,
             'complete_browser_playback':movie['browser_playback'],'protected_assets_unchanged':True,
             'preservation_contract':preservation,
             'test_scope':'Windows, Blender 5.3, CPU rendering, Microsoft Edge; no cross-platform claim.'}
    save(args.run_id+'-099-summary',summary)
    print('RELIABILITY_VERIFIED '+json.dumps(summary),flush=True)


if __name__=='__main__':
    try:main()
    except Exception:
        import traceback
        label=sys.argv[sys.argv.index('--run-id')+1] if '--run-id' in sys.argv else 'verification-01'
        try:save(label+'-098-stopped',{'passed':False,'error':traceback.format_exc()})
        except FileExistsError:pass
        raise
