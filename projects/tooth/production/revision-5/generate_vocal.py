from pathlib import Path
import datetime, hashlib, json, requests

root=Path(__file__).resolve().parent
key=next(v.strip().strip('"').strip("'") for k,v in
         (line.split('=',1) for line in (root.parent.parent/'.env').read_text(encoding='utf-8-sig').splitlines() if '=' in line)
         if k.strip().lower()=='elevenlabs_api_key')
body={
    'text':'An elderly man sings one warm sustained wordless AHH note. Audible human vocal cords, open mouth, resonant chest voice, gentle natural vibrato. The vowel is a clear sung ah, steady D4 around 294 Hz. Start voicing immediately, hold one continuous pitch, release softly. Close dry solo male voice recorded in silence. No whisper, no hiss, no breath sound, no music, no instruments, no speech, no other sounds.',
    'duration_seconds':2.0,'model_id':'eleven_text_to_sound_v3','prompt_influence':.7}
res=requests.post('https://api.elevenlabs.io/v1/sound-generation',headers={'xi-api-key':key},json=body,timeout=120)
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'endpoint':'/v1/sound-generation','request':body,'status':res.status_code}
if res.ok:
    (root/'vocal-original.mp3').write_bytes(res.content)
    receipt['sha256']=hashlib.sha256(res.content).hexdigest()
else: receipt['error']=res.text.replace(key,'[redacted]')[:400]
(root/'vocal-generation.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print('Vocal generation HTTP',res.status_code)
