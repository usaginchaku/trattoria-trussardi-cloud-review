# CABUV02 baseline QA (input as delivered, nothing edited): exact triangle-clipping overlap of added vs fixed/added,
# per-triangle density sqrt(|UV area|/world area) with localToWorld from native_mesh.json, fixed density percentiles,
# exact minimum distance of added triangles to the unit-square edge.
# usage: python qa_baseline.py native_mesh.json out.json
import sys,json
import numpy as np
from uvgeom import clip_area,sarea,Grid
mj,out=sys.argv[1:3]; m=json.load(open(mj))
uv=np.array(m['attributes']['uv2'],dtype=np.float32).astype(np.float64)
P=np.array(m['attributes']['positions'],dtype=np.float32).astype(np.float64)
T=np.array(m['submeshes'][0]['triangles'],dtype=np.int64).reshape(-1,3)
L=m['unitsAndAxes']['localToWorld']; M=np.array([[L['e%d%d'%(i,j)] for j in range(4)] for i in range(4)])
W=P@M[:3,:3].T
ua=np.array([abs(sarea(uv[t])) for t in T]); wa=np.linalg.norm(np.cross(W[T[:,1]]-W[T[:,0]],W[T[:,2]]-W[T[:,0]]),axis=1)/2
dens=np.sqrt(ua/wa)
FT=[uv[t] for t in T[:4220]]; g=Grid(FT)
ov_fixed=[]; 
for i in range(4220,4408):
    a=uv[T[i]]; s=sum(clip_area(a,FT[k]) for k in g.near(a,0.0))
    ov_fixed.append(s)
AT=[uv[t] for t in T[4220:]]; ga=Grid(AT); ov_add=0.0
for i,a in enumerate(AT):
    for k in ga.near(a,0.0):
        if k>i: ov_add+=clip_area(a,AT[k])
fd=dens[:4220][ua[:4220]>0]
pc=[0,1,5,10,25,50,75,90,95,99,100]
res={'method':'Sutherland-Hodgman convex clipping in float64 of Float32 UV2; spatial hash candidates; edge contact counts as 0 area (and as 0 padding)',
 'addedUvAreaSum':float(ua[4220:].sum()),'fixedUvAreaSum':float(ua[:4220].sum()),
 'addedVsFixedPositiveOverlapAreaSum':float(sum(ov_fixed)),'addedTrianglesWithPositiveOverlapVsFixed':int(sum(1 for x in ov_fixed if x>0)),
 'addedVsAddedPositiveOverlapAreaSum':ov_add,
 'addedMinDistToUnitSquareEdge':float(min(min(uv[v].min(),1-uv[v].max()) for v in range(9039,9441))),
 'density':{'definition':'sqrt(|UV area|/world area), world via native localToWorld (UV units per world metre)',
   'addedMinMedianMax':[float(np.min(dens[4220:])),float(np.median(dens[4220:])),float(np.max(dens[4220:]))],
   'addedAreaWeighted':float(np.average(dens[4220:],weights=wa[4220:])),
   'fixedNondegenerateCount':int(len(fd)),'fixedPercentiles':{str(p):float(np.percentile(fd,p)) for p in pc},
   'fixedAreaWeighted':float(np.average(dens[:4220],weights=wa[:4220]))},
 'fixedZeroUvAreaTriangles':int((ua[:4220]==0).sum())}
json.dump(res,open(out,'w'),indent=1); print(json.dumps(res,indent=1))
