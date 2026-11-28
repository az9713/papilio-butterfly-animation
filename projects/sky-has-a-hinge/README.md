# The Sky Has a Hinge

A pierced astrolabe rotates against a midnight sky. Its pointer selects a position before one brilliant star rises into the same alignment. The camera draws back to the night beyond the brass.

Pierced brass, engraved astronomical geometry and a star prediction combine precision with cosmic scale.

Original board concept #4. astrolabes is the Getty AAT vocabulary anchor. This short is an authored miniature adaptation, not a documentary demonstration.

## Story beats

- 0–4 s: brass rings turn independently
- 4–8 s: pointer settles on the horizon
- 8–11 s: the predicted star rises into alignment
- 11–14 s: camera reveals the night beyond the instrument

## Sources and rebuild

The Blender builder reads source/design.svg and source/timeline.json. Open source/scene.blend to edit the baked animation. The generation prompts, raw ElevenLabs music and sound effects, mix, previews and receipts are retained.

Build from this folder with Blender in background mode and source/build_scene.py. Production commands and verification receipts will be recorded as each stage completes.
## Reproduction commands

Install Blender 5.3, Python 3.13 and FFmpeg, with ffmpeg available on PATH. Extract the source ZIP into an empty directory. Run from the extracted project directory:

~~~powershell
python source/rebuild.py --blender "PATH_TO_BLENDER_EXECUTABLE"
~~~

The rebuild reads the SVG and format/brief JSON, saves the editable Blender scene, renders 336 frames, mixes the retained ElevenLabs stems and encodes film.mp4. No API key or new generation is needed. For the five-frame staging check, append --preview-only. Edit source/design.svg to change the vector forms. The JSON declares resolution, frame rate, duration, deterministic seed and the brief. Scene-specific event timing is in the labeled sections of source/build_scene.py, and signature audio times are in audio/cue-plan.json. The present timing contract is fourteen seconds at 24 fps. Animation is baked into scene.blend.

[Watch with sound](player.html) · [Rubric assessment](assessment.md) · [Encoded checks](receipts/encoded-film.json)

The source archive excludes regenerable full frame sequences. Original music and sound-effect stems, request prompts and receipts are included. GPT Image and fal.ai were not used to generate this film. The builder follows the SVG & 3D Design workflow and local Blender scripting used for the existing projects.
