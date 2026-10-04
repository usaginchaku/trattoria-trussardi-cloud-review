# CABUV02 probe: for the added charts that do not fit at scale 1, find the largest uniform scale s (about chart centroid,
# rotations 0/90/180/270, no mirroring) at which they fit into the FIXED UV2 free space with a given normalized margin,
# then check the remaining charts still fit at scale 1. Raster search only (N px, +1px conservative); informs HOLD/candidate.
# usage: python scale_probe.py native_mesh.json out.json [margins comma list] [scale step]
import sys,json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
from scipy.signal import fftconvolve
mj,out=sys.argv[1:3]
MARGINS=[float(x) for x in sys.argv[3].split(',')] if len(sys.argv)>3 else [0.01171875,0.0078125,0.00390625]
STEP=float(sys.argv[4]) if len(sys.argv)>4 else 0.025
m=json.load(open(mj)); uv=np.array(m['attributes']['uv2'],dtype=np.float32).astype(np.float64)
T=np.array(m['submeshes'][0]['triangles'],dtype=np.int64).reshape(-1,3); F=T[:4220]; A=T[4220:]; N=2048
par=list(range(len(uv)))
def f(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
for t in A:
    for v in t[1:]: par[f(v)]=f(t[0])
ch={}
for i,t in enumerate(A): ch.setdefault(f(t[0]),[]).append(i)
charts=list(ch.values())
def raster(polys,shape):
    im=Image.new('L',(shape[1],shape[0]),0); d=ImageDraw.Draw(im)
    for p in polys: d.polygon([tuple(x) for x in (p*N).tolist()],fill=1,outline=1)
    return np.array(im,dtype=bool)
fo=raster([uv[t] for t in F],(N,N)); fo|=np.roll(fo,1,0)|np.roll(fo,-1,0); fo|=np.roll(fo,1,1)|np.roll(fo,-1,1)
ROT=[np.eye(2),np.array([[0,-1],[1,0.]]),np.array([[-1,0],[0,-1.]]),np.array([[0,1],[-1,0.]])]
def area(c): return sum(abs(np.cross(uv[A[t][1]]-uv[A[t][0]],uv[A[t][2]]-uv[A[t][0]]))/2 for t in c)
def try_place(occ,c,s,margin):
    blocked=(distance_transform_edt(~occ)<=margin*N+1.5) if margin>0 else occ.copy(); bw=int(np.ceil(margin*N))+1 if margin>0 else 0
    if bw: blocked[:bw,:]=True; blocked[-bw:,:]=True; blocked[:,:bw]=True; blocked[:,-bw:]=True
    vs=np.unique(A[c].ravel()); cen=uv[vs].mean(0)
    for r in range(4):
        P=(uv[vs]-cen)*s@ROT[r].T; o=np.floor(P.min(0)*N)/N-1.0/N; loc=P-o; idx={v:i for i,v in enumerate(vs)}
        sh=(int(np.ceil(loc[:,1].max()*N))+2,int(np.ceil(loc[:,0].max()*N))+2)
        if sh[0]>=N or sh[1]>=N: continue
        M=raster([loc[[idx[v] for v in A[t]]] for t in c],sh); M|=np.roll(M,1,0)|np.roll(M,1,1)
        corr=fftconvolve(blocked.astype(np.float32),M[::-1,::-1].astype(np.float32),mode='valid')
        val=np.argwhere(corr<0.5)
        if len(val):
            y,x=val[0]; occ=occ.copy(); occ[y:y+sh[0],x:x+sh[1]]|=M; return occ,r
    return None,None
order=sorted(range(len(charts)),key=lambda k:-area(charts[k])); big=order[:2]; rest=order[2:]
res={'N':N,'bigCharts':[{'tris':[4220+i for i in charts[k]],'uvArea':area(charts[k]),'bboxUv':np.ptp(uv[np.unique(A[charts[k]].ravel())],0).tolist()} for k in big],
     'addedUvAreaTotal':sum(area(c) for c in charts),'probe':[]}
for margin in MARGINS:
    best=None
    for s in np.round(np.arange(1.0,0.19,-STEP),3):
        occ=fo
        ok=True
        for k in big:
            occ,r=try_place(occ,charts[k],s,margin)
            if occ is None: ok=False; break
        if ok: best=float(s); break
    restok=None
    if best:
        placed=0
        for k in rest:
            o2,_=try_place(occ,charts[k],1.0,margin)
            if o2 is not None: occ=o2; placed+=1
        restok=placed
    row={'marginUv':margin,'maxScaleBothBigCharts':best,'densityRatioAtThatScale':best,'texelAreaRatio':None if best is None else best*best,
         'restChartsPlacedAtScale1':restok,'restChartsTotal':len(rest)}
    res['probe'].append(row); print(row,flush=True)
json.dump(res,open(out,'w'),indent=1)
