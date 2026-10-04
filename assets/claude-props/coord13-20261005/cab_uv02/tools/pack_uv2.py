# CABUV02: relocate the 107 added UV2 charts (402 editable vertices) into free space of the FIXED UV2 layout.
# Chart shape kept exactly (rigid translation, rotation by multiples of 90deg only if needed; no scaling, no mirroring),
# so density/distortion stay at baseline. Fixed UV2 0..9038 is never modified.
# Search: conservative raster (N px) + Euclidean distance transform; exact verification is done separately in qa_uv2.py.
# usage: python pack_uv2.py native_mesh.json edit_scope.json out_dir
import sys,json,time
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
from scipy.signal import fftconvolve
mj,ej,od=sys.argv[1:4]
m=json.load(open(mj)); e=json.load(open(ej))
uv32=np.array(m['attributes']['uv2'],dtype=np.float32); uv=uv32.astype(np.float64)
T=np.array(m['submeshes'][0]['triangles'],dtype=np.int64).reshape(-1,3)
F=T[:4220]; A=T[4220:]; E=e['editableVertexIds']
assert sorted(set(A.ravel().tolist()))==E, 'every editable vertex must be used by an added triangle'
N=2048
# added charts (vertex-id connectivity)
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
fixed_occ=raster([uv[t] for t in F],(N,N))
fixed_occ|=np.roll(fixed_occ,1,0)|np.roll(fixed_occ,-1,0); fixed_occ|=np.roll(fixed_occ,1,1)|np.roll(fixed_occ,-1,1)  # +1px conservative
ROT=[np.eye(2),np.array([[0,-1],[1,0.]]),np.array([[-1,0],[0,-1.]]),np.array([[0,1],[-1,0.]])]
def chart_pts(c,r):
    vs=np.unique(A[c].ravel()); P=uv[vs]@ROT[r].T
    return vs,P
def pack(margin):
    occ=fixed_occ.copy(); placed={}; failed=[]; rp=margin*N+1.5
    bw=int(np.ceil(margin*N))+1
    order=sorted(range(len(charts)),key=lambda k:-np.prod(np.ptp(uv[np.unique(A[charts[k]].ravel())],0)+1e-4))
    for k in order:
        c=charts[k]; ok=False
        blocked=distance_transform_edt(~occ)<=rp
        blocked[:bw,:]=True; blocked[-bw:,:]=True; blocked[:,:bw]=True; blocked[:,-bw:]=True
        for r in range(4):
            vs,P=chart_pts(c,r); o=np.floor(P.min(0)*N)/N-1.0/N
            loc=P-o; idx={v:i for i,v in enumerate(vs)}
            sh=(int(np.ceil(loc[:,1].max()*N))+2,int(np.ceil(loc[:,0].max()*N))+2)
            M=raster([loc[[idx[v] for v in A[t]]] for t in c],sh)
            M|=np.roll(M,1,0)|np.roll(M,1,1)
            corr=fftconvolve(blocked.astype(np.float32),M[::-1,::-1].astype(np.float32),mode='valid')
            val=np.argwhere(corr<0.5)
            if len(val):
                y,x=val[0]; off=np.array([x,y])/N
                newP=loc+off; placed[k]=(r,vs,newP)
                sub=occ[y:y+sh[0],x:x+sh[1]]; sub|=M
                ok=True; break
        if not ok: failed.append(k)
    return placed,failed
res={'N':N,'charts':len(charts),'ladder':[]}
best=None
for margin in [0.03125,0.0234375,0.015625,0.01171875,0.0078125,0.005859375,0.00390625]:
    t0=time.time(); pl,fail=pack(margin)
    fa=[np.ptp(uv[np.unique(A[charts[k]].ravel())],0) for k in fail]
    res['ladder'].append({'targetMarginUv':margin,'allPlaced':not fail,'placedCharts':len(pl),'unplacedCharts':len(fail),
        'unplacedTriangles':sum(len(charts[k]) for k in fail),'unplacedUvAreaSum':float(sum(abs(np.cross(uv[A[t][1]]-uv[A[t][0]],uv[A[t][2]]-uv[A[t][0]]))/2 for k in fail for t in charts[k])),
        'unplacedChartBboxUv':[[round(float(x),5) for x in b] for b in fa],'sec':round(time.time()-t0,1)})
    print(res['ladder'][-1],flush=True)
    if not fail and best is None: best=(margin,pl)
if best:
    margin,pl=best; new=uv32[:].copy()
    rots={}
    for k,(r,vs,P) in pl.items():
        new[vs]=P.astype(np.float32); rots[k]=r
    res['chosenTargetMarginUv']=margin
    res['rotationHistogram']={str(r):sum(1 for x in rots.values() if x==r) for r in range(4)}
    np.save(od+'/new_uv2_editable.npy',new[E])
json.dump(res,open(od+'/pack_log.json','w'),indent=1)
