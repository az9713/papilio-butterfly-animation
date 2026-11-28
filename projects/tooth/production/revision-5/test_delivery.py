"""Test the actual exports, shared timing, song/stop/return, and offline player."""
from pathlib import Path
import datetime,hashlib,json,subprocess
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
from scipy.signal import butter,sosfilt,correlate,find_peaks

root=Path(__file__).resolve().parent
timeline=json.loads((root/'timeline.json').read_text())
names=['The Tooth - reclaimed.mp4']+[f'Pass-{i}.mp4' for i in (1,2,3)]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def audio(path):
    return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','1','-ar','16000','-f','f32le','-']),dtype='<f4')
def frame(number):
    cap=cv2.VideoCapture(str(root/names[0]))
    cap.set(cv2.CAP_PROP_POS_FRAMES,number)
    ok,im=cap.read();cap.release();assert ok
    return im
def segment(sound,start,end):return sound[round(start*16000):round(end*16000)]
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'outputs':{},'browser':{}}
bounds=timeline['pass_boundaries']
counts=[384]+[round((b-a)*24) for a,b in zip(bounds,bounds[1:])]
for name,count in zip(names,counts):
    path=root/name
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
    video,aud=probe['streams']
    assert (video['codec_name'],video['width'],video['height'],video['avg_frame_rate'],int(video['nb_frames']))==('h264',960,540,'24/1',count)
    assert (aud['codec_name'],aud['sample_rate'],aud['channels'])==('aac','48000',2)
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(path),'-f','null','-'],check=True)
    report['outputs'][name]={'sha256':digest(path),'frames':count,'bytes':path.stat().st_size,'duration':float(probe['format']['duration'])}
full=audio(root/names[0])
voice=audio(root/'voice.wav')
cues=json.loads((root/'audio-cues.json').read_text())
assert cues['dedicated_breath_events']==[]
checks=[]
v=timeline['voice']
for label,start,end in [('first',v['first_start'],v['first_start']+v['duration']),
                        ('attempt',v['attempt_start'],v['attempt_end']),
                        ('returned',v['return_start'],v['return_start']+v['duration'])]:
    # Include the metallic interruption in the full mix but check the voice
    # before it enters so the attempt is audible on its own.
    test_end=min(end,v['interruption_start']-.02) if label=='attempt' else end
    encoded=segment(full,start,test_end)
    stem=segment(voice,start,test_end)
    correlation=float(np.corrcoef(encoded,stem)[0,1])
    rms=float(np.sqrt(np.mean(encoded**2)))
    assert correlation>.96 and rms>.10
    checks.append({'event':label,'start_s':start,'end_s':end,'encoded_voice_correlation':correlation,'encoded_rms':rms})
stop=segment(voice,8.32,8.49)
assert max(abs(stop))==0
assert np.sqrt(np.mean(segment(full,8.32,8.49)**2))>.04
first=segment(full,3.60,4.60)
last=segment(full,14.10,15.10)
same_note_correlation=float(np.corrcoef(first,last)[0,1])
assert same_note_correlation>.99
pitch={}
for label,sound in [('first',first),('returned',last)]:
    values=[]
    for offset in np.arange(.0,.75,.1):
        y=segment(sound,offset,offset+.1)
        y=sosfilt(butter(4,650,fs=16000,output='sos'),y)
        ac=correlate(y,y,mode='full',method='fft')[len(y)-1:]
        peaks=find_peaks(ac)[0];peaks=peaks[(peaks>16000/500)&(peaks<16000/80)]
        lag=peaks[np.argmax(ac[peaks])]
        values.append(float(16000/lag))
    pitch[label]=float(np.median(values))
assert abs(pitch['first']-293.665)<10 and abs(pitch['returned']-pitch['first'])<2
report['song_stop_return']={'vocal_events':checks,'silent_voice_stem_after_interruption':True,
                           'metal_audible_after_voice_stops':True,'first_returned_correlation':same_note_correlation,
                           'median_pitch_hz':pitch,'dedicated_breath_events':[]}
line=audio(root/'customer-line.wav')
start=round(timeline['dialogue_start']*16000)
assert np.corrcoef(full[start:start+len(line)],line)[0,1]>.96

# A closed mouth follows the interrupted vocal, and the next singing pose
# visibly differs at the jaw. The visual review sheet exposes these frames.
mouth=np.s_[285:365,525:665]
opened=frame(195)
closed=frame(202)
mouth_difference=float(np.mean(abs(opened[mouth].astype(float)-closed[mouth].astype(float))))
assert mouth_difference>2
before,after=frame(251),frame(303)
def copper(im):
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    return (hsv[:,:,0]<15)&(hsv[:,:,1]>145)&(hsv[:,:,2]>180)
slot=np.s_[235:305,575:605]
assert copper(before)[slot].mean()>.9 and copper(after)[slot].mean()<.03
assert copper(after)[120:195,475:615].sum()>900
report['performance']={'interrupted_open_closed_jaw_pixel_difference':mouth_difference,
                       'copper_seated_before_extraction':True,'empty_slot_and_detached_tooth_after':True,
                       'audience_comprehension':'unverified by fresh human viewers'}

samples=[20,91,195,202,239,276,303,346,376]
sheet=Image.new('RGB',(1170,747),'#1e211d')
draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
for i,number in enumerate(samples):
    tile=Image.fromarray(cv2.cvtColor(frame(number),cv2.COLOR_BGR2RGB)).resize((390,219),Image.Resampling.LANCZOS)
    x,y=390*(i%3),249*(i//3)
    sheet.paste(tile,(x,y));draw.text((x+8,y+223),f'{number/24:.3f} s',font=font,fill='#f0d6b1')
sheet.save(root/'screening-frames.jpg',quality=94)

with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge')
    report['edge_version']=browser.version
    for width in (1100,390):
        page=browser.new_page(viewport={'width':width,'height':800})
        page.goto((root/'Screening.html').as_uri())
        results=[]
        for i,name in enumerate(names):
            page.get_by_role('button').nth(i).click()
            page.wait_for_function('document.querySelector("video").currentTime>.05')
            page.wait_for_function('document.querySelector("video").ended',timeout=30000)
            state=page.locator('video').evaluate('v=>({ended:v.ended,muted:v.muted,volume:v.volume,error:v.error?.message??null,duration:v.duration,frames:v.getVideoPlaybackQuality().totalVideoFrames})')
            assert state['ended'] and not state['muted'] and state['volume']>0 and state['error'] is None
            assert page.locator('video').bounding_box()['width']<=width
            results.append({'file':name,**state})
        report['browser'][str(width)]=results
        page.close()
    browser.close()
report['offline_player_sha256']=digest(root/'Screening.html')
(root/'end-to-end.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('PASS: decoded song, interrupted vocal, matching returned D, jaw change, removal and eight full playback runs.')
