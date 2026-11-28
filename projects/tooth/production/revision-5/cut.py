"""Assemble the corrected 24 fps screening from the registered Blender and puppet plates."""
from pathlib import Path
import json
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parent
base = root.parent
sys.path.insert(0, str(base))
from edit import points, raw

W, H = 960, 540
size = (W, H)
bench = cv2.resize(cv2.imread(str(root/'bench.png')), size, interpolation=cv2.INTER_AREA)
empty = cv2.imread(str(root/'empty.png'))
part = cv2.imread(str(root/'tooth.png'), cv2.IMREAD_UNCHANGED)
glove = cv2.imread(str(root/'hand.png'), cv2.IMREAD_UNCHANGED)
grip = np.array(json.loads((root/'registration.json').read_text())['grip_pixel'])
hand_scale = .48
glove = cv2.resize(glove, None, fx=hand_scale, fy=hand_scale, interpolation=cv2.INTER_AREA)
tip = np.array([1507,627])*hand_scale
reaction = cv2.resize(cv2.imread(str(root/'reaction.png')), size)
from scipy.io.wavfile import read
speech_rate, speech = read(root/'customer-line.wav')
timeline=json.loads((root/'timeline.json').read_text())
subtitle_font = ImageFont.truetype('C:/Windows/Fonts/georgia.ttf', 30)
font = ImageFont.truetype('C:/Windows/Fonts/georgiab.ttf', 25)
turn = cv2.VideoCapture(str(root/'turning.mp4'))
turning = []
while True:
    ok, frame = turn.read()
    if not ok: break
    turning.append(frame)
turn.release()

def ease(x):
    x = np.clip(x,0,1)
    return x*x*(3-2*x)

def composite(background, sprite, transform, opacity=1):
    layer=cv2.warpAffine(sprite, transform, size, flags=cv2.INTER_LINEAR)
    alpha=layer[:,:,3:4].astype(np.float32)*(opacity/255)
    return (background*(1-alpha)+layer[:,:,:3]*alpha).astype(np.uint8)

def pair(t, length, labelled):
    scale=1+.026*ease(t/length)
    m=cv2.getRotationMatrix2D((480,268),0,scale)
    im=cv2.warpAffine(bench,m,size,flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    if labelled:
        canvas=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
        d=ImageDraw.Draw(canvas)
        for x,label in [(24,'The repairer'),(766,'The customer')]:
            bb=d.textbbox((x,485),label,font=font)
            d.rounded_rectangle((bb[0]-12,bb[1]-5,bb[2]+12,bb[3]+7),radius=6,fill='#29231e')
            d.text((x,485), label, font=font,fill='#f2ddbc')
        im=cv2.cvtColor(np.asarray(canvas),cv2.COLOR_RGB2BGR)
    return im

def workbench(t,removal):
    # A fixed camera preserves the identity of the slot. Positive lift moves the
    # copper part toward screen left and rotates its far end into clear view.
    if removal:
        approach=ease((t-.25)/.50)
        lift=ease((t-.95)/1.02)
        detached=0
    else:
        approach=1
        lift=1-ease((t-.47)/1.02)
        detached=ease((t-1.75)/.57)
    travel=np.array([-162*lift, -110*lift + 32*np.sin(np.pi*lift)])
    m=cv2.getRotationMatrix2D(tuple(grip),-67*lift,1+.06*lift)
    m[:,2]+=travel
    im=composite(empty,part,m)
    off=(1-approach)+detached
    edge=m @ np.array([grip[0]-24,grip[1],1])
    hand_position=edge-tip+np.array([-665*off,-45*off])
    hm=np.float32([[1,0,hand_position[0]],[0,1,hand_position[1]]])
    return composite(im,glove,hm)

def window(t,start,end,ramp=.06):
    return ease((t-start)/ramp)*(1-ease((t-end)/ramp))

def actor(t):
    v=timeline['voice']
    first=window(t,v['first_start']-.04,v['first_start']+v['duration']-.03)
    attempt=window(t,v['attempt_start']-.04,v['attempt_end']-.01,.04)
    returned=window(t,v['return_start']-.04,v['return_start']+v['duration']-.03)
    prepare=.24*window(t,7.78,8.00,.12)
    opening=.72*max(first,attempt,returned)+prepare
    line_time=t-timeline['dialogue_start']
    if 0<=line_time<len(speech)/speech_rate:
        segment=speech[round(line_time*speech_rate):round((line_time+.04)*speech_rate)].astype(float)/32768
        opening=max(opening,min(.72,.18+float(np.sqrt(np.mean(segment**2)))*7))
    disappointed=ease((t-8.31)/.23)*(1-ease((t-13.82)/.15))
    recovery=ease((t-13.9)/.35)
    sx,sy=W/1672,H/941
    im=cv2.resize(raw,size,interpolation=cv2.INTER_AREA)
    if opening>.001:
        mask=np.zeros((H,W),np.uint8)
        poly=np.round(points*np.array([sx,sy])).astype('int32')
        cv2.fillPoly(mask,[poly],255,lineType=cv2.LINE_AA)
        transform=cv2.getRotationMatrix2D((1208*sx,437*sy),7*opening,1)
        shifted=cv2.warpAffine(im,transform,size,flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
        alpha=cv2.warpAffine(mask,transform,size)[:,:,None]/255
        cavity=np.zeros_like(mask)
        lips=np.array([[972,532],[1068,496],[1138,508],[1163,493],[1155,526],[1048,544],[979,555]])
        cv2.fillPoly(cavity,[np.round(lips*np.array([sx,sy])).astype('int32')],255)
        a=cv2.GaussianBlur(cavity,(3,3),.55)[:,:,None]/255
        background=im*(1-a)+np.array([22,26,40])*a
        im=np.uint8(np.clip(background*(1-alpha)+shifted*alpha,0,255))
    head=cv2.getRotationMatrix2D((W*.70,H*.91),1.45*disappointed-.6*recovery,1.04)
    head[1,2]+=6*disappointed-2*recovery
    im=cv2.warpAffine(im,head,size,flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    if timeline['dialogue_start']<=t<timeline['dialogue_start']+len(speech)/speech_rate:
        canvas=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
        draw=ImageDraw.Draw(canvas)
        text='That was my part.'
        box=draw.textbbox((0,0),text,font=subtitle_font)
        x=(W-box[2]+box[0])/2
        draw.rounded_rectangle((x-15,470,W-x+15,521),8,fill='#22201e')
        draw.text((x,477),text,font=subtitle_font,fill='#f5e6cb')
        im=cv2.cvtColor(np.array(canvas),cv2.COLOR_RGB2BGR)
    return im

def frame(number):
    t=number/timeline['fps']
    shot=next(s for s in timeline['shots'] if round(s['start']*24)<=number<round(s['end']*24))
    local=t-shot['start']
    name=shot['name']
    if name=='bench': return pair(local,shot['end']-shot['start'],True)
    if name=='empty mechanism':return turning[min(len(turning)-1,round(local*24))]
    if name=='insert':return workbench(local*1.5,False)
    if name=='remove':return workbench(local*1.2,True)
    if name=='recognition':
        transform=cv2.getRotationMatrix2D((W*.30,H*.42),0,1.04+.02*local)
        return cv2.warpAffine(reaction,transform,size,borderMode=cv2.BORDER_REPLICATE)
    return actor(t)

def build():
    master=root/'The Tooth - reclaimed.mp4'
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','bgr24','-video_size','960x540','-framerate',str(timeline['fps']),'-i','pipe:0','-i',str(root/'mix.wav'),'-c:v','libx264','-threads','4','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(master)]
    enc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for number in range(round(timeline['duration']*timeline['fps'])):
        enc.stdin.write(frame(number).tobytes())
    enc.stdin.close()
    if enc.wait():raise RuntimeError('master encode failed')
    bounds=timeline['pass_boundaries']
    for i in range(3):
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(master),'-ss',str(bounds[i]),'-t',str(bounds[i+1]-bounds[i]),'-c:v','libx264','-threads','4','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(root/f'Pass-{i+1}.mp4')],check=True)

if __name__=='__main__':
    build()
