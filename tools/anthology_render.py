"""Bounded, restartable local Blender render runner, one GPU process at a time."""
from pathlib import Path
import argparse,datetime,json,shutil,subprocess,time
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
BLENDER='C:/Program Files/Blender Foundation/Blender 5.3/blender.exe'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--ids',nargs='*',type=int);args=parser.parse_args()
    plans=json.loads((ROOT/'production/anthology/selection.json').read_text(encoding='utf8'))
    if args.ids:plans=[p for p in plans if p['concept_id'] in args.ids]
    work=ROOT/'.publication-work';work.mkdir(exist_ok=True)
    for p in plans:
        path=ROOT/'projects'/p['slug'];shutil.copyfile(ROOT/'tools/anthology_scene.py',path/'source/build_scene.py')
        phase='preview' if args.preview else 'render';log=work/f"{p['slug']}-{phase}.log";start=time.monotonic()
        command=[BLENDER,'--background','--factory-startup','--threads','4','--python',str(path/'source/build_scene.py'),'--','--preview' if args.preview else '--render']
        print('START',p['concept_id'],p['slug'],phase,flush=True)
        with log.open('w',encoding='utf8') as out:result=subprocess.run(command,stdout=out,stderr=subprocess.STDOUT)
        content=log.read_text(encoding='utf8',errors='replace')
        record={'phase':phase,'concept_id':p['concept_id'],'exit_code':result.returncode,'success_marker':f"ANTHOLOGY_SCENE_OK {p['concept_id']}" in content,
                'elapsed_seconds':round(time.monotonic()-start,2),'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        (path/'receipts'/f'{phase}.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
        if result.returncode or not record['success_marker']:raise RuntimeError(f"{p['slug']} failed, inspect its local render log")
        if args.preview:
            sheet=Image.new('RGB',(640*3,360*2+40),'#151c20');draw=ImageDraw.Draw(sheet)
            for i,image in enumerate(sorted((path/'previews').glob('preview-*.png'))):
                im=Image.open(image).convert('RGB').resize((640,360));sheet.paste(im,((i%3)*640,(i//3)*380))
                draw.text(((i%3)*640+10,(i//3)*380+342),f"{p['title']} | frame {image.stem.split('-')[-1]}",fill='white')
            sheet.save(path/'previews/storyboard.jpg',quality=90)
        else:
            from anthology_finish import finish
            finish(path)
        print('DONE',p['concept_id'],record['elapsed_seconds'],flush=True)

if __name__=='__main__':main()
