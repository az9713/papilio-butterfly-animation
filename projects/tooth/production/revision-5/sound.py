from pathlib import Path
import json,subprocess,xml.etree.ElementTree as ET
import numpy as np
from scipy.io.wavfile import read,write

root=Path(__file__).resolve().parent
timeline=json.loads((root/'timeline.json').read_text())
sr=48000
count=round(timeline['duration']*sr)
time=np.arange(count)/sr
tracks={name:np.zeros((count,2)) for name in ['voice','box','tools']}
events=[]
def add(track,start,wave,pan=0,kind=None):
    offset=round(start*sr)
    length=min(len(wave),count-offset)
    gains=np.sqrt(np.array([1-pan,1+pan])/2)
    tracks[track][offset:offset+length]+=wave[:length,None]*gains
    if kind:events.append({'kind':kind,'start_s':start,'end_s':(offset+length)/sr})
def metal(midi):
    t=np.arange(round(sr*1.1))/sr
    f=440*2**((midi-69)/12)
    wave=sum(a*np.sin(2*np.pi*f*k*t)*np.exp(-t/tau) for k,a,tau in [(1,.87,.38),(2.003,.34,.23),(3.94,.16,.12),(6.23,.09,.06)])
    return .5*wave*(1-np.exp(-t/.0025))
score=[(float(e.get('data-beat')),int(e.get('data-midi')),e.get('data-cadence')=='1') for e in ET.parse(root/'score.svg').iter() if e.get('data-midi')]
for p,start in enumerate(timeline['phrase_starts']):
    for beat,midi,cadence in score:
        if cadence and p!=1:continue
        at=start+beat*60/timeline['bpm']
        add('box',at,metal(midi)*(1.25 if cadence else .8),-.3,'metal interruption' if cadence else 'box note')
rate,vocal=read(root/'vocal-D.wav');assert rate==sr
vocal=vocal.astype(float)/32768
v=timeline['voice']
add('voice',v['first_start'],vocal,.25,'first sung D')
attempt=vocal[:round((v['attempt_end']-v['attempt_start'])*sr)].copy()
attempt[-round(.015*sr):]*=np.linspace(1,0,round(.015*sr))
add('voice',v['attempt_start'],attempt,.25,'interrupted sung D')
add('voice',v['return_start'],vocal,.25,'reclaimed sung D')
rate,line=read(root/'customer-line.wav');assert rate==sr
line=line.astype(float)/32768
line*=min(.16/(np.sqrt(np.mean(line**2))+1e-9),.60/(max(abs(line))+1e-9))
add('voice',timeline['dialogue_start'],line,.25,'customer dialogue')
for start in [5.20,5.65,11.20,11.60]:
    t=np.arange(round(.07*sr))/sr
    add('tools',start,.14*np.sin(2*np.pi*1100*t)*np.exp(-t/.012),-.1,'forceps click')
pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(root.parent/'elevenlabs-bed.mp3'),'-ac','2','-ar',str(sr),'-f','f32le','-'])
bed=np.frombuffer(pcm,'<f4').reshape(-1,2)
bed=np.pad(bed,((0,max(0,count-len(bed))),(0,0)))[:count].copy()
bed*=.012/(np.sqrt(np.mean(bed**2))+1e-9)
bed*=np.minimum(time/.3,1)[:,None]*np.clip((16-time)/.7,0,1)[:,None]
duck=np.ones(count)
for a,b in [(3.4,4.74),(7.95,9.65),(13.9,15.3)]:
    window=np.clip((time-a)/.05,0,1)*np.clip((b-time)/.05,0,1)
    duck*=1-.97*window
bed*=duck[:,None]
# Only the metal cadence interrupts the second vocal. All other accompaniment
# is subdued in the first and returned-note moments.
box_duck=np.ones(count)
for a,b in [(3.4,4.74),(13.9,15.3)]:
    box_duck*=1-.97*np.clip((time-a)/.05,0,1)*np.clip((b-time)/.05,0,1)
box_duck*=1-.97*np.clip((time-7.98)/.015,0,1)*np.clip((8.245-time)/.015,0,1)
box_duck*=1-.97*np.clip((time-8.46)/.025,0,1)*np.clip((9.65-time)/.025,0,1)
tracks['box']*=box_duck[:,None]
mix=sum(tracks.values())+bed
gain=min(1,.89/(max(abs(mix).max(),1e-9)))
mix*=gain
for name,wave in {**tracks,'bed':bed,'mix':mix/gain}.items():
    write(root/(name+'.wav'),sr,(wave*gain*32767).astype(np.int16))
receipt={'timeline':'timeline.json','duration_s':16,'events':events,'voice_gain':gain,'dedicated_breath_events':[],
         'background':'Original ElevenLabs Music bed','vocal_source':'ElevenLabs sung ah, one prepared source reused at first and last cadence',
         'peak':float(abs(mix).max())}
(root/'audio-cues.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
