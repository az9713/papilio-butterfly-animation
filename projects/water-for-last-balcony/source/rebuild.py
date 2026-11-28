"""Rebuild locally from retained sources. No API key or paid generation needed."""
from pathlib import Path
import argparse,json,subprocess
p=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--blender',required=True);a.add_argument('--preview-only',action='store_true');args=a.parse_args()
subprocess.run([args.blender,'--background','--factory-startup','--threads','4','--python',str(p/'source/build_scene.py'),'--','--preview' if args.preview_only else '--render'],check=True)
if not args.preview_only:
 subprocess.run(['python',str(p/'source/mix_audio.py')],check=True)
 subprocess.run(['python',str(p/'source/encode.py')],check=True)
print('REBUILD_OK')
