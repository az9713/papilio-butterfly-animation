"""Place original ElevenLabs signature effects at explicit story events."""
from pathlib import Path
import concurrent.futures,datetime,hashlib,json,subprocess
import requests
from anthology_preflight import key

ROOT=Path(__file__).resolve().parents[1]
CUES={
3:(7.5,2.5,'One close gentle stream of water rinsing photographic paper in a shallow tray. Clear liquid pour and splash only. No music, no voice.'),
4:(7.0,.7,'One very delicate precise brass detent click as a small astronomical pointer locks into place. Dry close mechanism only, no ambience, no voice, no music.'),
9:(4.8,1.2,'One adult male comic sneeze, a clearly recognizable loud ah-CHOO sneeze. One sneeze only, dry close recording in silence. No words or music.'),
15:(10.1,1.0,'One short clean puff of pressurized air escaping from a tiny foundry mold vent, then a quiet cooling metal tick. No voices, no music.'),
25:(11.3,2.4,'Three distinct tiny wooden puppet footsteps stepping onto a polished wooden tabletop. Close dry Foley with small clear contact knocks. No voices or music.'),
30:(10.25,1.6,'One clear small songbird chirp followed by a brief flutter of wings taking flight. Natural dry close bird sound. No wind, no voice, no music.')}

def run(cid,p):
    path=ROOT/'projects'/p['slug'];start,duration,prompt=CUES[cid];dest=path/'audio/cue.mp3'
    plan={'start_s':start,'duration_s':duration,'gain':.6,'prompt':prompt}
    (path/'audio/cue-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf8')
    if not dest.exists():
        body={'text':prompt,'duration_seconds':duration,'model_id':'eleven_text_to_sound_v3','prompt_influence':.8}
        token=key();r=requests.post('https://api.elevenlabs.io/v1/sound-generation',headers={'xi-api-key':token},json=body,timeout=180)
        receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'endpoint':'/v1/sound-generation','request':body,'status':r.status_code,'request_id':r.headers.get('request-id')}
        if r.ok:dest.write_bytes(r.content);receipt['sha256']=hashlib.sha256(r.content).hexdigest()
        else:receipt['error']=r.text.replace(token,'[redacted]')[:500]
        (path/'receipts/elevenlabs-cue.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
        assert r.ok,(cid,r.status_code)
    filt=f'[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.68,afade=t=in:d=0.25,afade=t=out:st=13.2:d=0.8[m];[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.15,afade=t=in:d=0.1,afade=t=out:st=13.4:d=0.6[f];[2:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.60,adelay={round(start*1000)}|{round(start*1000)}[c];[m][f][c]amix=inputs=3:normalize=0,loudnorm=I=-18:TP=-1.5:LRA=9,apad,atrim=duration=14[a]'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(path/'audio/music.mp3'),'-i',str(path/'audio/sfx.mp3'),'-i',str(dest),'-filter_complex',filt,'-map','[a]','-c:a','pcm_s16le','-ar','48000',str(path/'audio/mix.wav')],check=True)
    (path/'receipts/cued-mix.json').write_text(json.dumps({'cue':plan,'music_gain':.68,'effects_bed_gain':.15,'mix_sha256':hashlib.sha256((path/'audio/mix.wav').read_bytes()).hexdigest(),'scope':'Signature ElevenLabs effect placed at the declared event time. Original two-stem mix receipt is retained as the preceding iteration.'},indent=2)+'\n',encoding='utf8')
    print('CUED_MIX_OK',cid,flush=True)

def main():
    plans={p['concept_id']:p for p in json.loads((ROOT/'production/anthology/selection.json').read_text(encoding='utf8'))}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for f in concurrent.futures.as_completed([pool.submit(run,cid,plans[cid]) for cid in CUES]):f.result()

if __name__=='__main__':main()
