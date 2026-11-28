"""Check deployed routes and the exact accepted movie/source download bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,hashlib,json,urllib.request

ROOT=Path(__file__).resolve().parents[1]
BASE='https://az9713.github.io/papilio-butterfly-animation/'
routes=['','projects/butterfly/','projects/tooth/','projects/tooth/README.html',
        'docs/getty-aat.html','docs/rubric.html','docs/concepts.html','docs/concepts-archive.html',
        'docs/discussion.html','docs/workflow.html','projects/tooth/assessment.html',
        'projects/butterfly/development/','development/']
checks={
    'projects/tooth/film.mp4':ROOT/'projects/tooth/film.mp4',
    'projects/tooth/downloads/tooth-accepted-source.zip':ROOT/'projects/tooth/downloads/tooth-accepted-source.zip',
    'papilio-final-1080p.mp4':ROOT/'projects/butterfly/papilio-final-1080p.mp4',
    'projects/butterfly/papilio-final-1080p.mp4':ROOT/'projects/butterfly/papilio-final-1080p.mp4'
}

def fetch(path):
    with urllib.request.urlopen(BASE+path,timeout=35) as response:
        data=response.read()
        assert response.status==200,path
    record={'path':path,'status':200,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    if path in checks:
        assert record['sha256']==hashlib.sha256(checks[path].read_bytes()).hexdigest(),path
        record['exact_file_match']=True
    else:
        text=data.decode('utf8')
        if not path:assert '<h1>Animation Studio</h1>' in text
        if path=='projects/tooth/':assert 'film.mp4' in text and 'Reclaimed' in text
        if path=='docs/concepts.html':assert text.count('class="concept"')==30
    return record

def main():
    with ThreadPoolExecutor(max_workers=5) as executor:
        records=list(executor.map(fetch,routes+list(checks)))
    result={'passed':True,'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'site':BASE,'checks':records,'scope':'Live HTTP routes and byte-identical accepted media/source downloads'}
    (ROOT/'publication/live-verification.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print('PASS:',len(records),'live routes, accepted film/source bytes and legacy butterfly movie bytes.')

if __name__=='__main__':main()
