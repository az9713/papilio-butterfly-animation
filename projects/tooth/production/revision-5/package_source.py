from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,zipfile

root=Path(__file__).resolve().parent
parent=root.parent
original=['customer.png','edit.py','elevenlabs-bed.mp3','music-receipt.json','image-receipt.json','mechanism.blend','mechanism.py','score.svg']
members=['README.md','timeline.json','score.svg','bench.png','hand.png','turning.mp4','registration.json','empty.png','tooth.png',
         'macro.py','macro.blend','image-prompts.json','reaction.png','reaction-prompt.json','customer-line.mp3',
         'customer-line.wav','dialogue-generation.json','vocal-original.mp3','vocal-D.wav','vocal-generation.json',
         'vocal-preparation.json','generate_vocal.py','prepare_vocal.py','sound.py','cut.py','screen.py',
         'test_delivery.py','package_source.py','audio-cues.json']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
main=root/'Source.zip'
assets=root/'Reaction-asset.zip'
with zipfile.ZipFile(main,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for name in original:z.write(parent/name,name)
    for name in members:
        if name!='reaction.png':z.write(root/name,'revision-5/'+name)
with zipfile.ZipFile(assets,'w',compression=zipfile.ZIP_DEFLATED) as z:
    z.write(root/'reaction.png','revision-5/reaction.png')
with tempfile.TemporaryDirectory(prefix='tooth-reclaimed-') as td:
    extracted=Path(td)
    for archive in (main,assets):
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            z.extractall(extracted)
    working=extracted/'revision-5'
    for script in ('sound.py','cut.py','screen.py'):
        subprocess.run([sys.executable,script],cwd=working,check=True)
    outputs=['The Tooth - reclaimed.mp4']+[f'Pass-{i}.mp4' for i in (1,2,3)]+['Screening.html']
    comparisons={}
    for name in outputs:
        comparisons[name]=digest(working/name)
        assert comparisons[name]==digest(root/name),name
report={'archives':{a.name:{'sha256':digest(a),'bytes':a.stat().st_size} for a in (main,assets)},
        'source_files':len(original)+len(members),'rebuild':'fresh temporary extraction outside Git using cached Blender layers',
        'byte_identical_outputs':comparisons}
(root/'rebuild-receipt.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('PASS: both source ZIPs rebuilt four byte-identical movies and an identical offline player.')
