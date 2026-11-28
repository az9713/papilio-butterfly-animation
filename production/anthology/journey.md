# Production journey

The user selected the final repository name svg-3d-animation-studio after source inspection confirmed the SVG roles in Butterfly and Tooth. GitHub repository identity was retained through both renames. The final renamed Pages site passed seventeen live route checks and exact media/source download comparisons.

The user then commissioned ten films from the thirty-concept board and approved 12–16 seconds at 1280×720 and 24 fps. The selected concepts are 1, 3, 4, 7, 9, 15, 19, 25, 28 and 30. All had an Appearance forecast of 4. The selection varies optical mechanism, material, scale and emotional register.

## First construction and preview

Ten project briefs and ten SVG inputs were authored. The common builder contains separately staged scenes. Each independent project receives a standalone copy and reads its own SVG and brief. Five key frames per scene were rendered at 640×360 before full rendering.

The first preview revealed these defects:

- Animated sphere props lost their modeled proportions when their object scale was reset by visibility animation. The scale is now applied to the underlying mesh before keyframes are inserted.
- Smooth normals across thin extruded profiles produced misleading surface highlights. Front and side polygon faces now use flat normals.
- The astrolabe and casting were cropped vertically. Their cameras now include the complete defining silhouette.
- The first iridescence ramp did not provide the intended black opening. Its input now explicitly measures one minus the absolute camera-ray/normal dot product, then maps the actual viewing angle to black, green and violet.
- The reverse weaving letters appeared mirrored. Their back-face construction now precompensates for the cloth turn.
- The panorama extended outside its window. A world-position mask clips the painted materials to the aperture.
- Water channels were partly behind the buildings. They now run in front, foundations support the houses, and the birdbath has a pedestal. The water ribbon grows in sequence after the three gate actions.
- The cleaner and sisters first had oval placeholder hands. The production versions include attached fingers and thumbs.

The original preview images remain in each project’s previews/iteration-1 directory. Repaired storyboards remain beside them.

## Sound generation and mix repair

ElevenLabs generated ten music_v2 instrumental stems and ten eleven_text_to_sound_v3 effects stems. Six additional signature effects provide rinse, detent, sneeze, vent, footsteps and bird cues. Every request has a model, prompt, status, request identifier when supplied, and output digest receipt. Cached successful outputs prevent unnecessary paid regeneration.

The first signature-cue mix failed because FFmpeg rejected duration notation without a leading zero. The duration literals were corrected and all six cue mixes completed. The generation outputs were reused.

Package inspection then caught loudness normalization leaving the WAV mix at its internal higher sample rate. The final mix commands now explicitly output 48 kHz stereo. Earlier mix receipts are retained as superseded iteration records, and final-mix.json identifies the current WAV. Already encoded films were re-encoded with that final mix.

## Text encoding repair

The local Windows default encoding corrupted curly apostrophes in copied brief text. UTF-8 reads are now explicit in the new production scripts. The brief files, players and Space text were corrected. SVG coordinates and animation staging were unaffected. Scene/source verification follows the final source refresh.

## Verification scope

The first source audit flagged Astrolabe because parallel sphere construction reordered polygon storage. Its vertices, oriented face connectivity, material indices and smooth flags were the same. The audit now canonicalizes cyclic face starts and sorts the oriented face records, preserving their winding and attributes. The independently rebuilt full-resolution hero frame also passes comparison with the encoded film. Audits start Blender with factory settings to exclude local add-on startup state.

The final contact sheets and posters are taken from decoded movie frames. This replaced the earlier contact-sheet implementation that used the corresponding unencoded render frames. The movies themselves were preserved during that evidence refresh.

Encoding checks cover the complete decode, 336 frames, 1280×720, 24 fps, fourteen seconds, non-silent audio without clipping and visible frame changes. Browser tests require the Play with sound control to reach the end at normal speed with muted false. Source package checks and film assessments are recorded separately. Passing delivery tests alone does not establish a first-time viewer’s understanding or exceptional artistic quality.
