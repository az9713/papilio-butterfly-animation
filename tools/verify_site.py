"""Validate the generated studio site, peer migration and accepted media."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,json,re,zipfile

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'_site'
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        for key in ('href','src','poster'):
            if attrs.get(key):self.links.append(attrs[key])

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    pages={}
    for path in SITE.rglob('*.html'):
        parsed=Page();parsed.feed(path.read_text(encoding='utf8'))
        assert len(parsed.ids)==len(set(parsed.ids)),('duplicate IDs',path.relative_to(SITE))
        pages[path.resolve()]=parsed
    count=0
    for path,page in pages.items():
        for link in page.links:
            parts=urlsplit(link)
            if parts.scheme or link.startswith('//'):continue
            target=(SITE/unquote(parts.path).lstrip('/')) if parts.path.startswith('/') else path.parent/unquote(parts.path)
            if not parts.path:target=path
            if target.is_dir():target=target/'index.html'
            target=target.resolve()
            assert target.is_relative_to(SITE.resolve()) and target.is_file(),('missing route',str(path.relative_to(SITE)),link)
            if parts.fragment and target.suffix=='.html':
                assert parts.fragment in pages[target].ids,('missing anchor',str(path.relative_to(SITE)),link)
            count+=1
    baseline=json.loads((ROOT/'publication/migration-baseline.json').read_text())
    preserved=0
    for old,sha in baseline['butterfly_files'].items():
        if old in baseline['kept_root_files']:continue
        moved=ROOT/'projects/butterfly'/old
        canonical=baseline.get('git_canonical_sha256',{}).get(old,sha)
        assert digest(moved) in {sha,canonical},('butterfly migration changed bytes',old)
        preserved+=1
    tooth=ROOT/'projects/tooth'
    acceptance=json.loads((tooth/'receipts/acceptance-and-publication.json').read_text())
    assert digest(tooth/'film.mp4')==acceptance['master_sha256']
    for name,sha in acceptance['public_source_files'].items():
        assert digest(tooth/'production'/name)==sha,('public source changed',name)
    archive=tooth/acceptance['public_source_zip']['file']
    assert digest(archive)==acceptance['public_source_zip']['sha256']
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert set(z.namelist())==set(acceptance['public_source_files'])
        for name in z.namelist():
            assert hashlib.sha256(z.read(name)).hexdigest()==acceptance['public_source_files'][name]
    data=json.loads((ROOT/'docs/concepts.json').read_text())
    concepts=data['concepts']
    assert len(concepts)==30 and {c['id'] for c in concepts}==set(range(1,31))
    assert len({(c['experience'],c['cause']) for c in concepts})==30
    assert len({c['aat']['id'] for c in concepts})==30
    assert all(len(c['forecast'])==5 and all(n in range(5) for n in c['forecast']) for c in concepts)
    remaining=list(concepts);front=1
    while remaining:
        layer=[a for a in remaining if not any(b is not a and all(v>=w for v,w in zip(b['forecast'],a['forecast'])) and any(v>w for v,w in zip(b['forecast'],a['forecast'])) for b in remaining)]
        assert all(c['pareto_front']==front for c in layer)
        remaining=[c for c in remaining if c not in layer];front+=1
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(p in {'.git','.reliability-work','.publication-work','_site','__pycache__'} for p in path.parts):continue
        relative=path.relative_to(ROOT)
        if len(relative.parts)==1 and path.name not in {'README.md','index.html','requirements-site.txt','.gitignore','.gitattributes','.nojekyll'}:continue
        assert path.name not in {'README.txt','transcript.txt','HANDOFF.md','.env'},path
        if path.suffix in {'.md','.html','.json','.py','.yml','.css'}:
            text=path.read_text(encoding='utf8')
            assert not re.search(r'[A-Za-z]:[/\\]+Users[/\\]+',text),('private path',path.relative_to(ROOT))
            assert not re.search(r'https://chatgpt\.com/(?:space|c)/|library-file:[A-Za-z0-9_]{12,}',text),('private account reference',path.relative_to(ROOT))
    assert all((ROOT/p/'README.md').is_file() for p in ['projects/butterfly','projects/tooth'])
    report={'passed':True,'html_documents':len(pages),'local_links_and_assets':count,
            'butterfly_files_preserved':preserved,'concepts':30,
            'front_1':[c['id'] for c in concepts if c['pareto_front']==1],
            'accepted_tooth_movie_unchanged':True,'source_zip_inventory_verified':True,
            'private_input_files_and_account_links_excluded':True,
            'readmes':['README.md','projects/butterfly/README.md','projects/tooth/README.md']}
    (SITE/'publication/site-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report))

if __name__=='__main__':main()
