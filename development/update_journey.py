"""Generate the human-readable development record from retained evidence."""
from datetime import datetime,timezone
import hashlib
import html
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from pipeline_common import CONFIG_KEYS,sha256


def main():
    folder=ROOT/'development';receipts=folder/'receipts'
    inventory=[]
    for path in sorted(receipts.glob('*.json')):
        if path.name=='index.json':continue
        payload=json.loads(path.read_text())
        inventory.append({'file':path.name,'sha256':sha256(path),'event':payload.get('event',path.stem),
                          'status':'pass' if payload.get('accepted',payload.get('passed')) is True else
                                   'stopped' if payload.get('accepted',payload.get('passed')) is False else 'record'})
    (receipts/'index.json').write_text(json.dumps(inventory,indent=2)+'\n',encoding='utf-8')
    stages=[
      ('Concept references','Generated brass/turquoise concept; refined legs into a pedestal-mounted sculpture.',['concept-v01.png','concept-v02.png']),
      ('Blockout and camera repair','First clay framing cropped tips and pedestal; second pass widened framing.',['stages/blockout-v01/blockout-v01-views.jpg','stages/blockout-v02/blockout-v02-views.jpg']),
      ('Editable geometry','Built wing plates, enamel faces, rims, ribs, fasteners and four hinge controls from SVG contours.',['wing-profiles.svg','stages/geometry-v01/geometry-v01-views.jpg']),
      ('Material and lighting repair','Deepened enamel, replaced the gold cap with an annular rim, and removed the horizon seam.',['stages/lookdev-v01/lookdev-v01-views.jpg','stages/lookdev-v02/lookdev-v02-views.jpg']),
      ('Motion review','Created a 12-second preview with six wing cycles and a complete orbit; checked framing, sampled intersections and loop boundaries.',['motion-preview-v01.mp4','motion-v01-audit.json']),
      ('Original delivery','Rendered and delivered the silent 1080p film, native scene and initial source archive.',['papilio-final-1080p.mp4','stages/final-v01/final-v01.blend','papilio-final-1080p-review.json']),
      ('Rubric and reliability diagnosis','Five dimensions: Intent, Appearance, Motion, Delivery, Editability. Assessment profile was 3,3,3,3,2; source control and revision handling needed repair.',['development/receipts/002-before-build.json','development/receipts/003-before-observations.json']),
      ('Source reliability repair','Connected all 22 JSON settings, required scene selection, bound resume to source/settings, generalized timing, and tested a fresh default rebuild and edited variants.',['development/receipts/verification-02-099-summary.json']),
    ]
    history=[]
    for title,decision,paths in stages:
        history.append({'stage':title,'decision':decision,
                        'origin':'contemporaneous repair receipts' if title.startswith(('Rubric','Source reliability')) else 'reconstructed from saved production artifacts',
                        'evidence':[{'path':name,'sha256':sha256(ROOT/name)} for name in paths]})
    commits=subprocess.check_output(['git','log','--reverse','--format=%H|%aI|%s'],cwd=ROOT).decode().splitlines()
    (folder/'history.json').write_text(json.dumps({'recording_policy':'Preserve evidence and failed attempts. Earlier production chronology is reconstructed from saved artifacts; per-step machine receipts start with the reliability repair. Do not fabricate missing historical timestamps.',
        'historical_stages':history,'git_history':[dict(zip(['commit','date','subject'],line.split('|',2))) for line in commits]},indent=2)+'\n',encoding='utf-8')
    env={'python':sys.version.split()[0],'blender':'5.3.0','ffmpeg':subprocess.check_output(['ffmpeg','-version']).decode().splitlines()[0],
         'python_packages':{name:importlib.metadata.version(name) for name in ['Pillow','playwright']},
         'tested_platform':'Windows','render_tests':['CPU','automatic backend selection'],'browser':'Microsoft Edge via Playwright'}
    (folder/'environment-tested.json').write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8')
    css=re.search(r'<style>(.*?)</style>',(ROOT/'index.html').read_text(encoding='utf-8'),re.S).group(1)
    css+='code{overflow-wrap:anywhere} td{overflow-wrap:anywhere}.pass{color:#87d9a2}.stopped{color:#ffbb85}'
    command='''blender --background --factory-startup --python-exit-code 1 --python build_scene.py -- --stage final --revision 2 --render none --device auto
blender --background --factory-startup --python-exit-code 1 --python render_saved.py -- --scene stages/final-v02/final-v02.blend --output final-frames/final-v02 --device auto --plan
blender --background --factory-startup --python-exit-code 1 --python render_saved.py -- --scene stages/final-v02/final-v02.blend --output final-frames/final-v02 --device auto
python encode_review.py final-frames/final-v02 papilio-revision-02.mp4 --browser-check'''
    article='''<h2 id="reliability">Source reliability release 1.1.0</h2><p>The original animation and all existing scene checkpoints and visual assets are preserved. This release repairs the path from a configuration change to the correct revised export. The <a href="development/index.html">development record</a> retains issues, decisions, commands, observed results, and failed attempts.</p><p><a href="https://github.com/az9713/papilio-butterfly-animation/releases/download/v1.1.0/papilio-source-v1.1.0.zip">Download the versioned source package</a>. Movies and raw frame caches are excluded from the source-only ZIP; preview media in its HTML guide uses the published website.</p>'''
    body='''<p><a href="../index.html">Animation and original workflow</a></p><h1>Source reliability and development record</h1><p>The delivered film stays unchanged. The updated source makes configuration controls effective, requires an explicit scene revision at rendering, and records the selected inputs and outputs. Original production decisions are retained alongside the repair evidence.</p><nav><a href="#issues">Issues and fixes</a><a href="#rebuild">Rebuild</a><a href="#controls">Controls</a><a href="#history">History</a><a href="#receipts">Receipts</a></nav>'''
    body+='<p class="meta">Source release 1.1.0 · Windows / Blender 5.3 verified · Original movie SHA-256: <code>586d7e0c9d8fd5af8d8d39aa4a89d01f0b4bfab4ab9b717d4d3d14d65ed9b465</code></p><p>Working-copy assets retain their original bytes. Source exports use Git canonical text line endings: the SVG is 1513 bytes with CRLF in the original working copy and 1509 bytes with LF in Git and the ZIP, with identical curve data. Binary movies and Blender checkpoints retain identical bytes. <a href="protected-assets.json">Both preservation hash sets</a> · <a href="receipts/020-package-preservation-diagnostic.json">Extraction diagnostic</a>.</p>'
    body+='''<h2 id="issues">Issues and fixes</h2><table><thead><tr><th>Issue</th><th>Before</th><th>Repair and evidence</th></tr></thead><tbody>
<tr><td>Controls</td><td>JSON camera_orbits, resolution, and final_samples were ignored.</td><td>All 22 fields are validated and consumed. Explicit CLI overrides win and are recorded in config-used.json and report.json. <a href="receipts/003-before-observations.json">Before</a> · <a href="receipts/verification-02-014-json-controls-inspect.json">After</a></td></tr>
<tr><td>Revision selection</td><td>The render helper always opened final-v01.</td><td>Rendering requires --scene and --output. Plans expose the selected scene hash. Frame reuse requires the same scene and render settings. <a href="receipts/verification-02-023-json-controls-selection-plan.json">Selection proof</a></td></tr>
<tr><td>Timing</td><td>Audit and encoding helpers assumed 288 frames at 24 fps.</td><td>Audits read the selected scene; encoding reads its render manifest. A disposable 12-frame, 6-fps, two-second CPU clip was rendered, resumed, encoded, and played completely. <a href="receipts/verification-02-040-encode-and-playback.json">Evidence</a></td></tr>
<tr><td>Source handoff</td><td>The initial ZIP predates the current guide and dependency file.</td><td>A versioned source ZIP copies committed source and checkpoints, includes pinned review dependencies, a hashed inventory, and links omitted movies to the published website.</td></tr>
</tbody></table><h3>A failed check remains part of the record</h3><p>The first repair run stopped because an exact geometry hash differed. Direct comparison found identical coordinates and transforms, with different ordering of sphere faces. Canonical comparison sorts oriented faces without reversing their winding; it then found identical geometry. The original failed check, diagnostic, and corrected check are retained. <a href="receipts/verification-01-098-stopped.json">Stopped run</a> · <a href="receipts/005-geometry-diagnostic.json">Diagnostic</a> · <a href="receipts/007-canonical-geometry-comparison.json">Resolved comparison</a>.</p>'''
    body+='''<h2 id="rebuild">Build, select, render, and encode</h2><p>Run from the project root. Substitute the installed Blender executable for blender. On PowerShell, prefix a quoted executable path with &amp;. Each new build uses a new revision or tag; existing checkpoint directories are preserved.</p><pre><code>'''+html.escape(command)+'''</code></pre><p>The --plan step opens and inspects the selected file without rendering or writing outputs. Remove --plan for the actual render. Existing complete frames can be resumed only with the same source and effective settings. Corrupt frames, changed settings, or a different scene require a new output directory.</p><p>The original final-v01 scene remains usable with the same explicit --scene argument. Do not run a rebuild into its existing checkpoint directory.</p><h3>Requirements and device selection</h3><p>Core construction and rendering use Blender’s bundled Python and the standard library. Encoding requires FFmpeg and ffprobe on PATH. For browser verification and the historical review-image helpers, install the recorded versions with <code>python -m pip install -r requirements-review.txt</code>. Browser checks default to installed Microsoft Edge; <code>--browser-channel chromium</code> selects a Playwright-installed Chromium instead.</p><p><code>--device auto</code> selects an available Cycles backend, preferring OptiX, and falls back to CPU. <code>--device cpu</code> explicitly uses CPU. Explicit unavailable GPU backends fail rather than silently substituting another backend. CPU and automatic OptiX selection were tested on the production Windows installation. Other operating systems and GPU backends remain unverified. <a href="environment-tested.json">Recorded environment</a>.</p><h3>Audit a new scene</h3><pre><code>blender --background --factory-startup --python-exit-code 1 --python audit_scene.py -- stages/final-v02/final-v02.blend --output audits/final-v02.json</code></pre><p>Framing is checked on every scene frame. Intersection checks sample half-second intervals and cover wing plates against each other and the named body parts. They are an artistic scene screen, not fabrication validation.</p>'''
    cfg=json.loads((ROOT/'config.json').read_text())
    purposes={
      'title':'Scene metadata; does not add lettering to the film.', 'duration_seconds':'Clip duration; duration × fps must be an integer frame count.',
      'fps':'Integer frame rate, 1–240.', 'resolution':'Two even pixel dimensions, each 16–16384; --res explicitly overrides it.',
      'final_samples':'Cycles sample count; --samples explicitly overrides it.',
      'camera_orbits':'Nonnegative integer revolutions per clip; zero gives a stationary camera.',
      'wing_period_seconds':'Seconds per wing cycle; must divide the duration when wings move.',
      'light_period_seconds':'Seconds per light cycle; must divide the duration when light modulation is active.',
      'wing_rest_degrees':'Wing angle around which the sinusoid moves.', 'wing_amplitude_degrees':'Nonnegative upper-wing angular amplitude.',
      'lower_wing_amplitude_factor':'Nonnegative multiplier for lower-wing amplitude.',
      'light_breath_fraction':'Light energy modulation fraction, 0–1.', 'lighting_revision':'Supported studio layout: 1 or 2.',
      'root_height':'Positive sculpture root height.', 'root_tilt_degrees':'Sculpture root X rotation in degrees.',
      'camera_radius':'Positive orbit radius.', 'camera_height':'Camera Z position.', 'camera_lens_mm':'Positive focal length.',
      'camera_target_height':'Camera aim height on the vertical axis.', 'camera_start_degrees':'Orbit starting angle.',
      'metal_roughness':'Brass roughness, 0–1.', 'enamel_roughness':'Enamel roughness, 0–1.'}
    body+='<h2 id="controls">Configuration contract</h2><p>JSON supplies defaults. Only explicitly supplied CLI --res and --samples values override it. Unknown keys, invalid types, invalid dimensions, and nonclosing active cycle periods fail before a checkpoint is created. Keep absolute M/C/Z commands when editing the supplied SVG; make_profiles.py regenerates the original contours.</p><table><thead><tr><th>Control</th><th>Delivered value</th><th>Meaning</th></tr></thead><tbody>'
    for key in sorted(CONFIG_KEYS):body+='<tr><td><code>'+key+'</code></td><td>'+html.escape(json.dumps(cfg[key]))+'</td><td>'+purposes[key]+'</td></tr>'
    body+='</tbody></table><p><a href="receipts/verification-02-099-summary.json">Integration summary</a> · <a href="../tests/test_pipeline.py">Unit tests</a> · <a href="verify_reliability.py">Repeatable Blender integration verifier</a>.</p>'
    body+='<p>Historical presentation helpers remain for provenance. They can require optional per-view render PNGs or intermediate movies that are omitted from the source-only ZIP. The supported build, audit, render, and encode commands above are the verified reproduction path.</p><h2 id="history">Development journey</h2><p>Early steps are reconstructed from preserved artifacts and Git history; exact per-step timestamps were not retained for every early decision. Repair steps have contemporaneous execution receipts. Historical statements are kept distinct from new measurements.</p>'
    for item in history:
        body+='<h3>'+html.escape(item['stage'])+'</h3><p>'+html.escape(item['decision'])+'</p><p>'
        body+=' · '.join('<a href="../'+entry['path']+'">'+html.escape(Path(entry['path']).name)+'</a>' for entry in item['evidence'])+'</p>'
    body+='<p><a href="history.json">Machine-readable history with artifact hashes and Git commits</a>.</p>'
    body+='''<h2 id="receipts">Execution receipts and future changes</h2><p>Each receipt retains the command, observed exit status, stdout and stderr, expected outcome, and available source hashes. An expected rejection counts as a passed negative test. Stopped attempts remain visible. Local account paths are redacted from published receipts; frame caches stay local.</p><pre><code>python development/record_step.py my-change-001 -- blender --background --factory-startup --python-exit-code 1 --python build_scene.py -- --stage final --revision 3 --render none
python -m unittest discover -s tests -v
python development/verify_reliability.py --blender BLENDER_EXECUTABLE --run-id my-verification-001</code></pre><p>Use a unique event ID and verification run ID. Receipts refuse to overwrite an earlier event. After a change, run <code>python development/update_journey.py</code> to refresh this index. <a href="receipts/index.json">Receipt inventory and SHA-256 digests</a>.</p><table><thead><tr><th>Step</th><th>Outcome</th><th>Receipt</th></tr></thead><tbody>'''
    for item in inventory:
        body+='<tr><td>'+html.escape(item['event'])+'</td><td class="'+item['status']+'">'+item['status']+'</td><td><a href="receipts/'+item['file']+'">JSON</a></td></tr>'
    body+='</tbody></table>'
    release=ROOT/'source-release.json'
    if release.exists():
        metadata=json.loads(release.read_text())
        body+='<h2>Package release verification</h2><p><a href="'+metadata['download_url']+'">Source ZIP '+metadata['version']+'</a> · <a href="../source-release.json">Release receipt</a>. SHA-256: <code>'+metadata['sha256']+'</code>.</p>'
    (folder/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Papilio source reliability and development record</title><style>'+css+'</style><main>'+body+'</main></html>\n',encoding='utf-8')
    page=ROOT/'index.html';text=page.read_text(encoding='utf-8')
    replacement='<article id="reproduce">'+article+'<p><a href="development/index.html#rebuild">Current reproduction commands, configuration contract, device selection, and receipts</a>.</p></article>'
    text=re.sub(r'<article id="reproduce">.*?</article>',replacement,text,count=1,flags=re.S)
    if '>Development record</a>' not in text:text=text.replace('</nav>','<a href="development/index.html">Development record</a></nav>',1)
    page.write_text(text,encoding='utf-8')
    print(json.dumps({'receipt_count':len(inventory),'historical_stages':len(history),'configuration_fields':len(CONFIG_KEYS)}))


if __name__=='__main__':main()
