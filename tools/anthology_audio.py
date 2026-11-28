"""Generate cached ElevenLabs stems and mix the ten films. No secrets in receipts."""
from pathlib import Path
import argparse,concurrent.futures,datetime,hashlib,json,subprocess,time
import requests
from anthology_preflight import key

ROOT=Path(__file__).resolve().parents[1]

def generate(plan,kind):
    path=ROOT/'projects'/plan['slug'];dest=path/'audio'/f'{kind}.mp3';receipt=path/'receipts'/f'elevenlabs-{kind}.json'
    if dest.exists() and receipt.exists():return {'concept_id':plan['concept_id'],'kind':kind,'cached':True}
    token=key()
    if kind=='music':endpoint='/v1/music';body={'prompt':plan['music_prompt'],'music_length_ms':14000,'model_id':'music_v2','force_instrumental':True}
    else:endpoint='/v1/sound-generation';body={'text':plan['sfx_prompt'],'duration_seconds':14,'model_id':'eleven_text_to_sound_v3','prompt_influence':.7}
    start=time.monotonic()
    response=requests.post('https://api.elevenlabs.io'+endpoint,headers={'xi-api-key':token},json=body,timeout=240)
    data={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'endpoint':endpoint,'request':body,'status':response.status_code,
          'request_id':response.headers.get('request-id'),'content_type':response.headers.get('content-type'),'elapsed_seconds':round(time.monotonic()-start,2)}
    if response.ok:
        dest.write_bytes(response.content);data['sha256']=hashlib.sha256(response.content).hexdigest();data['bytes']=len(response.content)
    else:data['error']=response.text.replace(token,'[redacted]')[:600]
    receipt.write_text(json.dumps(data,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'concept_id':plan['concept_id'],'kind':kind,'status':response.status_code}),flush=True)
    if not response.ok:raise RuntimeError(f"ElevenLabs {kind} failed for {plan['concept_id']}: HTTP {response.status_code}")
    return data

def mix(plan):
    path=ROOT/'projects'/plan['slug']
    # Generated effect sequences are atmospheric beds. Exact causal accents are
    # selected from the same ElevenLabs source and placed by declared cue times.
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(path/'audio/music.mp3'),'-i',str(path/'audio/sfx.mp3'),
                    '-filter_complex','[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.68,afade=t=in:d=0.25,afade=t=out:st=13.2:d=0.8[m];[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.32,afade=t=in:d=0.1,afade=t=out:st=13.4:d=0.6[f];[m][f]amix=inputs=2:normalize=0,loudnorm=I=-18:TP=-1.5:LRA=9,apad,atrim=duration=14[a]',
                    '-map','[a]','-c:a','pcm_s16le','-ar','48000',str(path/'audio/mix.wav')],check=True)
    record={'music':'audio/music.mp3','effects':'audio/sfx.mp3','mix':'audio/mix.wav','duration':14,
            'music_gain':.68,'sfx_gain':.32,'loudness_target_lufs':-18,'true_peak_target_db':-1.5,
            'scope':'Two original ElevenLabs stems. Generated effect sequence is a sound bed, with event recognition and final synchronization reviewed in the encoded film.',
            'mix_sha256':hashlib.sha256((path/'audio/mix.wav').read_bytes()).hexdigest()}
    (path/'receipts/mix.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='*',type=int);parser.add_argument('--mix-only',action='store_true');args=parser.parse_args()
    plans=json.loads((ROOT/'production/anthology/selection.json').read_text(encoding='utf8'))
    if args.ids:plans=[p for p in plans if p['concept_id'] in args.ids]
    if not args.mix_only:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(generate,p,k) for p in plans for k in ['music','sfx']]
            for future in concurrent.futures.as_completed(futures):future.result()
    for p in plans:mix(p)
    print('AUDIO_OK',len(plans),flush=True)

if __name__=='__main__':main()
