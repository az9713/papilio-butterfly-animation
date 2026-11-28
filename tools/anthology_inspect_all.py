"""Make screening evidence from decoded movies while preserving all film bytes."""
from pathlib import Path
import hashlib,json
from anthology_finish import finish

ROOT=Path(__file__).resolve().parents[1]
for p in json.loads((ROOT/'production/anthology/selection.json').read_text(encoding='utf8')):
    path=ROOT/'projects'/p['slug'];before=hashlib.sha256((path/'film.mp4').read_bytes()).hexdigest()
    finish(path,encode=False)
    assert hashlib.sha256((path/'film.mp4').read_bytes()).hexdigest()==before
print('TEN_ENCODED_EVIDENCE_INSPECTIONS_OK')
