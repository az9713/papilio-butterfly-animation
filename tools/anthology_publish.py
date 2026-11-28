"""Build independent project players, source archives and the anthology gallery."""
from pathlib import Path
import hashlib,html,json,zipfile

ROOT=Path(__file__).resolve().parents[1]
REBUILD='''"""Rebuild locally from retained sources. No API key or paid generation needed."""
from pathlib import Path
import argparse,json,subprocess
p=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--blender',required=True);a.add_argument('--preview-only',action='store_true');args=a.parse_args()
subprocess.run([args.blender,'--background','--factory-startup','--threads','4','--python',str(p/'source/build_scene.py'),'--','--preview' if args.preview_only else '--render'],check=True)
if not args.preview_only:
 subprocess.run(['python',str(p/'source/mix_audio.py')],check=True)
 subprocess.run(['python',str(p/'source/encode.py')],check=True)
print('REBUILD_OK')
'''
MIX='''"""Mix retained ElevenLabs stems without contacting a service."""
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
'''
ENCODE='''"""Encode the declared frame sequence with the retained soundtrack."""
from pathlib import Path
import json,subprocess
p=Path(__file__).resolve().parents[1];c=json.loads((p/'source/timeline.json').read_text(encoding='utf8'))
subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(c['fps']),'-i',str(p/'frames/frame_%04d.png'),'-i',str(p/'audio/mix.wav'),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(c['duration']),'-movflags','+faststart',str(p/'film.mp4')],check=True)
print('ENCODE_OK')
'''

def player(p):
    title=html.escape(p['title']);slug=p['slug'];beats=''.join('<li>'+html.escape(b)+'</li>' for b in p['story_beats'])
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · SVG and 3D Animation Studio</title><link rel="stylesheet" href="../../assets/studio.css">
<nav class="nav"><a href="../../index.html">Animation Studio</a><a href="../../anthology.html">Ten films</a><a href="../../docs/concepts.html#concept-{p['concept_id']}">Original concept</a><a href="README.html">Sources and rebuild</a></nav>
<main class="film"><p class="meta">CONCEPT {p['concept_id']:02} · 14 SECONDS · SOUND</p><h1>{title}</h1>
<video id="screen" controls playsinline preload="metadata" poster="poster.jpg" aria-label="{title} screening"><source src="film.mp4" type="video/mp4"></video>
<div class="player-tabs"><button id="play">Play with sound</button><a href="film.mp4" download>Download film</a><a href="downloads/{slug}-source.zip" download>Editable source ZIP</a></div><p id="status" role="status">Ready · 14 seconds</p>
<details><summary>Story, original pitch and adaptation</summary><p>{html.escape(p['adaptation'])}</p><ul>{beats}</ul><h2>The original concept</h2><p>{html.escape(p['original_pitch'])}</p><p>{html.escape(p['selection_justification'])}</p><p>Getty AAT anchor: <a href="{html.escape(p['aat']['url'],quote=True)}">{html.escape(p['aat']['term'])}</a>.</p></details>
<h2>Construction and iteration</h2><p>Editable SVG profiles drive Blender geometry or scene structure. The saved Blender scene contains baked animation. Original ElevenLabs music and effects provide the soundtrack. This film uses procedural vector and 3D construction.</p>
<p><a href="source/design.svg">SVG input</a> · <a href="source/scene.blend">Blender scene</a> · <a href="source/timeline.json">Timeline and brief</a> · <a href="receipts/encoded-film.json">Encoded-film checks</a> · <a href="assessment.html">Rubric assessment</a></p>
<details><summary>Compare the first preview with the repaired preview</summary><h3>First preview</h3><img loading="lazy" src="previews/iteration-1/storyboard.jpg" alt="First development storyboard"><h3>Repaired preview</h3><img loading="lazy" src="previews/storyboard.jpg" alt="Repaired development storyboard"></details>
<h2>Frames from the film</h2><img loading="lazy" src="screening-frames.jpg" alt="Eight timestamped frames extracted from the encoded film">
</main><footer><a href="../../anthology.html">All ten films</a></footer>
<script>const v=document.querySelector('#screen'),s=document.querySelector('#status');document.querySelector('#play').addEventListener('click',async()=>{{v.muted=false;v.volume=1;v.currentTime=0;try{{await v.play()}}catch(e){{s.textContent='Playback failed: '+e.message}}}});v.addEventListener('playing',()=>s.textContent='Playing with sound');v.addEventListener('ended',()=>s.textContent='Playback complete · 14 seconds');v.addEventListener('error',()=>s.textContent='Media error');</script></html>'''

def main():
    plans=json.loads((ROOT/'production/anthology/selection.json').read_text(encoding='utf8'))
    for p in plans:
        path=ROOT/'projects'/p['slug']
        (path/'index.html').write_text(player(p),encoding='utf8')
        for name,content in [('rebuild.py',REBUILD),('mix_audio.py',MIX),('encode.py',ENCODE)]:
            (path/'source'/name).write_text(content,encoding='utf8')
        readme=path/'README.md';body=readme.read_text(encoding='utf8')
        marker='## Reproduction commands'
        if marker in body:body=body[:body.index(marker)]
        body+='''## Reproduction commands

Install Blender 5.3, Python 3.13 and FFmpeg, with ffmpeg available on PATH. Extract the source ZIP into an empty directory. Run from the extracted project directory:

~~~powershell
python source/rebuild.py --blender "PATH_TO_BLENDER_EXECUTABLE"
~~~

The rebuild reads the SVG and format/brief JSON, saves the editable Blender scene, renders 336 frames, mixes the retained ElevenLabs stems and encodes film.mp4. No API key or new generation is needed. For the five-frame staging check, append --preview-only. Edit source/design.svg to change the vector forms. The JSON declares resolution, frame rate, duration, deterministic seed and the brief. Scene-specific event timing is in the labeled sections of source/build_scene.py, and signature audio times are in audio/cue-plan.json. The present timing contract is fourteen seconds at 24 fps. Animation is baked into scene.blend.

[Watch with sound](player.html) · [Rubric assessment](assessment.md) · [Encoded checks](receipts/encoded-film.json)

The source archive excludes regenerable full frame sequences. Original music and sound-effect stems, request prompts and receipts are included. GPT Image and fal.ai were not used to generate this film. The builder follows the SVG & 3D Design workflow and local Blender scripting used for the existing projects.
'''
        readme.write_text(body,encoding='utf8')
        (path/'player.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(p["title"])}</title><style>body{{background:#151a1a;color:#ece8dd;font:18px Georgia;max-width:1100px;margin:40px auto;padding:20px}}video{{width:100%}}</style><h1>{html.escape(p["title"])}</h1><video controls playsinline src="film.mp4"></video><p>14 seconds. Play with sound.</p></html>',encoding='utf8')
        if not (path/'film.mp4').exists():continue
        # Match Git's canonical LF text bytes on every platform before hashing
        # or archiving. This preserves source identity after checkout.
        for file in path.rglob('*'):
            if file.is_file() and file.suffix in {'.py','.md','.json','.svg','.html'}:
                data=file.read_bytes();canonical=data.replace(b'\r\n',b'\n')
                if data!=canonical:file.write_bytes(canonical)
        dest=path/'downloads';dest.mkdir(exist_ok=True)
        members={}
        files=[readme,path/'player.html',path/'film.mp4',path/'poster.jpg',path/'screening-frames.jpg']+([path/'assessment.md'] if (path/'assessment.md').exists() else [])+[f for folder in ['source','audio','receipts'] for f in (path/folder).rglob('*') if f.is_file() and f.name not in {'source-package.json','source-package-test.json'} and f.suffix not in {'.blend1','.pyc'}]
        with zipfile.ZipFile(dest/(p['slug']+'-source.zip'),'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for file in files:
                name=file.relative_to(path).as_posix();data=file.read_bytes();z.writestr(name,data);members[name]=hashlib.sha256(data).hexdigest()
        receipt={'archive':f"downloads/{p['slug']}-source.zip",'sha256':hashlib.sha256((dest/(p['slug']+'-source.zip')).read_bytes()).hexdigest(),'members':members,'scope':'Editable SVG, baked Blender scene, builders, original ElevenLabs stems and receipts. Full frames are regenerated.'}
        (path/'receipts/source-package.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    cards=''.join(f'<article class="project"><a href="projects/{p["slug"]}/"><img loading="lazy" src="projects/{p["slug"]}/poster.jpg" alt="{html.escape(p["title"],quote=True)}"></a><p class="meta">CONCEPT {p["concept_id"]:02} · {html.escape(p["aat"]["term"])}</p><h2>{html.escape(p["title"])}</h2><p>{html.escape(p["selection_justification"])}</p><a href="projects/{p["slug"]}/">Watch with sound</a></article>' for p in plans)
    gallery=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ten films · SVG and 3D Animation Studio</title><link rel="stylesheet" href="assets/studio.css"><nav class="nav"><a href="index.html">Animation Studio</a><a href="docs/concepts.html">Thirty concepts</a><a href="docs/rubric.html">Rubric</a></nav><main><h1>Ten ways to change a world</h1><p class="lead">Ten fourteen-second films from the Getty AAT concept board. Each begins with editable SVG, takes form in Blender, and has original ElevenLabs music and sound.</p><p><a href="docs/anthology.html">Selection, adaptations, development and evidence</a></p><section class="projects">{cards}</section></main><footer><a href="https://github.com/az9713/svg-3d-animation-studio">Sources and development records</a></footer></html>'''
    (ROOT/'anthology.html').write_text(gallery,encoding='utf8')
    print('ANTHOLOGY_PLAYERS_AND_PACKAGES_OK')

if __name__=='__main__':main()
