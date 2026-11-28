from pathlib import Path
import cv2,numpy as np,subprocess,math
R=Path(__file__).resolve().parent
W,H=960,540;fps=24
raw=cv2.imread(str(R/'customer.png'));hh,ww=raw.shape[:2]
# The portrait's carved jaw is a separate hinged shape, pivoting at its brass ear rivet.
points=np.array([[976,532],[990,531],[1019,520],[1050,507],[1066,501],[1087,511],[1111,518],[1138,514],[1162,503],[1174,484],[1182,458],[1187,441],[1209,436],[1228,449],[1228,483],[1220,520],[1194,551],[1165,578],[1130,603],[1095,626],[1066,638],[1042,637],[1020,626],[1008,603],[1000,580],[989,558],[973,550]],float)
def ease(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def ease_window(t,start,up,end,down):return ease((t-start)/up)*(1-ease((t-end)/down))
def portrait(t,p):
 local=t-5*p
 if p==0:opening=1.0*ease_window(local,4.30,.16,4.79,.17);inhale=ease_window(local,3.86,.39,4.4,.51)
 elif p==1:opening=.29*ease_window(local,4.13,.18,4.37,.14);inhale=ease_window(local,3.88,.44,4.39,.18)
 else:opening=.5*ease((local-3.84)/.53);inhale=ease((local-3.72)/.68)
 # Scale to output resolution first. Work in the material coordinates of the original plate.
 base=cv2.resize(raw,(W,H),interpolation=cv2.INTER_AREA)
 sx=W/1672;sy=H/941;poly=np.round(points*np.array([sx,sy])).astype('int32')
 mask=np.zeros((H,W),np.uint8);cv2.fillPoly(mask,[poly],255,lineType=cv2.LINE_AA)
 zoom=[1.01,1.055,1.102][p]+.011*(local-3)
 ang=3.3*opening
 if ang>.001:
  M=cv2.getRotationMatrix2D((1208*sx,437*sy),ang,1)
  lifted=cv2.warpAffine(base,M,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
  alpha=cv2.warpAffine(mask,M,(W,H),flags=cv2.INTER_LINEAR)[:,:,None]/255
  original=base.astype(float)
  lip=np.zeros_like(mask)
  cv2.fillPoly(lip,[np.round(np.array([[972,532],[1068,496],[1138,508],[1163,493],[1155,526],[1048,544],[979,555]])*np.array([sx,sy])).astype('int32')],255)
  a=cv2.GaussianBlur(lip,(3,3),.55)[:,:,None]/255
  original=original*(1-a)+np.array([22,26,40])*a
  base=np.uint8(np.clip(original*(1-alpha)+lifted*alpha,0,255))
 M=cv2.getRotationMatrix2D((W*.66,H*.66),-.32*inhale,zoom);M[1,2]-=2.7*inhale
 return cv2.warpAffine(base,M,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
def main():
 cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','bgr24','-video_size','960x540','-framerate','24','-i','-','-i',str(R/'mix.wav'),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(R/'The Tooth That Didn’t Sing.mp4')]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for j in range(344):
  t=j/24;rep=int(t//5);local=t%5
  if local<3:
   k=j//2+1
   path=R/'mechanism-frames'/f'{k:03}.jpg'
   im=cv2.imread(str(path))
   if im is None:raise RuntimeError(f'missing frame {k}')
   z=[1.01,1.11,1.18][rep]+.016*local/3
   M=cv2.getRotationMatrix2D((W*.36,H*.53),0,z)
   im=cv2.warpAffine(im,M,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
  else:im=portrait(t,rep)
  p.stdin.write(im.tobytes())
 p.stdin.close()
 if p.wait():raise RuntimeError('mux failed')
 for n,start,end in [(1,0,5),(2,5,10),(3,10,344/24)]:
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(R/'The Tooth That Didn’t Sing.mp4'),'-ss',str(start),'-t',str(end-start),'-c:v','libx264','-crf','18','-c:a','aac','-b:a','192k','-movflags','+faststart',str(R/f'Pass-{n}.mp4')],check=True)


if __name__=='__main__':main()
