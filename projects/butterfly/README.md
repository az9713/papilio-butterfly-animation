# Papilio butterfly animation

![Brass and turquoise butterfly sculpture](papilio-poster.png)

A 12-second, 1080p, 24 fps kinetic sculpture built using the SVG & 3D Design workflow, GPT Image references, and Blender 5.3.

Source reliability release **1.1.1** closes the standalone ZIP journal-refresh failure, following the 1.1.0 repairs to configuration controls, explicit revision selection, safe render resumption, and scene-derived timing. The existing film, scene checkpoints, and visual assets are preserved.

- [Development journey, issues, fixes, commands, and evidence](https://az9713.github.io/papilio-butterfly-animation/development/)
- [Versioned source package](https://github.com/az9713/papilio-butterfly-animation/releases/download/v1.1.1/papilio-source-v1.1.1.zip)
- [Current build and render instructions](https://az9713.github.io/papilio-butterfly-animation/development/#rebuild)
- [Configuration contract](https://az9713.github.io/papilio-butterfly-animation/development/#controls)
- [Complete standalone verification summary](development/receipts/journal-closure-099-summary.json)

JSON settings supply the defaults; explicit `--res` and `--samples` flags override them and are recorded. Rendering requires both `--scene` and `--output`. Use `--plan` to inspect the selected scene and settings before rendering. The source-only ZIP includes the matching guide, dependencies, checkpoints, and receipts; movie links in its guide use the published website.

The development record preserves the original failed check and its diagnosis. Earlier production stages are reconstructed from saved artifacts; execution receipts are recorded from the reliability repair onward. Tests cover Windows, Blender 5.3, CPU rendering, automatic OptiX selection, and Edge playback. Other platforms remain unverified.

- [Watch the animation and explore the visual guide](https://az9713.github.io/papilio-butterfly-animation/)
- [Download or play the final film](papilio-final-1080p.mp4)
- [Open the editable Blender scene](stages/final-v01/final-v01.blend)
- [Local HTML guide](index.html): after cloning or downloading the repository, open `index.html` in a browser. The live guide is published through GitHub Pages from `main`, at the repository root.
- [Production recap](production-recap.jpg)

The HTML guide is the complete project documentation. It contains the exact image prompts, tool inputs/outputs, dependencies, commands, and validation limits. The image tool did not expose an exact model version. The Blender scene has no external texture dependencies. The movie is unchanged from the completed production delivery.

Raw frame caches, logs, credentials, and private conversation material are excluded. Blender checkpoint path metadata and JSON receipt paths have been made relative, and PNG metadata has been removed with pixel bytes verified unchanged. Original local production artifacts are preserved separately.

## Standalone journal refresh

After recording a change, run `python development/update_journey.py` from the extracted project root. Journal refresh requires only Python standard-library modules; absent historical media and Git history use explicitly labelled retained evidence. It preserves the historical tested-environment record.

[Issue, repair, acceptance procedure, and revised assessment](development/source-reliability-closure.md) describe the complete build, audit, render, encode, playback, receipt, and refresh acceptance test. Post-packaging verification receipts accompany the frozen source ZIP on GitHub Releases.

## Sources and references

The [full bibliography and project-input provenance](https://az9713.github.io/papilio-butterfly-animation/#sources) are also included in the HTML guide.

### Original tutorial and plugin

- [OpenAI — From concept art to editable SVGs and 3D scenes](https://learn.chatgpt.com/guides/svg-3d-design) — Original guide for developing a visual reference, constructing editable SVG or 3D geometry, and iterating on the result.
- [OpenAI — Experiment with SVG & 3D Design with the Codex Plugin](https://www.youtube.com/watch?v=1u0hTd86_HU&t=11s) — Original video reference supplied with the project. Published by OpenAI; its title and channel were confirmed through YouTube metadata.
- [OpenAI — SVG & 3D Design plugin](https://chatgpt.com/plugins/Plugin_13c5903473e081919917a1070fad1dd1) — Public plugin listing linked by the OpenAI guide. Production used the installed svg-3d-design skill, version 0.1.2; its instructions guided construction and visual review.

### Image generation and model background

- [OpenAI — Image generation in ChatGPT](https://learn.chatgpt.com/docs/image-generation) — Image creation and editing documentation. The earlier https://learn.chatgpt.com/codex/image-generation address redirects here.
- [OpenAI — GPT-Image-2.5 Sunburst model documentation](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst) — Background model reference from the original walkthrough. It does not identify the model used to generate this project’s images.
- [OpenAI — GPT-Image-2.5 Flare model documentation](https://developers.openai.com/api/docs/models/gpt-image-2.5-flare) — Background model reference from the original walkthrough. Production used the built-in image tool, which did not expose an exact model identifier.

### Blender workflow references

- [Blender Manual — Rendering From The Command Line](https://docs.blender.org/manual/en/latest/advanced/command_line/render.html) — Background rendering and command-line execution. The project ran local Blender processes with Python scripts.
- [Blender Python API — Quickstart and Python interpreter](https://docs.blender.org/api/current/info_quickstart.html#using-the-python-interpreter) — The bpy interface for constructing and editing scene data.
- [Blender Manual — Import SVG as Curves](https://docs.blender.org/manual/en/latest/files/import_export/svg_curve.html) — Alternative SVG import route discussed in the walkthrough. This production instead used a focused M/C/Z path reader in build_scene.py.
- [Blender 5.3 Manual — Rendering Animations](https://docs.blender.org/manual/en/5.3/render/output/animation.html) — Version-specific animation and frame-sequence workflow. The original walkthrough also linked the latest-version page at https://docs.blender.org/manual/en/latest/render/output/animation.html.

### Technical documentation for reproduction and verification

- [W3C — SVG 2 Paths](https://www.w3.org/TR/SVG2/paths.html) — Path syntax, including moveto, cubic Bézier curves, and closepath.
- [FFmpeg — image2 image sequences](https://ffmpeg.org/ffmpeg-formats.html#image2-1) — Image-sequence format reference carried forward from the original walkthrough.
- [FFmpeg — command-line documentation](https://ffmpeg.org/ffmpeg.html) — Encoding and decoding command reference.
- [FFmpeg — ffprobe documentation](https://ffmpeg.org/ffprobe.html) — Inspecting movie codec, dimensions, duration, frame rate, and decoded frame count.
- [Pillow — Image module](https://pillow.readthedocs.io/en/stable/reference/Image.html) — Image opening, verification, pixel comparisons, and contact-sheet processing.
- [Microsoft — Playwright for Python](https://playwright.dev/python/docs/intro) — Browser automation used for complete video playback, loop replay, and layout checks.
- [Python — Python 3.13 documentation](https://docs.python.org/3.13/) — Standard-library reference for local production and verification helpers.
- [GitHub Docs — Creating a GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site) — Static publication of this guide from the main branch at the repository root.
- [GitHub CLI — gh repo create](https://cli.github.com/manual/gh_repo_create) — Repository creation command reference.

### Project inputs and generated references

The concept images were generated for this project. The SVG and parameters are the inputs to the procedural Blender build; no external 3D asset or image texture was used.

- [First generated concept](concept-v01.png)
- [Refined sculpture concept](concept-v02.png)
- [Exact image prompts](https://az9713.github.io/papilio-butterfly-animation/#prompts)
- [Editable SVG wing contours](wing-profiles.svg)
- [Original contour control points](profile-control-points.json)
- [Selected scene parameters](config.json)
- [Blender scene builder](build_scene.py)
- [Final scene audit](final-scene-audit.json)
- [Final movie validation](papilio-final-1080p-review.json)
