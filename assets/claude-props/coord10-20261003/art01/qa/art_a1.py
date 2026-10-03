# ART01 A1: self-authored motifs for tiles 21-24 of PaintingAtlas_FUR06.png only (procedural vector shapes, no reference pixels used).
# Each motif is drawn at the painting face's true aspect (w/h from the FBX), then resampled into the exact UV box of that frame;
# the strip between UV box and the editable rect is filled by edge extension (mip bleed). Pixels outside the 4 editable rects are copied unchanged.
import json,sys,hashlib,numpy as np
from PIL import Image,ImageDraw,ImageFilter
SRC='src9/assets/codex-source/coord10-art01-20261003/PaintingAtlas_FUR06.png'
scope=json.load(open('src9/assets/codex-source/coord10-art01-20261003/frame_scope.json'))
fr=json.load(open('c9/art_frames.json'))
SS=4
def canvas(aspect,H=900):
    W=int(H*aspect); im=Image.new('RGB',(W*SS,H*SS),(0,0,0)); return im,ImageDraw.Draw(im),W*SS,H*SS
def E(d,cx,cy,rx,ry,col,W,H): d.ellipse([ (cx-rx)*W,(cy-ry)*H,(cx+rx)*W,(cy+ry)*H ],fill=col)
def P(d,pts,col,W,H): d.polygon([(x*W,y*H) for x,y in pts],fill=col)
def finish(im):
    im=im.filter(ImageFilter.GaussianBlur(SS*2.2)); return im.resize((im.width//SS,im.height//SS),Image.LANCZOS)
def m22(a):  # Frame_22 (tile21): pale sky, terracotta stepped diagonal mass right/lower
    im,d,W,H=canvas(a); d.rectangle([0,0,W,H],fill=(226,230,229))
    for cx,cy,rx,ry,c in [(0.30,0.18,0.30,0.16,(200,212,220)),(0.22,0.45,0.22,0.14,(214,222,228)),(0.62,0.10,0.25,0.10,(235,236,233))]: E(d,cx,cy,rx,ry,c,W,H)
    P(d,[(1.0,0.12),(0.86,0.16),(0.80,0.27),(0.70,0.30),(0.64,0.42),(0.52,0.47),(0.46,0.60),(0.30,0.66),(0.24,0.78),(0.10,0.84),(0.06,1.0),(1.0,1.0)],(196,112,64),W,H)
    P(d,[(1.0,0.30),(0.90,0.33),(0.84,0.45),(0.74,0.50),(0.70,0.62),(0.58,0.68),(0.54,0.80),(1.0,0.86)],(214,140,86),W,H)
    for cx,cy,rx,ry,c in [(0.14,0.62,0.09,0.06,(176,198,216)),(0.40,0.36,0.07,0.05,(186,204,220))]: E(d,cx,cy,rx,ry,c,W,H)
    return finish(im)
def m23(a):  # Frame_23 (tile22): white ground, lavender row of rounded humps (centre tallest), merged base, top ~35% white
    im,d,W,H=canvas(a); d.rectangle([0,0,W,H],fill=(242,241,238))
    col=(171,164,214); col2=(186,180,225)
    for cx,cy,rx,ry in [(0.17,0.62,0.15,0.18),(0.38,0.56,0.15,0.22),(0.60,0.44,0.14,0.30),(0.82,0.60,0.14,0.20)]: E(d,cx,cy,rx,ry,col,W,H)
    d.rectangle([0.03*W,0.62*H,0.96*W,0.92*H],fill=col)
    for cx,cy,rx,ry in [(0.27,0.64,0.10,0.12),(0.49,0.60,0.10,0.14),(0.71,0.62,0.10,0.12)]: E(d,cx,cy,rx,ry,col,W,H)
    for cx,cy,rx,ry in [(0.58,0.34,0.05,0.10),(0.36,0.52,0.05,0.08),(0.18,0.60,0.04,0.06)]: E(d,cx,cy,rx,ry,col2,W,H)
    return finish(im)
def m24(a):  # Frame_24 (tile23): blue stacked vertical mass (left) + ochre vertical mass (right) on cream
    im,d,W,H=canvas(a); d.rectangle([0,0,W,H],fill=(238,235,226))
    oc=(206,166,108); oc2=(216,182,130)
    for cx,cy,rx,ry in [(0.70,0.38,0.18,0.14),(0.72,0.56,0.20,0.18),(0.70,0.78,0.19,0.16)]: E(d,cx,cy,rx,ry,oc,W,H)
    E(d,0.76,0.58,0.08,0.12,oc2,W,H)
    bl=(72,124,196); bl2=(94,144,210)
    for cx,cy,rx,ry in [(0.44,0.15,0.19,0.12),(0.36,0.33,0.24,0.14),(0.32,0.54,0.22,0.16),(0.36,0.76,0.23,0.17)]: E(d,cx,cy,rx,ry,bl,W,H)
    E(d,0.30,0.58,0.09,0.12,bl2,W,H); E(d,0.48,0.12,0.07,0.05,bl2,W,H)
    return finish(im)
def m25(a):  # Frame_25 (tile24): purple branching coral/antler (chunky, rounded tips) on white; lighter lavender lower mass
    im,d,W,H=canvas(a); d.rectangle([0,0,W,H],fill=(242,240,244))
    lv=(196,172,218); E(d,0.62,0.74,0.30,0.16,lv,W,H); E(d,0.42,0.86,0.24,0.10,lv,W,H)
    pu=(150,104,182)
    def stroke(pts,wid):
        d.line([(x*W,y*H) for x,y in pts],fill=pu,width=int(wid*W),joint='curve')
        for x,y in pts: d.ellipse([x*W-wid*W/2,y*H-wid*W/2,x*W+wid*W/2,y*H+wid*W/2],fill=pu)
    stroke([(0.42,0.90),(0.44,0.70),(0.40,0.52),(0.44,0.36)],0.17)
    stroke([(0.44,0.36),(0.30,0.22),(0.26,0.10)],0.14); stroke([(0.44,0.36),(0.62,0.24),(0.70,0.12)],0.14)
    stroke([(0.62,0.24),(0.82,0.26)],0.11); stroke([(0.30,0.22),(0.14,0.27)],0.10)
    stroke([(0.42,0.60),(0.60,0.55),(0.72,0.45)],0.12); stroke([(0.42,0.74),(0.22,0.70)],0.11)
    for x,y,r in [(0.26,0.10,0.09),(0.70,0.12,0.09),(0.82,0.26,0.07),(0.14,0.27,0.07),(0.72,0.45,0.08),(0.22,0.70,0.07)]: E(d,x,y,r,r*W/H*0.0+r*a,pu,W,H)
    return finish(im)
MOT={'22':m22,'23':m23,'24':m24,'25':m25}
A=np.array(Image.open(SRC).convert('RGBA')); OUT=A.copy(); H=A.shape[0]
log=[]
for f in scope['frames']:
    n=f['sourceSpec']['name'].split('_')[1]
    x0,y0,x1,y1=f['editablePixelRectExclusive']
    u0,v0=f['paintingUvMin']; u1,v1=f['paintingUvMax']
    ext=fr[n]['painting_extent']; aspect=ext[0]/ext[2]
    art=MOT[n](aspect).convert('RGBA')
    # UV box in pixel coordinates (float), rows from top
    px0,px1=u0*2048,u1*2048; py0,py1=(1-v1)*2048,(1-v0)*2048
    rw,rh=x1-x0,y1-y0
    # sample art for every pixel centre of the editable rect: map pixel centre -> art coords, clamp outside UV box (edge extension)
    xs=(np.arange(x0,x1)+0.5-px0)/(px1-px0); ys=(np.arange(y0,y1)+0.5-py0)/(py1-py0)
    xs=np.clip(xs,0,1); ys=np.clip(ys,0,1)
    a=np.array(art).astype(float); ah,aw=a.shape[:2]
    gx=xs*(aw-1); gy=ys*(ah-1)
    X0=np.floor(gx).astype(int); Y0=np.floor(gy).astype(int); X1=np.minimum(X0+1,aw-1); Y1=np.minimum(Y0+1,ah-1); fx=gx-X0; fy=gy-Y0
    top=a[Y0][:,X0]*(1-fx)[None,:,None]+a[Y0][:,X1]*fx[None,:,None]; bot=a[Y1][:,X0]*(1-fx)[None,:,None]+a[Y1][:,X1]*fx[None,:,None]
    tile=top*(1-fy)[:,None,None]+bot*fy[:,None,None]
    tile[...,3]=255
    OUT[y0:y1,x0:x1]=np.clip(np.round(tile),0,255).astype(np.uint8)
    art.convert('RGB').save(f'c9/art_A1_motif_F{n}.png')
    log.append({'frame':f'Frame_{n}','tile':f['paintingAtlasTile'],'rect':[x0,y0,x1,y1],'uv_box_px':[px0,py0,px1,py1],'painting_aspect_w_over_h':aspect})
Image.fromarray(OUT).convert(Image.open(SRC).mode).save('c9/PaintingAtlas_FUR06_A1.png',optimize=True)
# outside-rect identity check on decoded RGBA
B=np.array(Image.open('c9/PaintingAtlas_FUR06_A1.png').convert('RGBA')); mask=np.ones(A.shape[:2],bool)
for f in scope['frames']:
    x0,y0,x1,y1=f['editablePixelRectExclusive']; mask[y0:y1,x0:x1]=False
diff=(A!=B).any(-1)
info={'size':list(B.shape[:2][::-1]),'mode':Image.open('c9/PaintingAtlas_FUR06_A1.png').mode,'pixels_changed_outside_rects':int((diff&mask).sum()),'pixels_changed_inside_rects':int((diff&~mask).sum()),
 'rgba_sha256_outside_rects_source':hashlib.sha256(A[mask].tobytes()).hexdigest(),'rgba_sha256_outside_rects_A1':hashlib.sha256(B[mask].tobytes()).hexdigest(),'tiles':log}
json.dump(info,open('c9/art_A1_check.json','w'),indent=1); print(json.dumps(info)[:600])
