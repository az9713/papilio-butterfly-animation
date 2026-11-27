"""Package a clean Git source revision, with a hashed inventory and usable guide."""
import argparse
import json
from pathlib import Path
import re
import posixpath
import subprocess
from urllib.parse import urljoin,urlsplit
import zipfile
from pipeline_common import ROOT,sha256,write_json,receipt

BASE='https://az9713.github.io/papilio-butterfly-animation/'


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--version',default='1.1.0')
    args=parser.parse_args(argv)
    output=args.output.resolve()
    if output.exists():raise FileExistsError('Preserve the previous package; select a new output name')
    if not re.fullmatch(r'\d+\.\d+\.\d+',args.version):raise ValueError('Use a semantic version')
    if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT).strip():
        raise RuntimeError('Commit source and documentation before packaging a release')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    tracked=subprocess.check_output(['git','ls-tree','-r','--name-only',commit],cwd=ROOT).decode().splitlines()
    selected=[]
    visual={'concept-v01.png','concept-v02.png','wing-profiles.svg','wing-profiles.png',
            'papilio-poster.png','production-recap.jpg','papilio-final-1080p-contact.jpg',
            'papilio-final-1080p-boundary.jpg'}
    for name in tracked:
        path=Path(name)
        if (path.suffix in {'.py','.json','.md','.html'} or name in visual or
            name=='requirements-review.txt' or
            (name.startswith('stages/') and (path.suffix=='.blend' or name.endswith('-views.jpg')))):
            selected.append(name)
    selected=set(selected)
    payloads={}
    for name in sorted(selected):
        data=subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)
        if name.endswith('.html'):
            text=data.decode('utf-8')
            def link(match):
                prefix,url=match.group(1),match.group(2)
                parsed=urlsplit(url)
                if parsed.scheme or url.startswith('#'):return match.group()
                target=posixpath.normpath((Path(name).parent/parsed.path).as_posix())
                if target not in selected:return prefix+'="'+urljoin(BASE+name,url)+'"'
                return match.group()
            data=re.sub(r'(href|src|poster)="([^"]+)"',link,text).encode('utf-8')
        elif name=='README.md':
            text=data.decode('utf-8')
            for omitted in ['papilio-final-1080p.mp4']:
                text=text.replace(']('+omitted+')',']('+BASE+omitted+')')
            data=text.encode('utf-8')
        payloads[name]=data
    import hashlib
    manifest={'schema_version':1,'source_release':args.version,'source_commit':commit,
              'scope':'Editable sources, scene checkpoints, review images, documentation and receipts. Movies and raw frame caches excluded; omitted media links use the published website.',
              'guide_link_rewrite':'HTML references to omitted media are rewritten to published URLs; source code and Blender checkpoints are copied byte for byte from the source commit.',
              'files':[{'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
                       for name,data in payloads.items()]}
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for name,data in payloads.items():archive.writestr(name,data)
        archive.writestr('package-manifest.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:raise RuntimeError('Archive integrity check failed')
        for entry in manifest['files']:
            if hashlib.sha256(archive.read(entry['path'])).hexdigest()!=entry['sha256']:
                raise RuntimeError('Archive manifest mismatch')
    if output.stat().st_size>10*1024*1024:raise RuntimeError('Package exceeds Space upload budget')
    report=receipt('source-package',source_version=args.version,source_commit=commit,
                   archive=output.name,bytes=output.stat().st_size,sha256=sha256(output),
                   files=len(payloads)+1,crc_and_manifest_passed=True)
    write_json(output.with_suffix('.receipt.json'),report)
    print('PAPILIO_PACKAGE_COMPLETE '+json.dumps(report),flush=True)


if __name__=='__main__':main()
