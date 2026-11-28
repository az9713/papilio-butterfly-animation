# The Botanist’s Washing Line

A miniature cyanotype sheet loses its pressed leaves to a gust. A wash turns the paper deep blue, leaving ivory leaf impressions. A many-legged silhouette appears beneath the leaves.

Cyan blue, ivory botanical silhouettes and a tiny insect reveal give a graphic material transformation with a comic discovery.

Original board concept #3. cyanotypes (photographic prints) is the Getty AAT vocabulary anchor. This short is an authored miniature adaptation, not a documentary demonstration.

## Story beats

- 0–4 s: pressed leaves on pale paper
- 4–7 s: gust removes the specimens
- 7–11 s: blue rinse reveals the plant shadows
- 11–14 s: push toward the insect impression

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
