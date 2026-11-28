"""Render shared Markdown and publish peer projects with legacy butterfly URLs."""
from pathlib import Path
import hashlib,html,json,re,shutil
from urllib.parse import unquote,urlsplit
import markdown

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_site'
SKIP={'.git','.reliability-work','__pycache__','dist'}

def write_utf8(path,text):
    path.write_bytes(text.encode('utf8'))

def shell(title,body,depth=0):
    prefix='../'*depth
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · Animation Studio</title><link rel="stylesheet" href="{prefix}assets/studio.css">
<nav class="nav"><a href="{prefix}index.html">Animation Studio</a><a href="{prefix}docs/getty-aat.html">Getty AAT</a><a href="{prefix}docs/rubric.html">Rubric</a><a href="{prefix}docs/concepts.html">Thirty concepts</a><a href="{prefix}docs/workflow.html">Workflow</a></nav>
<main class="document">{body}</main><footer><a href="https://github.com/az9713/svg-3d-animation-studio">Source repository</a></footer></html>'''

def rewrite_markdown_links(body,path):
    def fix(match):
        link=html.unescape(match.group(1))
        parts=urlsplit(link)
        if parts.scheme or not parts.path.endswith('.md'):return match.group()
        target=(path.parent/unquote(parts.path)).resolve()
        if target.is_file() and target.is_relative_to(OUT):
            return 'href="'+html.escape(parts.path[:-3]+'.html'+('#'+parts.fragment if parts.fragment else ''),quote=True)+'"'
        return match.group()
    return re.sub(r'href="([^"]+)"',fix,body)

def concepts():
    data=json.loads((ROOT/'docs/concepts.json').read_text())
    entries=data['concepts']
    rows=[]
    cards=[]
    for c in sorted(entries,key=lambda c:(c['pareto_front'],c['id'])):
        scores=''.join(f'<td>{n}</td>' for n in c['forecast'])
        rows.append(f'<tr data-front="{c["pareto_front"]}" data-experience="{html.escape(c["experience"])}"><td>{c["pareto_front"]}</td><th><a href="#concept-{c["id"]}">{c["id"]}. {html.escape(c["title"])}</a></th>{scores}</tr>')
        cards.append(f'''<article class="concept" id="concept-{c["id"]}" data-front="{c["pareto_front"]}" data-experience="{html.escape(c["experience"])}">
<p class="meta">{html.escape(c["experience"])} / {html.escape(c["cause"])}</p><h2>{c["id"]}. {html.escape(c["title"])}</h2>
<p>{html.escape(c["pitch"])}</p><p><a href="{html.escape(c["aat"]["url"],quote=True)}">{html.escape(c["aat"]["term"])} · Getty {c["aat"]["id"]}</a></p>
<details><summary>Evaluation and first production test</summary><p>Forecast I / A / M / D / E &nbsp; {' / '.join(map(str,c['forecast']))}. Pareto front {c['pareto_front']}.</p><p>{html.escape(c["justification"])}</p><p>{html.escape(c["first_test"])}</p></details></article>''')
    body='''<h1>Thirty ways to make a film move</h1><p class="lead">AAT-inspired concepts, their original five-score forecasts, and the tests that could decide whether to build them.</p>
<p>Each pairing of five experiences and six causes of change appears once. The original first-prototype shortlist was Tooth (#22), Whale (#1), then Octopus (#10). The new Pareto comparison uses the saved forecasts and keeps members of each front tied. <a href="rubric.html">How the comparison works</a> · <a href="concepts-archive.html">Original full discussion</a></p>
<div class="filters"><label>Experience <select id="experience"><option>All</option><option>Discovery</option><option>Comedy</option><option>Suspense</option><option>Elegy</option><option>Liberation</option></select></label><label>Pareto front <select id="front"><option>All</option><option>1</option><option>2</option><option>3</option><option>4</option></select></label><p id="count" aria-live="polite">30 concepts</p></div>
<div class="table-wrap"><table id="comparison"><thead><tr><th>Front</th><th>Concept</th><th>Intent</th><th>Appearance</th><th>Motion</th><th>Delivery</th><th>Editability</th></tr></thead><tbody>'''
    body+=''.join(rows)+'</tbody></table></div>'+''.join(cards)
    body+='''<script>const e=document.querySelector('#experience'),f=document.querySelector('#front');function filter(){let n=0;document.querySelectorAll('.concept').forEach(c=>{c.hidden=(e.value!=='All'&&c.dataset.experience!==e.value)||(f.value!=='All'&&c.dataset.front!==f.value);if(!c.hidden)n++});document.querySelectorAll('#comparison tbody tr').forEach(c=>c.hidden=(e.value!=='All'&&c.dataset.experience!==e.value)||(f.value!=='All'&&c.dataset.front!==f.value));document.querySelector('#count').textContent=n+' concepts'}e.addEventListener('change',filter);f.addEventListener('change',filter);</script>'''
    write_utf8(OUT/'docs/concepts.html',shell('Thirty animation concepts',body,1))

def main():
    assert OUT.resolve()==ROOT.resolve()/'_site'
    if OUT.exists():
        assert (OUT/'.studio-build').exists(),'Output directory must belong to this builder'
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT/'.studio-build').write_text('Animation studio static build')
    for folder in ['projects','docs','assets','publication']:
        for source in (ROOT/folder).rglob('*'):
            if source.is_file() and not any(p in SKIP for p in source.parts) and source.suffix not in {'.pyc','.log'}:
                destination=OUT/source.relative_to(ROOT)
                destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(source,destination)
    for name in ['index.html','README.md','.nojekyll']:
        shutil.copyfile(ROOT/name,OUT/name)
    # Preserve earlier published butterfly paths in the build output. The source
    # repository keeps one canonical butterfly directory.
    legacy=[]
    butterfly=ROOT/'projects/butterfly'
    for source in butterfly.rglob('*'):
        if not source.is_file() or any(p in SKIP for p in source.parts) or source.suffix in {'.pyc','.log'}:continue
        relative=source.relative_to(butterfly)
        if relative.as_posix() in ['index.html','README.md']:continue
        destination=OUT/relative
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,destination)
        legacy.append(relative.as_posix())
    for source in list(OUT.rglob('*.md')):
        body=markdown.markdown(source.read_text(encoding='utf8'),extensions=['tables','fenced_code','toc'])
        body=rewrite_markdown_links(body,source)
        body=body.replace('<table>','<div class="table-wrap"><table>').replace('</table>','</table></div>')
        title=next(iter(re.findall(r'<h1[^>]*>(.*?)</h1>',body)),'Project document')
        destination=source.with_suffix('.html')
        write_utf8(destination,shell(re.sub('<[^>]+>','',title),body,len(destination.relative_to(OUT).parts)-1))
    # Add studio navigation and contain wide legacy tables in generated pages.
    # The original butterfly guide and its retained source hashes stay intact.
    for relative in ('projects/butterfly/index.html','projects/butterfly/development/index.html','development/index.html'):
        target=OUT/relative
        prefix='../'*(len(Path(relative).parts)-1)
        page=target.read_text(encoding='utf8')
        style='<style>body{overflow-wrap:anywhere}.studio-table{max-width:100%;overflow-x:auto}.studio-nav{display:flex;gap:22px;flex-wrap:wrap;padding:18px 24px;border-bottom:1px solid #34434e;font-size:15px}.studio-nav a{color:#8fe2d9}</style>'
        nav=f'<nav class="studio-nav"><a href="{prefix}index.html">Animation Studio</a><a href="{prefix}projects/tooth/">Tooth project</a><a href="{prefix}docs/rubric.html">Shared rubric</a></nav>'
        page=page.replace('<table>','<div class="studio-table"><table>').replace('</table>','</table></div>')
        page=page.replace('<main>',style+nav+'<main>',1)
        write_utf8(target,page)
    concepts()
    # Historical project sources retain their recorded bytes. Only the served
    # navigation is updated after the studio repository rename.
    for target in list(OUT.rglob('*.html'))+list(OUT.rglob('*.md')):
        page=target.read_text(encoding='utf8')
        updated=page.replace('https://az9713.github.io/papilio-butterfly-animation/',
                             'https://az9713.github.io/svg-3d-animation-studio/')
        updated=updated.replace('https://github.com/az9713/papilio-butterfly-animation',
                                'https://github.com/az9713/svg-3d-animation-studio')
        if updated!=page:write_utf8(target,updated)
    receipt={'canonical_projects':['projects/butterfly/','projects/tooth/'],'legacy_butterfly_paths':legacy,
             'rendered_documents':len(list(OUT.rglob('*.html')))}
    (OUT/'publication/site-build.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
    print(json.dumps({'rendered_documents':receipt['rendered_documents'],'compatibility_paths':len(legacy)}))

if __name__=='__main__':main()
