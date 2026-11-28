"""Refresh final scene metadata, remove local path fields, preserve film identity."""
from pathlib import Path
import hashlib,json,re,subprocess
import zstandard

ROOT=Path(__file__).resolve().parents[1]
BLENDER='C:/Program Files/Blender Foundation/Blender 5.3/blender.exe'

def main():
    plans=json.loads((ROOT/'production/anthology/selection.json').read_text(encoding='utf8'))
    for p in plans:
        project=ROOT/'projects'/p['slug'];movie=hashlib.sha256((project/'film.mp4').read_bytes()).hexdigest()
        # Final canonical text bytes precede scene identity properties.
        for file in project.rglob('*'):
            if file.is_file() and file.suffix in {'.py','.md','.json','.svg','.html'}:
                raw=file.read_bytes();file.write_bytes(raw.replace(b'\r\n',b'\n'))
        with (ROOT/'.publication-work'/f"{p['slug']}-source-refresh.log").open('w',encoding='utf8') as out:
            result=subprocess.run([BLENDER,'--background','--factory-startup','--threads','2','--python',str(project/'source/build_scene.py')],stdout=out,stderr=subprocess.STDOUT)
        assert result.returncode==0
        scene=project/'source/scene.blend';data=scene.read_bytes();compressed=data.startswith(b'\x28\xb5\x2f\xfd')
        if compressed:
            with zstandard.ZstdDecompressor().stream_reader(data) as stream:raw=stream.read()
        else:raw=data
        spans=[]
        def replace(m):spans.append((m.start(),m.end()));return b'//'.ljust(len(m.group()),b'\0')
        safe=re.sub(rb'[A-Za-z]:[/\\]Users[/\\][^\x00\r\n]+',replace,raw)
        assert len(raw)==len(safe)
        allowed=set(i for a,b in spans for i in range(a,b))
        assert all(i in allowed for i,(a,b) in enumerate(zip(raw,safe)) if a!=b)
        final=zstandard.ZstdCompressor(level=3).compress(safe) if compressed else safe
        scene.write_bytes(final)
        record=json.loads((project/'receipts/scene.json').read_text(encoding='utf8'));record['scene_sha256']=hashlib.sha256(final).hexdigest()
        record['builder_sha256']=hashlib.sha256((project/'source/build_scene.py').read_bytes()).hexdigest()
        (project/'receipts/scene.json').write_bytes((json.dumps(record,indent=2)+'\n').encode('utf8'))
        (project/'receipts/public-scene.json').write_bytes((json.dumps({'path_fields_replaced':len(spans),'only_path_field_bytes_changed':True,'before_sha256':hashlib.sha256(data).hexdigest(),'after_sha256':hashlib.sha256(final).hexdigest(),'film_unchanged_during_source_refresh':hashlib.sha256((project/'film.mp4').read_bytes()).hexdigest()==movie,'scope':'Final source identity refreshed without rendering or changing the movie. Any absolute local user path fields are replaced with relative fields.'},indent=2)+'\n').encode('utf8'))
        print('FINAL_SOURCE_OK',p['concept_id'],flush=True)

if __name__=='__main__':main()
