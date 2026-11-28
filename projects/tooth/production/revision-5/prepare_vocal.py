from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt,correlate,find_peaks

root=Path(__file__).resolve().parent
subprocess.run(['ffmpeg','-v','error','-y','-i',str(root/'vocal-original.mp3'),'-ar','48000','-ac','1',str(root/'vocal-raw.wav')],check=True)
sr,x=wavfile.read(root/'vocal-raw.wav')
x=x.astype(float)/32768
def pitches(wave):
    values=[]
    for start in np.arange(.2,len(wave)/sr-.15,.1):
        y=sosfilt(butter(4,700,fs=sr,output='sos'),wave[round(start*sr):round((start+.1)*sr)])
        co=correlate(y,y,mode='full',method='fft')[len(y)-1:]
        peaks=find_peaks(co)[0];peaks=peaks[(peaks>sr/400)&(peaks<sr/90)]
        values.append(float(sr/peaks[np.argmax(co[peaks])]))
    return values
original_pitch=float(np.median(pitches(x[round(.25*sr):round(1.65*sr)])))
factor=293.664768/original_pitch
filters=f'atrim=start=0.25:end=1.65,asetpts=PTS-STARTPTS,rubberband=tempo=1.1666667:pitch={factor}:formant=preserved'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(root/'vocal-original.mp3'),'-af',filters,'-ar','48000','-ac','1',str(root/'vocal-D.wav')],check=True)
sr,x=wavfile.read(root/'vocal-D.wav');x=x.astype(float)/32768
x=np.pad(x,(0,max(0,57600-len(x))))[:57600]
x*=min(.25/(np.sqrt(np.mean(x*x))+1e-9),.73/(max(abs(x))+1e-9))
fade=round(sr*.035);x[:fade]*=np.linspace(0,1,fade);x[-fade:]*=np.linspace(1,0,fade)
wavfile.write(root/'vocal-D.wav',sr,(x*32767).astype(np.int16))
report={'source_median_hz':original_pitch,'pitch_factor':factor,'prepared_median_hz':float(np.median(pitches(x))),
        'duration_s':1.2,'filters':filters,'sha256':hashlib.sha256((root/'vocal-D.wav').read_bytes()).hexdigest()}
(root/'vocal-preparation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
