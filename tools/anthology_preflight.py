"""Read-only production preflight. Never prints keys or account identifiers."""
from pathlib import Path
import datetime,importlib.util,json,shutil,subprocess
import requests

ROOT=Path(__file__).resolve().parents[1]
BLENDER=Path('C:/Program Files/Blender Foundation/Blender 5.3/blender.exe')

def key():
    # Keep credentials in the original private workspace, outside publication.
    path=ROOT.parent/'.env'
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        if '=' in line:
            name,value=line.split('=',1)
            if name.strip().lower()=='elevenlabs_api_key':return value.strip().strip('"').strip("'")
    raise RuntimeError('ElevenLabs key missing')

def main():
    modules={name:importlib.util.find_spec(name) is not None for name in ['requests','numpy','PIL','cv2','scipy','playwright']}
    response=requests.get('https://api.elevenlabs.io/v1/user/subscription',headers={'xi-api-key':key()},timeout=30)
    payload=response.json() if response.ok else {}
    result={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'blender_available':BLENDER.is_file(),'ffmpeg_available':bool(shutil.which('ffmpeg')),
            'ffprobe_available':bool(shutil.which('ffprobe')),'python_modules':modules,
            'free_disk_gb':round(shutil.disk_usage(ROOT).free/1e9,1),
            'elevenlabs_http_status':response.status_code,
            'elevenlabs_credit_capacity_available':payload.get('character_limit',0)>payload.get('character_count',0) if response.ok else False,
            'scope':'Read-only local dependencies and ElevenLabs subscription access. GPU rendering and generation endpoints require separate smoke tests.'}
    (ROOT/'production/anthology/preflight.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result))
    assert BLENDER.is_file() and all(modules.values()) and response.ok

if __name__=='__main__':main()
