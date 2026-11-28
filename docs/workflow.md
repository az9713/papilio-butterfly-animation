# Tools and the production workflow

The workflow joins generated references, editable geometry, a shared performance timeline, sound design and audience feedback. Codex coordinates the files and tool calls. The artist supplies the purpose, evaluates the result and decides when the film works.

<div class="workflow-map" role="group" aria-label="Production workflow with three asset branches and a feedback loop">
<div class="flow-wide">Getty AAT + creative brief → rubric forecasts → first production test</div>
<div>GPT Image<br>Character and look references</div>
<div>SVG + Blender<br>Editable shape, mechanism and render layers</div>
<div>ElevenLabs<br>Music, sung note and dialogue</div>
<div class="flow-wide">↓ Shared timeline + Python edit and sound assembly</div>
<div class="flow-wide">↓ FFmpeg exports + browser and source-package checks</div>
<div class="flow-wide">↓ Audience screening + rubric → revise the responsible stage → screen again</div>
<div class="flow-wide flow-note">Codex coordinates the files, tool calls and receipts throughout. fal.ai can supply a future hosted generation branch feeding the asset stage.</div>
</div>

## Roles and actual use

| Tool or representation | Inputs | Outputs and role in these projects |
| --- | --- | --- |
| Getty AAT | A subject, object type, material or artistic process | Concept anchors and relationships used to explore varied proposals. |
| Codex | The brief, feedback, files and callable tools | Scene and edit scripts, asset orchestration, tests, diagnosis, documentation and publication. |
| SVG & 3D Design | Art direction, generated references and editable construction goals | A guided workflow for vector and 3D construction. Butterfly uses wing contours. Tooth uses an unrolled pin score and a procedural mechanism. |
| GPT Image | Descriptions and selected visual references | Butterfly concept art and Tooth character, bench, hand and reaction plates. The production tool did not expose its exact image-model identifier. |
| Blender | Python scene instructions, editable geometry, lighting and camera settings | Butterfly’s animated sculpture and Tooth’s cylinder, comb, copper insert, forceps and registered macro layers. Local scripts use Blender’s bpy API and background rendering. |
| ElevenLabs Music | An instrumental direction and target duration | The sparse background bed for Tooth. |
| ElevenLabs sound generation | A vocal performance description and duration | The sung ah used for the accepted Tooth performance. Its original pitch was measured and the prepared note tuned around D4. |
| ElevenLabs speech | A selected stock voice and the short customer line | “That was my part.” The stock George voice was selected from the available account voices. |
| Python, NumPy and SciPy | Score events, prepared vocal, music and timing | Metallic notes, cue assembly, levels, soundtrack stems and audio checks. |
| OpenCV and Pillow | Rendered layers, portrait and performance timing | Jaw articulation, compositing, cuts, push-ins and review frames. |
| FFmpeg and ffprobe | Audio and frame streams | H.264/AAC movies, pass excerpts, pitch-processing filters, media inspection and full decoding. |
| Playwright with Edge | The actual player and exported files | Complete sound-enabled playback at desktop and narrow viewport widths. |
| Browser checks | The published Space or Pages player | Verification of served content and playback through the final frame. |
| Space | Progress, files, feedback and receipts | The collaborative development record used during iteration. |
| Git, GitHub and Pages | The public source, docs, accepted media and publication checks | Versioned peer projects, a shared library and a reproducible public site. |

OpenAI describes SVG & 3D Design as a Codex plugin guiding reference-driven editable SVG and 3D work. In these projects the Blender connection was implemented through local Python scripts and command-line rendering. [OpenAI workflow guide](https://learn.chatgpt.com/guides/svg-3d-design), [Blender Python documentation](https://docs.blender.org/api/current/info_quickstart.html)

ElevenLabs provides separate music, speech and sound-generation capabilities. These roles have separate prompts, source assets and receipts in Tooth. [Sound generation](https://elevenlabs.io/docs/overview/capabilities/sound-effects), [Speech](https://elevenlabs.io/docs/overview/capabilities/text-to-speech), [Music](https://elevenlabs.io/docs/overview/capabilities/music)

## Where fal.ai fits

fal.ai offers hosted model endpoints for image, video, audio and other generation tasks. A model endpoint accepts its documented input schema and returns results with media locations. Its queue API supports submission, status tracking and result retrieval. [Model APIs](https://fal.ai/docs/documentation/model-apis/overview), [Queue lifecycle](https://fal.ai/docs/documentation/model-apis/inference/queue)

A future variation could send an approved reference frame to a selected fal image-to-video model, retrieve a candidate shot, store the model ID and request receipt, and bring the downloaded result into the same edit and evaluation loop. A candidate still has to preserve character identity, the copper slot and the intended action.

The published production receipts for Butterfly and Tooth identify OpenAI image generation, local Blender and Python processing, with ElevenLabs audio in Tooth. fal.ai is an available extension to this workflow. This repository contains no fal generation receipt for either accepted film.

## The concrete Tooth loop

| Step | Concrete input | Result | Review that determines the next action |
| --- | --- | --- | --- |
| Define the causal story | A missing tooth lets a customer supply one note | Three linked passes | Can the setup, interruption and benefit of removal be understood? |
| Establish the look | Wooden customer, repair bench, brass mechanism | Generated plates and editable Blender scene | Can the audience identify both people and track the same slot? |
| Encode the phrase | Seven SVG note events and a tempo | Musical notes and pin layout | Can the recurring D be recognized? |
| Stage the performance | Shared timeline and reusable vocal | Sung note, interrupted attempt, returned note | Are mouth, voice and interruption coordinated? |
| Assemble and export | Layers, voice, box, music and tool cues | A 16-second film and three excerpts | Does the complete file communicate the intended sequence? |
| Test delivery | Encoded movies and actual player | Decode, cue, pixel and playback evidence | Were the intended events delivered? |
| Screen with the artist | The film with sound | Feedback such as “there was no humming” or “now it works” | Revise the failed part or accept the prototype. |
| Freeze and publish | Accepted bytes, sources and receipts | Rebuildable package and public commit | Do the served bytes and source rebuild match the accepted version? |

Every failed screening returns to the earliest responsible step. The initial absence of a repairer required new visual staging. The hiss required a new vocal and mix. The unexplained removal required a stronger performed interruption and audible return of the same note.

## The accepted timeline

The accepted edit uses 120 BPM for the SVG phrase and a single timeline.json for its main timings.

| Film time | Sound | Visible performance |
| --- | --- | --- |
| 3.50–4.70 s | A full sung D | He opens his jaw to sing. |
| 8.00–8.30 s | He tries the same vocal | His entry begins. |
| 8.25 s | The repaired metal note arrives | His vocal is interrupted. |
| After 8.30 s | His vocal stops while metal continues | His jaw closes and his head lowers. |
| 8.50–9.61 s | His short line | He identifies the loss. |
| 9.67–10.38 s | A pause in the exchange | The repairer reacts with concern. |
| 10.38–12.88 s | Restrained tool cues and the phrase | She removes the working tooth. |
| 14.00–15.20 s | The same full sung D returns | He sings and then settles with closed lips. |

The first and returned notes reuse one prepared vocal recording. The final mix omits the earlier filtered-noise breath cues. Reuse makes the musical identity verifiable while the interrupted middle fragment provides the contrast.

## What verification establishes

Tests inspect the exported files for a voiced entry, its cessation, the continuing metal note, the matching returned vocal, jaw change, a cleared slot, decoding and player completion. A new temporary extraction rebuilds the four movies and offline player byte for byte.

The artist’s final acceptance is recorded separately. Technical checks establish delivery of events. Audience responses establish whether those events communicate the story. [Accepted Tooth project](../projects/tooth/index.html)
