"""Publish scoped assessments and connect the ten-film gallery to the studio."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
NOTES={
1:('The separate gantry strokes assemble into a readable whale at the aligned hold, then split on departure.','The direct SVG outline, depth-separated fragments and dark water establish a coherent graphic industrial scene.','One continuous camera move establishes, holds and breaks the viewpoint.','Crane modeling is abstract. A human surveyor and a stronger sense of real dock scale would deepen the original discovery.'),
3:('Leaves depart before the blue field exposes their ivory impressions and the many-legged mark.','Cobalt, ivory and olive distinguish the paper states and the culprit.','Specimen motion precedes the rinse and the final closer view.','The botanist is omitted. Exposure and washing are compressed into a graphic transformation rather than a chemical simulation.'),
4:('The pointer settles before the separate bright star reaches its selected position.','Complete brass silhouette, angular engraving and a midnight star field support the celestial miniature.','Rete, pointer, rising star and camera have distinct phases.','The instrument is a stylized astronomical prop. No accurate historical astrolabe or calculated celestial prediction is claimed.'),
7:('A stationary jacket changes from black through green to violet; BEST and EXIT give simultaneous contradictory verdicts.','Camera-ray/normal-dependent color, brass trim and monochrome officials carry the contrast.','The observers and camera change viewpoint while the garment stays fixed.','The verdicts appear as symbols. Hand pinning, facial reactions and a richer comic pause would improve performance.'),
9:('The profile acquires extra chins and the caricature is fixed on a lifted sheet. The full political gag is less clearly established.','Vermilion, teal and ivory, comb-like pigment lines and the gilded tray provide a coherent printmaking miniature.','The sneeze cue, pigment perturbation and paper lift are staged. Flow is represented by geometry rather than convincing fluid motion.','The minister reaction and fourth reflection chin are omitted. A fluid surface and a clearer reaction remain the strongest improvements.'),
15:('A visible air pocket climbs ahead of the advancing bronze and escapes at the ear before the finished horse is revealed.','A clear horse silhouette, contrasting cavity, bright fill and darker final bronze separate the material states.','Fill, bubble escape and mold retreat give one sequential event.','This is a stylized kinematic cutaway. It does not simulate casting flow, trapped gas or thermal solidification.'),
19:('The station passes, the stitched end arrives and bare linen replaces the journey. The widow and late husband relationship remains implicit.','Warm wood, brass borders, blue painted mountains and pale empty linen give the ending visual contrast.','The scroll and crank slow together before the hold on the empty window.','The original emotional backstory is not established. A portrait, empty seat or more specific performed gesture could strengthen it.'),
25:('The smallest child leaves the formal family arrangement and crosses the lower boundary of the picture.','Gilded framing, optical ribs and a small ivory child distinguish the escape from the adult line.','The camera pass and frame rock precede the child departure.','The film is lenticular-inspired staging, not a calculated interlaced optical print. Adult reactions and genuinely view-selected imagery would deepen it.'),
28:('A floral face turns over to reveal BYE, followed by two hands meeting the fabric.','Indigo warp, copper weft, gold flowers and pale reverse lettering separate the two faces.','Shuttle movement and increasing weft rows precede the turn and hand contact.','The short uses an illustrative woven panel with reverse letter contours. It does not generate a manufacturable Jacquard draft. Factory censorship context is omitted.'),
30:('Household gate actions pass water to the dry birdbath, followed by the uphill return of the bird.','Terracotta, three plaster colors, a blue ribbon and stepped architecture give a readable miniature landscape.','Water grows along the channels after gate actions, the bath fills, and the bird leaves.','Flow is animated along a declared path rather than numerically simulated. More nuanced hands, body reactions and bird articulation would improve acting.')}

def main():
    plans=json.loads((ROOT/'production/anthology/selection.json').read_text(encoding='utf8'));rows=[]
    for p in plans:
        intent,appearance,motion,gaps=NOTES[p['concept_id']]
        scores=[2 if p['concept_id'] in [9,19] else 3,3,2 if p['concept_id']==9 else 3,3,3]
        body=f'''# {p['title']} assessment

This is an author-informed assessment of the fourteen-second miniature adaptation. It is separate from the original concept forecast. Fresh-viewer comprehension and audience acceptance remain unverified.

| Dimension | Score out of 4 | Evidence |
| --- | --- | --- |
| Intent | {scores[0]} | {intent} |
| Appearance | {scores[1]} | {appearance} |
| Motion | {scores[2]} | {motion} |
| Delivery | 3 | The encoded-film receipt checks fourteen seconds, 336 frames, 1280×720, 24 fps, complete decode, non-silent audio and visible frame change. Normal-speed browser completion is recorded separately. |
| Editability | 3 | The archive contains direct SVG inputs, a baked Blender scene, builders and retained ElevenLabs audio. The independent outside-Git package test records its checked scope. |

Delivery and Editability scores apply to the final passing receipts linked below.

## Remaining gaps

{gaps}

## Evidence

[Film](film.mp4) · [Timestamped encoded frames](screening-frames.jpg) · [Encoded checks](receipts/encoded-film.json) · [Browser playback](receipts/browser-playback.json) · [Source package test](receipts/source-package-test.json) · [SVG](source/design.svg) · [Saved scene](source/scene.blend)

All music and effects were generated with ElevenLabs and retained with request receipts. The geometric materials and scenes are authored work guided by SVG & 3D Design, not historical reproductions certified by Getty.
'''
        (ROOT/'projects'/p['slug']/'assessment.md').write_bytes(body.encode('utf8'))
        rows.append(f"| #{p['concept_id']} [{p['title']}](../projects/{p['slug']}/) | {' / '.join(map(str,scores))} | {gaps} |")
    selection='\n'.join(f"| #{p['concept_id']} {p['title']} | [{p['aat']['term']}]({p['aat']['url']}) | {p['selection_justification']} |" for p in plans)
    body='''# Ten SVG and Blender films

Ten fourteen-second miniature films were selected from the thirty-concept board for visual range. Each selected concept originally received an Appearance forecast of 4. Finished-film scores below evaluate what was actually built.

[Open the ten-film screening gallery](../anthology.html)

## Selection

| Board concept | Getty AAT anchor | Reason for selection |
| --- | --- | --- |
'''+selection+'''

## Production and evidence

Each project contains a direct SVG input, fourteen-second Blender animation, original ElevenLabs music and sound, retained stems, a standalone source ZIP, preview comparisons and its own README. The new films use authored vector and procedural 3D construction. GPT Image and fal.ai were not used for this batch. [Production journey and repairs](../production/anthology/journey.md).

The builders preserve editable geometry and bake animation into the saved scenes. SVG controls form, while labeled builder sections define event timing. Signature audio cues have explicit start times. JSON files declare the format, seed and brief. These are stylized miniature adaptations, with their differences from the original pitches stated in each player.

## Rubric assessment

Order is Intent / Appearance / Motion / Delivery / Editability, on the existing 0–4 scale. This author-informed review does not establish fresh-viewer understanding or audience acceptance. Delivery and Editability scores are supported by the final per-project playback and extracted-package receipts.

| Film | Profile | Remaining gap |
| --- | --- | --- |
'''+ '\n'.join(rows)+'''

The strongest material and optical payoffs are Whale, Cyanotype, Astrolabe, Peacock and the woven reversal. The two weakest story adaptations are Marbling and Panorama. A concept forecast of 4 does not imply a finished artifact must receive 4. The original Butterfly and accepted Tooth movies remain unchanged.

## Sources

[Original thirty-concept board](concepts-archive.md) · [Getty AAT and its role](getty-aat.md) · [The established rubric](rubric.md) · [Workflow and tools](workflow.md) · [OpenAI SVG and 3D workflow guide](https://learn.chatgpt.com/guides/svg-3d-design) · [SVG path standard](https://www.w3.org/TR/SVG2/paths.html) · [Blender Python API](https://docs.blender.org/api/current/) · [ElevenLabs music](https://elevenlabs.io/docs/overview/capabilities/music) · [ElevenLabs sound effects](https://elevenlabs.io/docs/overview/capabilities/sound-effects) · [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html).
'''
    (ROOT/'docs/anthology.md').write_bytes(body.encode('utf8'))
    hub=ROOT/'index.html';t=hub.read_text(encoding='utf8')
    t=t.replace('Animation Studio · Butterfly and Tooth','SVG and 3D Animation Studio')
    t=t.replace('Two peer projects built with generated references, editable SVG and 3D sources, Blender, sound and repeated audience feedback.','Twelve peer projects with editable SVG and 3D sources, Blender animation, original sound and retained development records.')
    if '<!-- ANTHOLOGY -->' not in t:
        t=t.replace('<section class="library">','<!-- ANTHOLOGY --><section class="library"><h2>Ten new films</h2><p>From an anamorphic whale to a woven farewell: ten fourteen-second SVG and Blender miniatures, each with original ElevenLabs music and sound.</p><p><a href="anthology.html">Open the ten-film screening gallery</a> · <a href="docs/anthology.html">Selection, assessments and development</a></p></section><section class="library">')
    hub.write_bytes(t.encode('utf8'))
    readme=ROOT/'README.md';t=readme.read_text(encoding='utf8').replace('Two peer animation projects share','Twelve peer animation projects share')
    if '## Ten new films' not in t:
        t+='\n\n## Ten new films\n\n[Screen all ten films](https://az9713.github.io/svg-3d-animation-studio/anthology.html) · [Selection, adaptations and assessments](docs/anthology.md) · [Production journey](production/anthology/journey.md)\n\n| Board concept | Project and README |\n| --- | --- |\n'
        t+='\n'.join(f"| #{p['concept_id']} | [{p['title']}](projects/{p['slug']}/README.md) |" for p in plans)
        t+='\n\nAll ten new films are fourteen seconds at 1280×720 and 24 fps. Each has direct SVG source, a saved Blender scene, original ElevenLabs music and sound, and a standalone source package.\n'
    readme.write_bytes(t.encode('utf8'))
    print('ASSESSMENTS_AND_STUDIO_NAVIGATION_SAVED')

if __name__=='__main__':main()
