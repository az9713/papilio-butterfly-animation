"""Encode the declared frame sequence with the retained soundtrack."""
from pathlib import Path
import json,subprocess
p=Path(__file__).resolve().parents[1];c=json.loads((p/'source/timeline.json').read_text(encoding='utf8'))
subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(c['fps']),'-i',str(p/'frames/frame_%04d.png'),'-i',str(p/'audio/mix.wav'),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(c['duration']),'-movflags','+faststart',str(p/'film.mp4')],check=True)
print('ENCODE_OK')
