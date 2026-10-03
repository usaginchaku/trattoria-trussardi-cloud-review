# ART01 A2: per-frame candidate copies of FinishAtlas_FUR06.png (original untouched). Only the colour cells used by that frame are shifted
# (new = old - cell_mean + target, keeps the existing per-pixel variation). UV/mesh/normals unchanged; Root assigns each copy to one Left_Frame renderer only.
import json,hashlib,numpy as np
from PIL import Image
SRC='src9/assets/codex-source/coord10-art01-20261003/FinishAtlas_FUR06.png'
A=np.array(Image.open(SRC).convert('RGB')).astype(float); H,W=A.shape[:2]
CELL={'cream':(0,256,256,512),'blue':(256,256,512,512),'olive':(512,0,768,256),'pink':(768,0,1024,256)}  # x0,y0,x1,y1 (rows from top), 0.25 UV grid
PLAN={'22':{'blue':(226,221,198),'olive':(84,88,60)},          # mat blue->cream (ref cream mat), frame olive slightly darker
      '23':{'blue':(66,70,54),'cream':(200,214,214)},          # frame light-blue->dark green, inner rim cream->blue-grey
      '24':{'pink':(112,58,62)},                               # frame pink->deeper maroon
      '25':{'blue':(228,228,240),'olive':(84,88,60)}}          # mat blue->pale lavender-white, frame olive slightly darker
log={}
for n,plan in PLAN.items():
    B=A.copy(); ch={}
    for cell,tgt in plan.items():
        x0,y0,x1,y1=CELL[cell]; reg=B[y0:y1,x0:x1]; mean=reg.reshape(-1,3).mean(0)
        B[y0:y1,x0:x1]=np.clip(reg-mean+np.array(tgt,float),0,255); ch[cell]={'from_mean':[round(v,1) for v in mean],'to':list(tgt),'rect':[x0,y0,x1,y1]}
    out=f'c9/FinishAtlas_FUR06_A2_F{n}.png'; Image.fromarray(np.round(B).astype(np.uint8)).save(out,optimize=True)
    C=np.array(Image.open(out).convert('RGBA')); O=np.array(Image.open(SRC).convert('RGBA'))
    mask=np.ones((H,W),bool)
    for cell in plan: x0,y0,x1,y1=CELL[cell]; mask[y0:y1,x0:x1]=False
    log[f'Frame_{n}']={'texture':out.split('/')[-1],'cells':ch,'pixels_changed_outside_cells':int(((C!=O).any(-1)&mask).sum())}
json.dump(log,open('c9/art_A2_check.json','w'),indent=1); print(json.dumps(log)[:900])
