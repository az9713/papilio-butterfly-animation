# Animation Studio

Two peer animation projects share one discovery, evaluation and publication workflow.

| Project | Film | Sources and development |
| --- | --- | --- |
| [Papilio butterfly](projects/butterfly/) | Twelve-second silent kinetic-sculpture loop | Editable Blender scene, SVG wing profiles, source release 1.1.1 and retained reliability receipts. |
| [The Tooth That Didn’t Sing](projects/tooth/) | Accepted sixteen-second film with sound | SVG pin score, Blender layers, character plates, ElevenLabs audio, scripted edit, prior cuts and acceptance evidence. |

[Open the public studio](https://az9713.github.io/animation-studio/) · [Watch Tooth](https://az9713.github.io/animation-studio/projects/tooth/) · [Watch Papilio](https://az9713.github.io/animation-studio/projects/butterfly/)

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

The repository is named animation-studio, and its Git remote uses that name. Earlier publication receipts retain the previous name as historical evidence. Git records the butterfly files as moves into projects/butterfly. The Pages build creates compatibility copies of earlier butterfly paths. Known legacy root hash links route to the butterfly guide.

## Build the public site

Use Python 3.13 and install requirements-site.txt. Run python tools/build_site.py. The generated site is in _site. Run python tools/verify_site.py to check the generated routes, concepts, media identities and publication privacy.

GitHub Actions builds and publishes this output on pushes to main. Source and media paths in the repository remain canonical under projects/. The public build supplies compatibility paths without duplicating the project sources in the repository.

Local browser verification uses Playwright with installed Microsoft Edge. Run python tools/test_browser.py after building. It checks responsive layouts, the catalog filters, full sound-enabled playback and legacy hash routing.

## Reproduce a film

Papilio’s commands and acceptance scope are retained in [its project README](projects/butterfly/README.md). Run those commands from projects/butterfly.

Tooth’s accepted source can be rebuilt from [the public source package](projects/tooth/downloads/tooth-accepted-source.zip), or from [the checked-in production sources](projects/tooth/production/revision-5/README.md). Its published film remains byte-identical to the accepted production export. Two local user-path fields in the public Blender source files were replaced with relative fields, and every other decompressed byte was verified unchanged.

The original Space production remains the collaborative record. The public repository contains the requested artistic discussion, sources and receipts with account-specific attachment links removed. Private .env and personal text inputs are excluded.
