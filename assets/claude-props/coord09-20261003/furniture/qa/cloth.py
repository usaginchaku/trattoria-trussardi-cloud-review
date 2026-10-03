# COORD09 tablecloth hem candidates (shape only; colour/material/UV untouched; wood untouched)
#  T1: hem vertical lobes deepened (hem-height variation x K about its mean), blended by drop fraction s^P so the tabletop edge stays fixed
#  T2: radial fold valleys deepened inward (distance below per-height outer radius x K), blended by s; outer radius kept
import bpy,bmesh,sys,json,math,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src,mode,K,tag=sys.argv[sys.argv.index('--')+1:]; K=float(K)
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=src)
o=bpy.data.objects['DiningTable']; me=o.data
uv_before=[tuple(l.uv) for l in me.uv_layers[0].data]
cn_before=[tuple(c.vector) for c in me.corner_normals]
co=np.array([v.co[:] for v in me.vertices])
isl=lambda p: me.materials[p.material_index].name.startswith('linen')
cl=np.array(sorted({v for p in me.polygons if isl(p) for v in p.vertices}))
wood=np.array(sorted({v for p in me.polygons if not isl(p) for v in p.vertices}))
assert not set(cl)&set(wood)
TOP=0.7195; c=co[cl]; r=np.hypot(c[:,0],c[:,1]); th=np.arctan2(c[:,1],c[:,0]); sk=c[:,2]<TOP
B=360
def binof(t): return ((t+math.pi)/(2*math.pi)*B).astype(int)%B
bi=binof(th)
# hem z per angle bin (smoothed)
hz=np.full(B,np.nan)
for k in range(B):
    m=sk&(bi==k)
    if m.any(): hz[k]=c[m,2].min()
idx=np.arange(B); g=~np.isnan(hz); hz=np.interp(idx,idx[g],hz[g],period=B)
F=np.fft.rfft(hz); NH=8; F[NH+1:]=0; hz=np.fft.irfft(F,B)  # smooth hem curve: Fourier harmonics 0..8 only
def hzf(t):  # continuous evaluation (no bin steps)
    k=np.arange(1,NH+1); a=F[1:NH+1]/B*2; tt=(t+math.pi)/(2*math.pi)*2*math.pi
    return F[0].real/B+np.real(np.exp(1j*np.outer(tt,k))@a)
EDGE=0.68  # z where the skirt leaves the table edge (below the rounded top edge)
new=c.copy(); info={'mode':mode,'K':K,'hem_fit_harmonics':8}
H=hzf(th); s=np.clip((EDGE-c[:,2])/(EDGE-H),0,1)
if mode=='T1':
    P=1.5; mean=hz.mean(); dz=(K-1)*(H-mean)*s**P
    new[:,2]=c[:,2]+np.where(sk,dz,0)
    info.update(power=P,hem_z_before=[float(hz.min()),float(hz.max())],hem_z_after=[float(mean+K*(hz.min()-mean)),float(mean+K*(hz.max()-mean))])
elif mode=='T2':
    # per height band outer radius
    zb=np.round(c[:,2]/0.01).astype(int); rmax={}
    for z_ in np.unique(zb): rmax[z_]=r[zb==z_].max()
    ro=np.array([rmax[z_] for z_ in zb])
    rn=np.where(sk&(s>0), ro-(ro-r)*(1+(K-1)*s), r)
    f=np.where(r>1e-6,rn/np.maximum(r,1e-9),1); new[:,0]=c[:,0]*f; new[:,1]=c[:,1]*f
    info.update(r_min_before=float(r[sk].min()),r_min_after=float(np.hypot(new[sk,0],new[sk,1]).min()))
for i,v in enumerate(cl): me.vertices[v].co=new[i]
me.update()
# normals: original custom normals equal default smooth normals (dot=1.0 everywhere, measured).
# Keep wood corners' stored normals; cloth corners take the recomputed default smooth normal of the new shape.
tmp=me.copy(); tmp.normals_split_custom_set([(0,0,0)]*len(tmp.loops)); dn=[tuple(c_.vector) for c_ in tmp.corner_normals]; bpy.data.meshes.remove(tmp)
clset=set(cl.tolist()); loops=[]
for p in me.polygons:
    for li in p.loop_indices: loops.append(dn[li] if isl(p) else cn_before[li])
me.normals_split_custom_set(loops); me.update()
# checks
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
def bvh(pred):
    b=bmesh.new(); vm={}
    for f in bm.faces:
        if pred(f):
            vs=[]
            for v in f.verts:
                if v.index not in vm: vm[v.index]=b.verts.new(v.co)
                vs.append(vm[v.index])
            b.faces.new(vs)
    return BVHTree.FromBMesh(b)
woodset=set(wood.tolist())
isw=lambda f: f.verts[0].index in woodset
inter=len(bvh(lambda f: not isw(f)).overlap(bvh(isw)))
co2=np.array([v.co[:] for v in me.vertices])
cn_after=[tuple(c_.vector) for c_ in me.corner_normals]
info.update(cloth_verts=len(cl),cloth_wood_tri_overlaps=inter,
  dims_before=list(map(float,np.ptp(co,0))),dims_after=list(map(float,np.ptp(co2,0))),zmin_after=float(co2[:,2].min()),
  cloth_zmin_after=float(co2[cl,2].min()),tris=sum(len(p.vertices)-2 for p in me.polygons),
  uv_unchanged=uv_before==[tuple(l.uv) for l in me.uv_layers[0].data],
  wood_normals_unchanged=all(cn_after[li]==cn_before[li] or np.allclose(cn_after[li],cn_before[li],atol=1e-4) for p in me.polygons if not isl(p) for li in p.loop_indices),
  wood_verts_unchanged=bool(np.allclose(co2[wood],co[wood])),
  nonmanifold=sum(1 for e in bm.edges if not e.is_manifold),boundary=sum(1 for e in bm.edges if e.is_boundary),zero_area=sum(1 for f in bm.faces if f.calc_area()<1e-12),
  zero_len_corner_normals=int(sum(1 for x in cn_after if Vector(x).length<1e-6)))
# baseline boundary count for reference
bpy.ops.wm.save_as_mainfile(filepath=f'c9/table_{tag}.blend',compress=False)
json.dump(info,open(f'c9/table_{tag}.json','w'),indent=1); print(json.dumps(info))
