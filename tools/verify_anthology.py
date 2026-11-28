"""Verify the final ten-film publication and its existing-project preservation."""
from pathlib import Path
import hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    plans=json.loads((ROOT/'production/anthology/selection.json').read_text(encoding='utf8'))
    assert len(plans)==10 and {p['concept_id'] for p in plans}=={1,3,4,7,9,15,19,25,28,30}
    records=[]
    for p in plans:
        path=ROOT/'projects'/p['slug'];digest=sha(path/'film.mp4')
        encoded=json.loads((path/'receipts/encoded-film.json').read_text(encoding='utf8'))
        browser=json.loads((path/'receipts/browser-playback.json').read_text(encoding='utf8'))
        package=json.loads((path/'receipts/source-package.json').read_text(encoding='utf8'))
        test=json.loads((path/'receipts/source-package-test.json').read_text(encoding='utf8'))
        scene=json.loads((path/'receipts/scene.json').read_text(encoding='utf8'))
        assert encoded['passed'] and encoded['film_sha256']==digest and encoded['audio_sample_rate']=='48000'
        assert encoded['frames']==336 and encoded['fps']=='24/1' and encoded['resolution']==[1280,720]
        assert browser['passed'] and browser['ended'] and browser['muted'] is False and browser['current_time']==14 and browser['film_sha256']==digest
        archive=path/package['archive'];assert sha(archive)==package['sha256']==test['archive_sha256'] and test['passed']
        assert test['outside_git'] and test['retained_audio_mix_byte_identical'] and test['geometry_and_sampled_motion_identical']
        assert test['rebuilt_hero_frame_mean_pixel_difference_from_encoded']<2.5
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None and set(z.namelist())==set(package['members'])
            for name,expected in package['members'].items():
                assert hashlib.sha256(z.read(name)).hexdigest()==expected and sha(path/name)==expected,(p['slug'],name)
        assert scene['svg_sha256']==sha(path/'source/design.svg') and scene['timeline_sha256']==sha(path/'source/timeline.json')
        assert scene['scene_sha256']==sha(path/'source/scene.blend') and scene['svg_roles']
        for name in ['README.md','assessment.md','index.html','player.html','poster.jpg','screening-frames.jpg']:
            assert (path/name).is_file()
        for kind in ['music','sfx']:
            generation=json.loads((path/'receipts'/f'elevenlabs-{kind}.json').read_text(encoding='utf8'))
            assert generation['status']==200 and generation['sha256']==sha(path/'audio'/f'{kind}.mp3')
        records.append({'concept_id':p['concept_id'],'slug':p['slug'],'film_sha256':digest,'source_zip_sha256':package['sha256'],
                        'source_members':len(package['members']),'duration_seconds':14,'browser_completed_unmuted':True,
                        'source_rebuilt_outside_git':True,'rebuilt_hero_mean_pixel_difference':test['rebuilt_hero_frame_mean_pixel_difference_from_encoded']})
    assert sha(ROOT/'projects/tooth/film.mp4')=='f74fbace55b2df53256e07a3df4cfed3fc81dc5d191efca2aa7bda8e69b17b74'
    assert sha(ROOT/'projects/butterfly/papilio-final-1080p.mp4')=='586d7e0c9d8fd5af8d8d39aa4a89d01f0b4bfab4ab9b717d4d3d14d65ed9b465'
    record={'passed':True,'films':records,'new_film_count':10,'total_new_film_seconds':140,'existing_films_unchanged':True,
            'readmes':12,'scope':'Delivery and extracted-source evidence. First-time audience understanding and artistic excellence are not inferred from these checks.'}
    (ROOT/'publication/anthology-verification.json').write_bytes((json.dumps(record,indent=2)+'\n').encode('utf8'))
    print('ANTHOLOGY_VERIFIED',len(records),'films, 140 seconds, ten extracted-source tests, existing movies unchanged.')

if __name__=='__main__':main()
