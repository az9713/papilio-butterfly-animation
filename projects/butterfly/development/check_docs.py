"""Check guide links, published text privacy, and desktop/mobile layout."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit,unquote,urljoin
import urllib.request
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'development'))
from record_step import save


class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        for key in ['href','src','poster']:
            if attrs.get(key):self.links.append(attrs[key])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--event',required=True)
    parser.add_argument('--live-url');args=parser.parse_args()
    checked=0
    for name in ['index.html','development/index.html']:
        path=ROOT/name;links=Links();links.feed(path.read_text(encoding='utf-8'))
        assert len(links.ids)==len(set(links.ids))
        for link in links.links:
            parsed=urlsplit(link)
            if parsed.scheme:continue
            target=(path.parent/unquote(parsed.path)).resolve() if parsed.path else path
            assert target.is_file(),(name,link)
            if parsed.fragment:
                fragment=Links();fragment.feed(target.read_text(encoding='utf-8'))
                assert parsed.fragment in fragment.ids,(name,link)
            checked+=1
    paths=[p for p in ROOT.rglob('*') if p.is_file() and
           not any(part in {'.git','.reliability-work','__pycache__','dist'} for part in p.parts) and
           p.suffix in {'.py','.json','.md','.html','.txt'} and p.name!='publication-check.json']
    account=Path.home().name
    for path in paths:
        text=path.read_text(encoding='utf-8')
        assert not re.search(r'(?i)\b'+re.escape(account)+r'\b',text),path.relative_to(ROOT)
        assert not re.search(r'(?i)[A-Z]:[/\\]+Users[/\\]+|chatgpt\.com/(?:space|c)/|claude\.ai/(?:chat|artifact)/',text),path.relative_to(ROOT)
        assert path.name not in ['README.txt','transcript.txt','HANDOFF.md'],path
    if args.live_url:
        import subprocess
        for name in ['index.html','development/index.html','source-release.json']:
            with urllib.request.urlopen(urljoin(args.live_url,name),timeout=30) as response:data=response.read()
            assert data==subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT),name
    with sync_playwright() as pw:
        browser=pw.chromium.launch(channel='msedge')
        page=browser.new_page(viewport={'width':1440,'height':1000})
        address=urljoin(args.live_url,'development/') if args.live_url else (ROOT/'development/index.html').as_uri()
        page.goto(address,wait_until='domcontentloaded')
        assert page.locator('h1').inner_text()=='Source reliability and development record'
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        browser.close()
    result={'accepted':True,'html_local_links_checked':checked,'text_files_scanned':len(paths),
            'personal_paths_or_excluded_files_found':False,'desktop_mobile_layout_passed':True,
            'live_served_bytes_match_commit':bool(args.live_url)}
    save(args.event,result);print(json.dumps(result))


if __name__=='__main__':main()
