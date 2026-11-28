"""Rebuild the actual public source ZIP after path metadata sanitation."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,zipfile

ROOT=Path(__file__).resolve().parents[1]
tooth=ROOT/'projects/tooth'
acceptance=json.loads((tooth/'receipts/acceptance-and-publication.json').read_text())
archive=tooth/acceptance['public_source_zip']['file']
original=json.loads((tooth/'receipts/rebuild-receipt.json').read_text())
results={}
with tempfile.TemporaryDirectory(prefix='tooth-public-package-') as td:
    extracted=Path(td)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        z.extractall(extracted)
    current=extracted/'revision-5'
    for script in ('sound.py','cut.py','screen.py'):
        subprocess.run([sys.executable,script],cwd=current,check=True)
    for name,sha in original['byte_identical_outputs'].items():
        actual=hashlib.sha256((current/name).read_bytes()).hexdigest()
        assert actual==sha,name
        results[name]=actual
report={'passed':True,'source_zip_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
        'rebuild':'Fresh extraction of the single public source ZIP outside Git',
        'byte_identical_to_accepted_production':results,'scene_path_redactions_verified_by':'acceptance-and-publication.json'}
(tooth/'receipts/public-package-rebuild.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('PASS: public source ZIP rebuilds the accepted four movies and offline player byte for byte.')
