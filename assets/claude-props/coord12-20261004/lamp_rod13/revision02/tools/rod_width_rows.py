# row profiles of dark runs (mean RGB < 95) in the lamp arm/plate region of the private attachments (scratch only) and of the model-only
# front preview of LAMP11 r2 downscaled so that its cup is 62 px wide. Prints numbers only; no pixels are written.
# usage: python rod_width_rows.py att1.jpg att2.jpg model_front.png out.json
import sys,json
import numpy as np
from PIL import Image
a1,a2,mf,out=sys.argv[1:5]
def runs(row,thr=95):
    xs=np.where(row<thr)[0]
    if not len(xs): return []
    rr=np.split(xs,np.where(np.diff(xs)>1)[0]+1); return [[int(r[0]),int(r[-1]),len(r)] for r in rr if len(r)>=2]
A=np.asarray(Image.open(a1).convert('RGB')).astype(int); B=np.asarray(Image.open(a2).convert('RGB')).astype(int)
res={'threshold_mean_rgb':95,'regions':{}}
for name,im,(x0,x1,y0,y1) in [('IMG_3594_left',A,(710,790,360,425)),('IMG_3594_right',A,(1278,1355,360,425)),('IMG_3675_left_of_shelf',B,(375,452,420,480))]:
    lum=im[y0:y1,x0:x1].mean(2); res['regions'][name]=[[r+y0,[[s+x0,e+x0,w] for s,e,w in runs(lum[r])]] for r in range(0,y1-y0,2)]
im=Image.open(mf).convert('RGB'); a=np.asarray(im).astype(int); cream=(a[:,:,1]>150)&(a[:,:,2]<a[:,:,1]-25); rows=np.where(cream.any(1))[0]
ws=max(np.where(cream[r])[0].ptp()+1 for r in rows); sc=62/ws; b=np.asarray(im.resize((round(im.width*sc),round(im.height*sc)),Image.LANCZOS)).astype(int)
cr=(b[:,:,1]>150)&(b[:,:,2]<b[:,:,1]-25); bot=int(np.where(cr.any(1))[0].max()); lum=b.mean(2)
res['model_front_scaled_cup62']=[[r-bot,runs(lum[r])] for r in range(bot-2,bot+26)]
json.dump(res,open(out,'w'),indent=1); print('ok')
