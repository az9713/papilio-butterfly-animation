# Standalone source reliability closure

Release 1.1.1 closes the journal-refresh failure in the source-only handoff. The original 12-second film, SVG, images, and Blender scene checkpoints are preserved. This is the final source-reliability iteration for the agreed Windows workflow; further work can focus on creative variants.

## Failure and repair

The 1.1.0 journal generator hashed historical movies that were intentionally omitted from the ZIP, then unconditionally invoked Git history. It also wrote the receipt index before those operations could fail. The prior reassessment diagnostic is retained in `receipts/journal-closure-001-before-diagnostic.json`.

The repaired generator hashes files that are present. For absent historical evidence it requires a valid retained SHA-256 and marks it as a retained historical digest, not a new measurement. Without this project's own Git checkout it preserves and labels the packaged commit snapshot. An unrelated parent checkout cannot be adopted as project history. Original chronology, additional recorded stages, and immutable execution receipts are retained.

Journal refresh uses only Python's standard library. It does not require Git, Blender, FFmpeg, Pillow, or Playwright. It preserves `environment-tested.json` rather than claiming the historical rendering tests ran again. `journal-refresh.json` records the actual journal runtime and evidence origins.

All input parsing, evidence fallbacks, Git-history fallback, and guide validation finish before the first generated file is written. Individual output files use temporary siblings and atomic replacement. This protects against the diagnosed prerequisite failures; it is not an all-files transaction against a disk failure. Missing media links use the published website.

A candidate acceptance run completed the production and journal commands, then stopped during receipt collection because a shared prefix also matched already-packaged historical receipts. The collector correctly refused to overwrite one. The final verifier collects only newly created receipts; the stopped run and diagnosis remain in `receipts/journal-closure-098-stopped.json` and `receipts/journal-closure-019-collection-diagnosis.json`.

## Complete standalone acceptance

The repeatable verifier extracts the exact source ZIP into a fresh system temporary directory outside any Git checkout. It does not supply the omitted movies. It creates a new Python virtual environment and installs only the pinned review dependencies.

```text
python development/verify_standalone.py --archive PATH_TO_SOURCE_ZIP --blender BLENDER_EXECUTABLE --run-id UNIQUE_ID --report NEW_REPORT_PATH
```

The checks include:

- Archive CRC and every manifest digest.
- Journal refresh with Python site packages disabled and an empty executable PATH.
- All 16 unit tests, including six journal regression tests.
- Baseline reconstruction, saved-scene verification of all 22 controls, explicit CLI overrides, and explicit scene selection.
- Audit, CPU rendering of a disposable two-second 12-frame clip, safe resume, rejection of mixed revisions and corrupt frames, encoding, complete Edge playback, and loop replay.
- A newly recorded event followed by another journal refresh, with the new event and integration summary present in the receipt inventory.
- Preservation of prior receipt bytes, Git-history snapshot, omitted-media historical hashes, and historical tested-environment record.

The authoritative result is the version-bound `papilio-source-v1.1.1-verification.json` supplied with the GitHub release and the corresponding `receipts/journal-closure-099-summary.json` on the published development record. The source ZIP is frozen before this acceptance run, so these post-packaging receipts are supplied alongside it rather than retroactively altering the tested archive. `package-manifest.json` identifies the ZIP source commit; the current ZIP-hash release receipt is not embedded inside its own archive.

## Revised rubric assessment

| Dimension | Initial | After first repair | After standalone closure | Evidence |
| --- | --- | --- | --- | --- |
| Intent | 3 | 3 | 3 | Same recognizable quiet museum sculpture and unchanged film. |
| Appearance | 3 | 3 | 3 | Same poster, multi-angle reviews, materials, geometry, and film bytes. |
| Motion | 3 | 3 | 3 | Same six wing cycles, one orbit, and retained loop checks. |
| Delivery | 3 | 3 | 3 | Same valid 1080p film; public delivery verified separately. |
| Editability including source reliability | 2 | 2 | 3 | Controls and revisions repaired; the complete declared source-only workflow now includes a tested journal refresh outside Git. |

A score of 3 means the agreed workflow meets its standard; it does not establish universal portability. Windows, Blender 5.3, FFmpeg, CPU rendering, and installed Microsoft Edge form the declared acceptance environment. A new Python environment is tested on the same machine, not a second operating system or machine. Physical-phone playback and other platforms remain unverified. Historical missing timestamps remain missing and are not reconstructed as exact execution events.

The score is conditional on the version-bound acceptance receipt reporting success. Aesthetic choices such as wing phase, camera easing, and detail framing are future creative directions, not additional source-reliability blockers. No artistic revision is included in this closure.
