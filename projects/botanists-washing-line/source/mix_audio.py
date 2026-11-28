"""Mix retained ElevenLabs stems without contacting a service."""
from pathlib import Path
import json,subprocess
p=Path(__file__).resolve().parents[1]
inputs=['-i',str(p/'audio/music.mp3'),'-i',str(p/'audio/sfx.mp3')]
cue=p/'audio/cue-plan.json'
if cue.exists():
 plan=json.loads(cue.read_text(encoding='utf8'));start=round(plan['start_s']*1000);inputs+=['-i',str(p/'audio/cue.mp3')]
 filt=f'[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.68,afade=t=in:d=0.25,afade=t=out:st=13.2:d=0.8[m];[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.15,afade=t=in:d=0.1,afade=t=out:st=13.4:d=0.6[f];[2:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.60,adelay={start}|{start}[c];[m][f][c]amix=inputs=3:normalize=0,loudnorm=I=-18:TP=-1.5:LRA=9,apad,atrim=duration=14[a]'
else:
 filt='[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.68,afade=t=in:d=0.25,afade=t=out:st=13.2:d=0.8[m];[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.32,afade=t=in:d=0.1,afade=t=out:st=13.4:d=0.6[f];[m][f]amix=inputs=2:normalize=0,loudnorm=I=-18:TP=-1.5:LRA=9,apad,atrim=duration=14[a]'
subprocess.run(['ffmpeg','-y','-v','error']+inputs+['-filter_complex',filt,'-map','[a]','-c:a','pcm_s16le','-ar','48000',str(p/'audio/mix.wav')],check=True)
print('MIX_OK')
