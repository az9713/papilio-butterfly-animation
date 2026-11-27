"""Encode a completed 288 frame stage, inspect the result, and exercise actual playback."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageStat,ImageChops
from playwright.sync_api import sync_playwright

root=Path(__file__).parent
p=argparse.ArgumentParser();p.add_argument('frames',type=Path);p.add_argument('output');p.add_argument('--bitrate');args=p.parse_args()
files=sorted(args.frames.glob('frame_*.png'))
assert len(files)==288, f'Expected 288 frames, found {len(files)}'
size=None
for i,path in enumerate(files,1):
 assert path.name==f'frame_{i:04d}.png'
 with Image.open(path) as im:
  if size is None:size=im.size
  assert im.size==size
  im.verify()
movie=root/args.output
if movie.exists():raise RuntimeError('Preserve existing movie '+str(movie))
command=[shutil.which('ffmpeg'),'-v','error','-framerate','24','-start_number','1','-i',str(args.frames/'frame_%04d.png'),'-frames:v','288','-c:v','libx264','-preset','slow']
command+=['-b:v',args.bitrate,'-maxrate',args.bitrate,'-bufsize','10M'] if args.bitrate else ['-crf','18']
command+=['-pix_fmt','yuv420p','-movflags','+faststart',str(movie)]
subprocess.run(command,capture_output=True,text=True,check=True)
subprocess.run([shutil.which('ffmpeg'),'-v','error','-i',str(movie),'-f','null','-'],capture_output=True,text=True,check=True)
probe=subprocess.run([shutil.which('ffprobe'),'-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_read_frames,duration:format=duration','-of','json',str(movie)],capture_output=True,text=True,check=True)
metadata=json.loads(probe.stdout);stream=metadata['streams'][0]
assert stream['r_frame_rate']=='24/1' and int(stream['nb_read_frames'])==288
assert abs(float(metadata['format']['duration'])-12)<.005
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
sheet=Image.new('RGB',(480*4,270*3+35*3),(16,20,24));draw=ImageDraw.Draw(sheet)
for slot,index in enumerate([0,12,36,60,84,108,144,168,204,228,252,276]):
 with Image.open(files[index]) as im:sheet.paste(im.convert('RGB').resize((480,270)),((slot%4)*480,(slot//4)*305+35))
 draw.text(((slot%4)*480+12,(slot//4)*305+5),f'{index/24:.1f} s  |  frame {index+1:03d}',font=font,fill=(227,231,234))
contact=root/(movie.stem+'-contact.jpg');sheet.save(contact,quality=94)
boundary=Image.new('RGB',(480*4,305),(16,20,24));d=ImageDraw.Draw(boundary)
for slot,index in enumerate([286,287,0,1]):
 with Image.open(files[index]) as im:boundary.paste(im.convert('RGB').resize((480,270)),(slot*480,35))
 d.text((slot*480+12,5),f'frame {index+1:03d}',font=font,fill=(227,231,234))
boundary.save(root/(movie.stem+'-boundary.jpg'),quality=94)
html=root/(movie.stem+'-player.html')
html.write_text('<!doctype html><html><body style="margin:0;background:#101418;color:#eee;font-family:Arial"><video id="film" controls muted playsinline style="width:100%;max-width:1280px" src="'+movie.name+'"></video></body></html>',encoding='utf-8')
with sync_playwright() as pw:
 browser=pw.chromium.launch(channel='msedge')
 page=browser.new_page(viewport={'width':1280,'height':760})
 page.goto(html.as_uri());page.wait_for_function('document.querySelector("video").readyState>=2')
 page.locator('video').evaluate('v=>v.play()')
 page.wait_for_function('document.querySelector("video").ended',timeout=25000)
 playback=page.locator('video').evaluate('v=>({ended:v.ended,currentTime:v.currentTime,width:v.videoWidth,height:v.videoHeight,error:v.error?.message??null})')
 assert playback['ended'] and playback['error'] is None
 # Exercise replay across the seam twice in the encoded player.
 page.locator('video').evaluate('v=>{v.loop=true;v.currentTime=11.5;v.play();}')
 page.wait_for_function('document.querySelector("video").currentTime<1',timeout=5000)
 replay1=page.locator('video').evaluate('v=>v.currentTime')
 page.locator('video').evaluate('v=>{v.currentTime=11.5;v.play();}')
 page.wait_for_function('document.querySelector("video").currentTime<1',timeout=5000)
 replay2=page.locator('video').evaluate('v=>v.currentTime')
 page.locator('video').evaluate('v=>{v.pause();v.currentTime=0;}')
 page.wait_for_function('!document.querySelector("video").seeking')
 page.screenshot(path=str(root/(movie.stem+'-playback.png')))
 browser.close()
diffs=[]
for j in [0,1,71,143,215,286]:
 with Image.open(files[j]) as a,Image.open(files[j+1]) as b:
  diffs.append({'between':[j+1,j+2],'mean_rgb_difference':sum(ImageStat.Stat(ImageChops.difference(a.convert('RGB'),b.convert('RGB'))).mean)/3})
with Image.open(files[-1]) as last,Image.open(files[0]) as first:
 seam_difference=sum(ImageStat.Stat(ImageChops.difference(last.convert('RGB'),first.convert('RGB'))).mean)/3
neighbor_difference=(diffs[0]['mean_rgb_difference']+diffs[-1]['mean_rgb_difference'])/2
report={'movie':str(movie),'bytes':movie.stat().st_size,'metadata':metadata,'all_pngs_verified':True,'decode_passed':True,'browser_playback':playback,'loop_replays':[replay1,replay2],'sampled_frame_differences':diffs,'source_frame_seam_mean_difference':seam_difference,'seam_to_neighbor_difference_ratio':seam_difference/neighbor_difference,'contact_sheet':str(contact),'note':'Encoded playback and sample/contact-sheet review are separate checks; no audio was requested.'}
(root/(movie.stem+'-review.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report),flush=True)
