"""Encode and inspect a completed film from its frame sequence and audio mix."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess
import cv2,numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]

def finish(path,encode=True):
    cfg=json.loads((path/'source/timeline.json').read_text(encoding='utf8'));frames=sorted((path/'frames').glob('frame_*.png'))
    assert len(frames)==cfg['duration']*cfg['fps'],(path.name,len(frames))
    command=['ffmpeg','-y','-v','error','-framerate',str(cfg['fps']),'-i',str(path/'frames/frame_%04d.png'),
             '-i',str(path/'audio/mix.wav'),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p',
             '-c:a','aac','-b:a','192k','-t',str(cfg['duration']),'-movflags','+faststart',str(path/'film.mp4')]
    if encode:subprocess.run(command,check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(path/'film.mp4'),'-f','null','-'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path/'film.mp4')]))
    video=next(s for s in probe['streams'] if s['codec_type']=='video');audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert video['width']==1280 and video['height']==720 and video['r_frame_rate']=='24/1' and int(video['nb_frames'])==336
    assert abs(float(probe['format']['duration'])-14)<.08
    pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(path/'film.mp4'),'-vn','-ar','48000','-ac','2','-f','f32le','-'])
    wave=np.frombuffer(pcm,'<f4');assert np.sqrt(np.mean(wave**2))>.005 and np.max(abs(wave))<1
    moments=[1,49,97,145,193,241,289,336];sheet=Image.new('RGB',(1280,760),'#141b20');draw=ImageDraw.Draw(sheet)
    capture=cv2.VideoCapture(str(path/'film.mp4'));decoded=[]
    for i,f in enumerate(moments):
        capture.set(cv2.CAP_PROP_POS_FRAMES,f-1);ok,frame=capture.read();assert ok,(path.name,f)
        decoded.append(Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)))
        im=decoded[-1].resize((320,180))
        sheet.paste(im,((i%4)*320,(i//4)*380//2));draw.text(((i%4)*320+8,(i//4)*190+163),f'{(f-1)/24:.2f} s',fill='white')
    # Keep the contact sheet compact rather than padding unused rows.
    sheet.crop((0,0,1280,380)).save(path/'screening-frames.jpg',quality=92)
    capture.set(cv2.CAP_PROP_POS_FRAMES,240);ok,poster=capture.read();assert ok;capture.release()
    Image.fromarray(cv2.cvtColor(poster,cv2.COLOR_BGR2RGB)).save(path/'poster.jpg',quality=94)
    sample=[np.asarray(im.resize((160,90)),dtype=float) for im in decoded]
    changes=[float(np.mean(abs(a-b))) for a,b in zip(sample,sample[1:])]
    assert max(changes)>2,'Film lacks visible motion'
    receipt={'passed':True,'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'concept_id':cfg['concept_id'],
             'film_sha256':hashlib.sha256((path/'film.mp4').read_bytes()).hexdigest(),'duration':probe['format']['duration'],
             'frames':int(video['nb_frames']),'resolution':[video['width'],video['height']],'fps':video['r_frame_rate'],
             'audio_codec':audio['codec_name'],'audio_sample_rate':audio['sample_rate'],'audio_channels':audio['channels'],
             'audio_rms':float(np.sqrt(np.mean(wave**2))),'audio_peak':float(np.max(abs(wave))),
             'sampled_frame_mean_changes':changes,'complete_decode':True,'encode_command':command[1:-1],
             'scope':'File integrity, frame sequence, motion and non-silent audio. Story comprehension and artistic merit need separate evidence.'}
    # Store reproducible relative command arguments instead of local account paths.
    receipt['encode_command']=['-framerate','24','-i','frames/frame_%04d.png','-i','audio/mix.wav','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t','14','-movflags','+faststart','film.mp4']
    (path/'receipts/encoded-film.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print('ENCODED_FILM_OK',cfg['concept_id'],flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('slug');parser.add_argument('--inspect-only',action='store_true');args=parser.parse_args();finish(ROOT/'projects'/args.slug,encode=not args.inspect_only)
