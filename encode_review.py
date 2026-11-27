"""Encode a complete selected-scene sequence using its render manifest."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess
from pipeline_common import png_size,sha256,path_label,receipt,receipt_path,write_json


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frames',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--browser-check',action='store_true')
    parser.add_argument('--browser-channel',default='msedge')
    args=parser.parse_args(argv)
    folder=args.frames.resolve();movie=args.output.resolve()
    if movie.exists():raise FileExistsError('Preserve existing movie: '+str(movie))
    manifest=folder/'render-manifest.json'
    if not manifest.is_file():raise ValueError('A render-manifest.json from render_saved.py is required')
    spec=json.loads(manifest.read_text())
    first,last=spec['frame_range'];count=last-first+1;fps=spec['fps']
    expected=[folder/f'frame_{frame:04d}.png' for frame in range(first,last+1)]
    if {p.name for p in folder.glob('frame_*.png')}!={p.name for p in expected}:
        raise ValueError('The frame sequence must exactly cover the selected scene range')
    for path in expected:
        if png_size(path)!=spec['resolution']:raise ValueError('Frame dimensions differ from render manifest')
    if any(value%2 for value in spec['resolution']):raise ValueError('H.264 yuv420p needs even dimensions')
    ffmpeg,ffprobe=shutil.which('ffmpeg'),shutil.which('ffprobe')
    if not ffmpeg or not ffprobe:raise RuntimeError('FFmpeg and ffprobe must be on PATH')
    movie.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run([ffmpeg,'-v','error','-n','-framerate',str(fps),'-start_number',str(first),
                    '-i',str(folder/'frame_%04d.png'),'-frames:v',str(count),'-c:v','libx264',
                    '-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],
                   check=True,capture_output=True,text=True)
    subprocess.run([ffmpeg,'-v','error','-i',str(movie),'-f','null','-'],check=True,capture_output=True,text=True)
    result=subprocess.run([ffprobe,'-v','error','-count_frames','-select_streams','v:0',
                           '-show_entries','stream=codec_name,width,height,r_frame_rate,nb_read_frames:format=duration',
                           '-of','json',str(movie)],check=True,capture_output=True,text=True)
    metadata=json.loads(result.stdout);stream=metadata['streams'][0]
    if (int(stream['nb_read_frames'])!=count or
        abs(float(Fraction(stream['r_frame_rate']))-fps)>1e-6 or
        [stream['width'],stream['height']]!=spec['resolution'] or
        abs(float(metadata['format']['duration'])-count/fps)>.01):
        raise RuntimeError('Encoded movie metadata differs from selected scene')
    playback={'status':'not_requested'}
    if args.browser_check:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            options={'channel':args.browser_channel} if args.browser_channel!='chromium' else {}
            browser=pw.chromium.launch(**options)
            page=browser.new_page()
            page.goto(movie.as_uri());page.wait_for_function('document.querySelector("video")?.readyState>=2')
            page.locator('video').evaluate('v=>{v.muted=true;v.loop=false;return v.play()}')
            page.wait_for_function('document.querySelector("video").ended',timeout=int((count/fps+15)*1000))
            playback=page.locator('video').evaluate('v=>({ended:v.ended,time:v.currentTime,error:v.error?.message??null})')
            if not playback['ended'] or playback['error']:raise RuntimeError('Browser playback failed')
            browser.close()
    report=receipt('encode',movie=path_label(movie),movie_sha256=sha256(movie),
                   bytes=movie.stat().st_size,render_manifest_sha256=sha256(manifest),
                   source_scene_sha256=spec['scene_sha256'],source_revision=spec['revision'],
                   metadata=metadata,all_pngs_verified=True,decode_passed=True,browser_playback=playback,passed=True)
    write_json(receipt_path(movie.parent/'receipts','encode'),report)
    print('PAPILIO_ENCODE_COMPLETE '+json.dumps(report),flush=True)
    return report


if __name__=='__main__':main()
