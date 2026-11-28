"""Verify all source archives outside Git using retained audio and scene rebuilds."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,tempfile,zipfile
import cv2,numpy as np

ROOT=Path(__file__).resolve().parents[1]
BLENDER='C:/Program Files/Blender Foundation/Blender 5.3/blender.exe'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    args=argparse.ArgumentParser();args.add_argument('--ids',nargs='*',type=int);args=args.parse_args()
    plans=json.loads((ROOT/'production/anthology/selection.json').read_text(encoding='utf8'))
    if args.ids:plans=[p for p in plans if p['concept_id'] in args.ids]
    records=[]
    for p in plans:
        project=ROOT/'projects'/p['slug'];receipt=json.loads((project/'receipts/source-package.json').read_text(encoding='utf8'));archive=project/receipt['archive']
        assert sha(archive)==receipt['sha256']
        with tempfile.TemporaryDirectory(prefix='svg-film-source-',delete=False) as folder:
            dest=Path(folder);assert not (dest/'.git').exists()
            (ROOT/'.publication-work'/f"{p['slug']}-source-location.json").write_text(json.dumps({'folder':folder}),encoding='utf8')
            with zipfile.ZipFile(archive) as z:
                assert z.testzip() is None
                assert set(z.namelist())==set(receipt['members'])
                for name,expected in receipt['members'].items():
                    assert (dest/name).resolve().is_relative_to(dest.resolve())
                    assert hashlib.sha256(z.read(name)).hexdigest()==expected
                z.extractall(dest)
            original_mix=sha(dest/'audio/mix.wav')
            subprocess.run(['python',str(dest/'source/mix_audio.py')],check=True,stdout=subprocess.DEVNULL)
            assert sha(dest/'audio/mix.wav')==original_mix,'Retained-stem mix rebuild differs'
            audit=ROOT/'tools/anthology_scene_audit.py'
            def command(args,log):
                with (ROOT/'.publication-work'/log).open('w',encoding='utf8') as out:
                    result=subprocess.run([BLENDER,'--background','--factory-startup','--threads','2','--python-exit-code','13']+args,stdout=out,stderr=subprocess.STDOUT)
                assert result.returncode==0,(p['slug'],log)
                content=(ROOT/'.publication-work'/log).read_text(encoding='utf8',errors='replace')
                assert 'SCENE_AUDIT_OK' in content or 'ANTHOLOGY_SCENE_OK' in content,(p['slug'],log,'missing success marker')
            command([str(dest/'source/scene.blend'),'--python',str(audit),'--',str(dest/'source'),str(dest/'before.json')],p['slug']+'-source-before.log')
            command(['--factory-startup','--python',str(dest/'source/build_scene.py'),'--','--frame','241','--width','1280'],p['slug']+'-source-rebuild.log')
            command([str(dest/'source/scene.blend'),'--python',str(audit),'--',str(dest/'source'),str(dest/'after.json')],p['slug']+'-source-after.log')
            before=json.loads((dest/'before.json').read_text(encoding='utf8'));after=json.loads((dest/'after.json').read_text(encoding='utf8'))
            assert before==after,(p['slug'],'Baked scene and source rebuild differ')
            rebuilt=cv2.imread(str(dest/'previews/preview-0241.png'));assert rebuilt is not None
            capture=cv2.VideoCapture(str(project/'film.mp4'));capture.set(cv2.CAP_PROP_POS_FRAMES,240);ok,encoded=capture.read();capture.release();assert ok
            mean_difference=float(np.mean(abs(rebuilt.astype(float)-encoded.astype(float))))
            assert mean_difference<2.5,(p['slug'],'Rebuilt hero frame differs from encoded film',mean_difference)
            assert sha(dest/'film.mp4')==sha(project/'film.mp4')
            result={'passed':True,'concept_id':p['concept_id'],'archive_sha256':receipt['sha256'],'members':len(receipt['members']),
                    'outside_git':True,'retained_audio_mix_byte_identical':True,'geometry_and_sampled_motion_identical':True,'scene_audit':after,
                    'rebuilt_hero_frame_mean_pixel_difference_from_encoded':mean_difference,
                    'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'scope':'Every ZIP member verified. Retained stems re-mixed byte for byte. Blender geometry and transforms at frames 1,169,336 rebuilt identically outside Git. A full-resolution hero frame was rerendered and compared with the encoded film. Full image sequence was not rerendered in this package test.'}
            (project/'receipts/source-package-test.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');records.append(result)
            print('SOURCE_PACKAGE_OK',p['concept_id'],flush=True)
    (ROOT/'publication/anthology-source-tests.json').write_text(json.dumps({'passed':True,'projects':records},indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
