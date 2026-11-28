# Animation Studio

Twelve peer animation projects share one discovery, evaluation and publication workflow. All use SVG as an editable source layer. The original Butterfly derives its wing geometry from SVG contours. Tooth derives mechanism pin events and soundtrack notes from an SVG score. Blender, compositing and audio tools produce the finished animations, with generated image plates also used in the original Tooth film.

| Project | Film | Sources and development |
| --- | --- | --- |
| [Papilio butterfly](projects/butterfly/) | Twelve-second silent kinetic-sculpture loop | Editable Blender scene, SVG wing profiles, source release 1.1.1 and retained reliability receipts. |
| [The Tooth That Didn’t Sing](projects/tooth/) | Accepted sixteen-second film with sound | SVG pin score, Blender layers, character plates, ElevenLabs audio, scripted edit, prior cuts and acceptance evidence. |

[Open the public studio](https://az9713.github.io/svg-3d-animation-studio/) · [Watch Tooth](https://az9713.github.io/svg-3d-animation-studio/projects/tooth/) · [Watch Papilio](https://az9713.github.io/svg-3d-animation-studio/projects/butterfly/)

## Shared documents

- [Getty AAT and the creative search](docs/getty-aat.md)
- [The five-dimension rubric](docs/rubric.md)
- [Thirty original concepts, justifications and forecasts](docs/concepts-archive.md)
- [Machine-readable catalog and derived Pareto fronts](docs/concepts.json)
- [Roles of Codex, SVG & 3D Design, GPT Image, Blender, ElevenLabs, fal.ai and the supporting tools](docs/workflow.md)
- [Discussion record and development decisions](docs/discussion.md)
- [Accepted Tooth assessment](projects/tooth/assessment.md)

Getty AAT supplies the vocabulary and concept anchors. The five-dimension rubric was developed for this workflow before the AAT concept catalog. Its current accepted Tooth profile is 3 / 3 / 3 / 3 / 3. The original recommendation ranked Tooth first to prototype. Forecast comparison and observed artifact acceptance are recorded separately.

## Repository layout

~~~text
projects/
  butterfly/     original project, sources, stages and receipts
  tooth/         accepted film, sources, previous cuts and receipts
docs/            shared vocabulary, rubric, catalog, discussion and workflow
assets/          shared website styling
tools/           site construction and publication validation
publication/     migration and publication evidence
~~~

The repository is named svg-3d-animation-studio, and its Git remote uses that name. Earlier publication receipts retain the previous name as historical evidence. Git records the butterfly files as moves into projects/butterfly. The Pages build creates compatibility copies of earlier butterfly paths. Known legacy root hash links route to the butterfly guide.

## Build the public site

Use Python 3.13 and install requirements-site.txt. Run python tools/build_site.py. The generated site is in _site. Run python tools/verify_site.py to check the generated routes, concepts, media identities and publication privacy.

GitHub Actions builds and publishes this output on pushes to main. Source and media paths in the repository remain canonical under projects/. The public build supplies compatibility paths without duplicating the project sources in the repository.

Local browser verification uses Playwright with installed Microsoft Edge. Run python tools/test_browser.py after building. It checks responsive layouts, the catalog filters, full sound-enabled playback and legacy hash routing.

## Reproduce a film

Papilio’s commands and acceptance scope are retained in [its project README](projects/butterfly/README.md). Run those commands from projects/butterfly.

Tooth’s accepted source can be rebuilt from [the public source package](projects/tooth/downloads/tooth-accepted-source.zip), or from [the checked-in production sources](projects/tooth/production/revision-5/README.md). Its published film remains byte-identical to the accepted production export. Two local user-path fields in the public Blender source files were replaced with relative fields, and every other decompressed byte was verified unchanged.

The original Space production remains the collaborative record. The public repository contains the requested artistic discussion, sources and receipts with account-specific attachment links removed. Private .env and personal text inputs are excluded.


## Ten new films

[Screen all ten films](https://az9713.github.io/svg-3d-animation-studio/anthology.html) · [Selection, adaptations and assessments](docs/anthology.md) · [Production journey](production/anthology/journey.md)

| Board concept | Project and README |
| --- | --- |
| #1 | [The Whale in Berth Six](projects/whale-in-berth-six/README.md) |
| #3 | [The Botanistâ€™s Washing Line](projects/botanists-washing-line/README.md) |
| #4 | [The Sky Has a Hinge](projects/sky-has-a-hinge/README.md) |
| #7 | [Dress Code for a Peacock](projects/dress-code-for-a-peacock/README.md) |
| #9 | [His Excellency the Spill](projects/his-excellency-the-spill/README.md) |
| #15 | [The Last Passage for the Bronze](projects/last-passage-for-the-bronze/README.md) |
| #19 | [The Seat Facing Backwards](projects/seat-facing-backwards/README.md) |
| #25 | [The Second Tenant](projects/second-tenant/README.md) |
| #28 | [A Letter Wide Enough to Wear](projects/letter-wide-enough-to-wear/README.md) |
| #30 | [Water for the Last Balcony](projects/water-for-last-balcony/README.md) |

All ten new films are fourteen seconds at 1280×720 and 24 fps. Each has direct SVG source, a saved Blender scene, original ElevenLabs music and sound, and a standalone source package.
