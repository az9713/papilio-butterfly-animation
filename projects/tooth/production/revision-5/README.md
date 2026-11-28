# The Tooth That Didn’t Sing — song, interruption and return

This 16-second revision gives the customer an audible role, interrupts it with the repaired box and returns the same note after the tooth is removed. GPT Image supplied the puppet plates. The SVG score and procedural Blender mechanism supply the music box and removable tooth. ElevenLabs supplied the instrumental, the new sung ah and the existing dialogue.

## Screening

Open Screening.html to choose the full film or any of the three sound-on passes.

| Event | Film time |
| --- | --- |
| His first sung D | 3.50–4.70 s |
| He tries the same note | 8.00–8.30 s |
| The metal note interrupts | 8.25 s |
| His voice stops and his jaw closes | 8.30 s onward |
| “That was my part” | 8.50–9.61 s |
| Her concerned reaction | 9.67–10.38 s |
| She removes the tooth | 10.38–12.88 s |
| He sings the same full D again | 14.00–15.20 s |

The first and returned vocals use the same prepared human vocal recording. Hissing breath effects were removed. The customer's mouth opens for singing, closes after the interruption and opens again for the returned note. His shoulder and head drop accompany the interruption. The final pose settles with closed lips after the note ends.

## Rebuild

Extract tooth-accepted-source.zip into a fresh folder. The public package contains revision-5, its shared parent sources and the reaction plate together.

Use Python 3.13, NumPy, SciPy, OpenCV, Pillow, FFmpeg/ffprobe, Playwright and installed Microsoft Edge on Windows. The image renderer uses the installed Georgia and Segoe UI fonts. From revision-5, run these commands.

1. Run python sound.py to create mix.wav and separate voice, box, tool and background stems.
2. Run python cut.py to build The Tooth - reclaimed.mp4 and Pass-1.mp4 through Pass-3.mp4.
3. Run python screen.py to create the portable offline player.
4. Run python test_delivery.py to check the actual encoded sound, jaw and extraction frames and eight complete browser playthroughs. The test creates end-to-end.json and a contact sheet with timestamps.

timeline.json is the shared timing input for sound, picture and verification. score.svg carries the note pitches and beat positions. The score is performed at 120 BPM in this cut. Cached Blender layers and turning footage support an exact editorial rebuild. macro.py and the Blender scenes are included for geometric revisions. Rerendering with different scene settings can produce different pixels.

generate_vocal.py is the optional generation script and reads a separately supplied parent .env. Rebuilding uses the included vocal-D.wav and needs no new generation. vocal-generation.json and vocal-preparation.json record the generated asset, source trim and tuning. Existing dialogue and background receipts accompany their media. The generation model's requested pitch was corrected from its measured pitch, with vocal formants preserved.

## Verification boundaries

The delivery tests check decoded audio, the interrupted vocal ending, continuing metal note, matching first/returned vocals, pitch, jaw change, a visible cleared socket, media formats, pass boundaries and player completion. The source package test rebuilds from both ZIPs outside Git and compares all four movies and the player byte for byte. Fresh audience comprehension remains a separate screening result.
