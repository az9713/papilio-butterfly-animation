"""Verify a released source ZIP, including journal refresh, outside any Git checkout."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'development'))
from pipeline_common import sha256
from record_step import clean,run,save


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,required=True)
    parser.add_argument('--blender',type=Path,required=True)
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    if args.report.exists():raise FileExistsError('Preserve the previous report')
    work=Path(tempfile.mkdtemp(prefix='papilio-standalone-'))
    source=work/'source';source.mkdir()
    with zipfile.ZipFile(args.archive) as z:
        assert z.testzip() is None
        manifest=json.loads(z.read('package-manifest.json'))
        for entry in manifest['files']:
            assert hashlib.sha256(z.read(entry['path'])).hexdigest()==entry['sha256']
        z.extractall(source)
    assert not (source/'.git').exists()
    git=subprocess.run(['git','rev-parse','--show-toplevel'],cwd=source,capture_output=True)
    assert git.returncode!=0,'Extraction must be outside every Git checkout'
    assert not list(source.glob('*.mp4')),'Do not add omitted movies to make the test pass'
    retained=json.loads((source/'development/history.json').read_text())
    historical={p.name:sha256(p) for p in (source/'development/receipts').glob('*.json') if p.name!='index.json'}
    environment=sha256(source/'development/environment-tested.json')
    def step(label,command,expect=0):
        return run(args.run_id+'-'+label,command,cwd=source,expected_exit=expect)
    step('011-create-isolated-environment',[sys.executable,'-m','venv',work/'venv'])
    python=work/'venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    # No site packages and no executable lookup: journal refresh really is stdlib-only.
    journal=[python,'-S','-c',"import os,runpy; os.environ['PATH']=''; runpy.run_path('development/update_journey.py',run_name='__main__')"]
    step('012-tool-free-journal-refresh',journal)
    first=json.loads((source/'development/history.json').read_text())
    assert first['git_history']==retained['git_history']
    assert 'retained' in first['git_history_origin']['mode']
    omitted=[e for s in first['historical_stages'] for e in s['evidence'] if 'retained' in e.get('hash_origin','')]
    assert {e['path'] for e in omitted}=={'motion-preview-v01.mp4','papilio-final-1080p.mp4'}
    step('013-install-declared-dependencies',[python,'-m','pip','install','-r','requirements-review.txt'])
    units=step('014-extracted-unit-tests',[python,'-m','unittest','discover','-s','tests','-v'])
    unit_count=int(re.search(r'Ran (\d+) tests',units.stderr).group(1))
    assert unit_count>=16
    step('015-complete-production-workflow',[python,'development/verify_reliability.py','--blender',args.blender,
                                            '--run-id',args.run_id+'-workflow'])
    integration=json.loads((source/'development/receipts'/(args.run_id+'-workflow-099-summary.json')).read_text())
    assert integration['passed']
    step('016-record-new-event',[python,'development/record_step.py',args.run_id+'-new-event','--',python,
                                '-c',"print('Standalone journal acceptance: edited scene, audit, render, resume, encode and playback completed')"])
    step('017-refresh-after-new-event',journal)
    index=json.loads((source/'development/receipts/index.json').read_text())
    assert args.run_id+'-new-event' in {e['event'] for e in index}
    assert args.run_id+'-workflow-099-summary' in {e['event'] for e in index}
    for name,digest in historical.items():assert sha256(source/'development/receipts'/name)==digest
    assert sha256(source/'development/environment-tested.json')==environment
    final_history=json.loads((source/'development/history.json').read_text())
    assert final_history['git_history']==retained['git_history']
    old_hashes={e['path']:e['sha256'] for s in retained['historical_stages'] for e in s['evidence']}
    for s in final_history['historical_stages']:
        for e in s['evidence']:
            if e['path'] in {'motion-preview-v01.mp4','papilio-final-1080p.mp4'}:
                assert e['sha256']==old_hashes[e['path']]
    loop_code='''import json,sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge')
    page=browser.new_page()
    page.goto(sys.argv[1])
    page.wait_for_function('document.querySelector("video")?.readyState>=2')
    page.locator('video').evaluate('v=>{window.wraps=0;let last=0;v.addEventListener("timeupdate",()=>{if(v.currentTime<last)window.wraps++;last=v.currentTime});v.muted=true;v.loop=true;return v.play()}')
    page.wait_for_function('window.wraps>=1',timeout=15000)
    observed=page.locator('video').evaluate('v=>({wraps:window.wraps,error:v.error?.message??null})')
    assert observed['wraps']>=1 and observed['error'] is None
    print(json.dumps(observed))
    browser.close()
'''
    loop=step('018-browser-loop-replay',[python,'-c',loop_code,
              (source/'.reliability-work'/(args.run_id+'-workflow')/'verification.mp4').as_uri()])
    loop_observation=json.loads(loop.stdout)
    for p in (source/'development/receipts').glob(args.run_id+'*.json'):
        if p.name in historical:continue  # Already retained; only collect newly executed steps.
        target=ROOT/'development/receipts'/p.name
        if target.exists():raise FileExistsError('Do not overwrite retained receipts: '+p.name)
        target.write_bytes(p.read_bytes())
    observation=json.loads((source/'development/journal-refresh.json').read_text())
    summary={'passed':True,'archive':args.archive.name,'archive_sha256':sha256(args.archive),
             'source_commit':manifest['source_commit'],'source_version':manifest['source_release'],
             'manifest_entries_checked':len(manifest['files']),'outside_any_git_checkout':True,
             'omitted_movies_remained_absent':True,'isolated_venv_declared_dependencies':True,
             'unit_tests_passed':unit_count,
             'browser_loop_replay':loop_observation,
             'journal_with_no_site_packages_or_external_tools':True,
             'journal_after_new_event_indexed':True,'historical_receipts_unchanged':len(historical),
             'historical_git_snapshot_preserved':True,'historical_media_hashes_retained_and_labelled':True,
             'historical_tested_environment_unchanged':True,'journal_observation':observation,
             'workflow':integration,'test_directory':str(work),
             'scope':'Windows, Blender 5.3, CPU, FFmpeg, Edge; new 2-second 12-frame verification clip; original film unchanged.'}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(clean(summary),indent=2)+'\n',encoding='utf-8')
    save(args.run_id+'-099-summary',summary)
    print('STANDALONE_VERIFIED '+json.dumps(clean(summary)),flush=True)


if __name__=='__main__':
    try:main()
    except Exception:
        import traceback
        if '--run-id' in sys.argv:
            event=sys.argv[sys.argv.index('--run-id')+1]+'-098-stopped'
            try:save(event,{'passed':False,'error':traceback.format_exc()})
            except FileExistsError:pass
        raise
