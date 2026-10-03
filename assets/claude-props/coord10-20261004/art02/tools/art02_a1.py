# ART02 A1: self-authored motif for LAY03_UpperFrame_1 (tile 3) only. Frames 2 and 3 are left as the input placeholders
# (motif not readable enough in IMG_3638/3669). Procedural flat shapes, no reference pixels used, no moire/occluder copied.
# The motif is drawn at the painting face's true aspect, resampled into the exact UV0 box, and the strip between UV box and
# editablePixelRectExclusive is filled by edge extension. All pixels outside the edited rect are copied unchanged.
import json,hashlib,numpy as np,sys
from PIL import Image,ImageDraw,ImageFilter
R='src2/assets/codex-source/coord10-art02-input-20261004/'
SRC=R+'PaintingAtlas_FUR06.png'; OUTP=sys.argv[1] if len(sys.argv)>1 else 'art2/PaintingAtlas_FUR06_ART02_A1.png'
scope=json.load(open(R+'frame_scope.json')); fr=json.load(open('art2/upper_frames.json'))
SS=4
def canvas(aspect,H=900):
    W=int(H*aspect); im=Image.new('RGB',(W*SS,H*SS),(0,0,0)); return im,ImageDraw.Draw(im),W*SS,H*SS
def P(d,pts,col,W,H): d.polygon([(x*W,y*H) for x,y in pts],fill=col)
def finish(im):
    im=im.filter(ImageFilter.GaussianBlur(SS*1.6)); return im.resize((im.width//SS,im.height//SS),Image.LANCZOS)
def m_u1(a):
    # observed (IMG_3638, rectified picture coords u right / v down): white band at top (v 0-0.10), blue field upper-left,
    # white diagonal streak from left v0.75-0.83 to right v0.28-0.39, red/pink field lower-right. Knife hides u0.35-0.65 v0.75-1 (inferred red).
    im,d,W,H=canvas(a)
    white=(240,239,230); blue=(66,118,185); blue2=(84,134,196); red=(192,88,98); red2=(176,78,90)
    d.rectangle([0,0,W,H],fill=white)
    P(d,[(0,0.10),(1,0.10),(1,0.28),(0,0.75)],blue,W,H)
    P(d,[(0,0.10),(1,0.10),(1,0.16),(0,0.30)],blue2,W,H)          # slightly lighter upper blue (flat anime tone step)
    P(d,[(0,0.83),(1,0.39),(1,1),(0,1)],red,W,H)
    P(d,[(0.25,1.0),(1,0.62),(1,1)],red2,W,H)                       # slightly darker lower-right red
    return finish(im)
MOT={'LAY03_UpperFrame_1':m_u1}
A=np.array(Image.open(SRC).convert('RGBA')); OUT=A.copy(); log=[]
for f in scope['frames']:
    if f['name'] not in MOT: continue
    x0,y0,x1,y1=f['editablePixelRectExclusive']
    ps=[s for s in f['materialSlots'] if s['name'].endswith('_Painting')][0]; (u0,v0),(u1,v1)=ps['uv0Min'],ps['uv0Max']
    n=f['name'][-1]; ext=fr[n]['painting_extent']; aspect=ext[0]/ext[2]
    art=MOT[f['name']](aspect).convert('RGBA')
    px0,px1=u0*2048,u1*2048; py0,py1=(1-v1)*2048,(1-v0)*2048
    assert x0<=px0 and px1<=x1 and y0<=py0 and py1<=y1
    xs=np.clip((np.arange(x0,x1)+0.5-px0)/(px1-px0),0,1); ys=np.clip((np.arange(y0,y1)+0.5-py0)/(py1-py0),0,1)
    a=np.array(art).astype(float); ah,aw=a.shape[:2]; gx=xs*(aw-1); gy=ys*(ah-1)
    X0=np.floor(gx).astype(int); Y0=np.floor(gy).astype(int); X1=np.minimum(X0+1,aw-1); Y1=np.minimum(Y0+1,ah-1); fx=gx-X0; fy=gy-Y0
    top=a[Y0][:,X0]*(1-fx)[None,:,None]+a[Y0][:,X1]*fx[None,:,None]; bot=a[Y1][:,X0]*(1-fx)[None,:,None]+a[Y1][:,X1]*fx[None,:,None]
    tile=top*(1-fy)[:,None,None]+bot*fy[:,None,None]; tile[...,3]=255
    OUT[y0:y1,x0:x1]=np.clip(np.round(tile),0,255).astype(np.uint8)
    art.convert('RGB').save(f'art2/motif_{f["name"]}.png')
    log.append({'frame':f['name'],'tile':f['paintingAtlasTile'],'rect':[x0,y0,x1,y1],'uv0_box_px':[px0,py0,px1,py1],'painting_aspect_w_over_h':aspect})
Image.fromarray(OUT).convert(Image.open(SRC).mode).save(OUTP,optimize=True)
B=np.array(Image.open(OUTP).convert('RGBA')); mask=np.ones(A.shape[:2],bool)
for l in log: x0,y0,x1,y1=l['rect']; mask[y0:y1,x0:x1]=False
diff=(A!=B).any(-1)
info={'size':list(B.shape[:2][::-1]),'mode':Image.open(OUTP).mode,'edited_frames':[l['frame'] for l in log],'unchanged_frames':['LAY03_UpperFrame_2','LAY03_UpperFrame_3'],
 'pixels_changed_outside_edited_rects':int((diff&mask).sum()),'pixels_changed_inside':int((diff&~mask).sum()),
 'rgba_sha256_outside_source':hashlib.sha256(A[mask].tobytes()).hexdigest(),'rgba_sha256_outside_candidate':hashlib.sha256(B[mask].tobytes()).hexdigest(),'tiles':log}
json.dump(info,open('art2/A1_check.json','w'),indent=1); print(json.dumps(info)[:700])
