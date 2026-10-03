# COORD09: single-factor basket candidates on top of COORD07 B.
#  W = lower slat/core contrast: core UVMap moved to a mid-tone atlas patch (weave texture itself not reproduced)
#  D = outer leaf parts bend down over the rim (length-preserving arc bend, leaves only)
#  L = leaves lengthened 1.25x along their own root->tip axis (width unchanged -> slimmer, sharper look)
import bpy,bmesh,json,sys,math,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src,factor,tag=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=src)
import os
OBJ=os.environ.get('OBJ','02_Flower_Basket_Mesh'); o=bpy.data.objects[OBJ]; me=o.data
uv_before={u.name:[tuple(l.uv) for l in u.data] for u in me.uv_layers}
atlas=[n.image for n in me.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image and 'BaseColor' in n.image.name][0]
W,H=atlas.size; px=np.array(atlas.pixels[:]).reshape(H,W,4)
def col(u,v): return px[min(H-1,max(0,int(v*H))),min(W-1,max(0,int(u*W))),:3]
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
uvl=bm.loops.layers.uv['UVMap']
seen=set(); isl=[]
for v in bm.verts:
    if v.index in seen: continue
    st=[v]; c=[]
    while st:
        x=st.pop()
        if x.index in seen: continue
        seen.add(x.index); c.append(x.index); st+=[e.other_vert(x) for e in x.link_edges]
    isl.append(c)
RIM=max(bm.verts[i].co.z for c in isl for i in c if min(bm.verts[j].co.z for j in c)<0.0625)
kind={}
for n,c in enumerate(isl):
    zlo=min(bm.verts[i].co.z for i in c)
    if zlo<0.0625: kind[n]='basket'; continue
    cs=[col(*l[uvl].uv) for i in c for l in bm.verts[i].link_loops]
    r,g,b=np.mean(cs,0); kind[n]='leaf' if g>r else 'flower'
cnt={k:sum(1 for v in kind.values() if v==k) for k in ('basket','leaf','flower')}
# rim outer half extents (top of basket)
bv=[bm.verts[i].co for n,c in enumerate(isl) if kind[n]=='basket' for i in c]
RX=max(abs(v.x) for v in bv if v.z>RIM-0.004); RY=max(abs(v.y) for v in bv if v.z>RIM-0.004)
info={'factor':factor,'tag':tag,'rim_top_m':RIM,'rim_half_extent_m':[RX,RY],'islands':cnt}
leaf_vidx=[i for n,c in enumerate(isl) if kind[n]=='leaf' for i in c]
if factor in('D','D2'):
    Rb,CAP=(0.035,9) if factor=='D' else (0.022,math.radians(80)); M=0.003; moved=0; maxdrop=0
    for i in leaf_vidx:
        v=bm.verts[i].co
        dx=max(0,abs(v.x)-(RX+M)); dy=max(0,abs(v.y)-(RY+M)); d=math.hypot(dx,dy)
        if d<=0: continue
        nx=math.copysign(dx,v.x)/d; ny=math.copysign(dy,v.y)/d
        th=d/Rb
        if th<=CAP: hor=Rb*math.sin(th)-d; drop=Rb*(1-math.cos(th))
        else:
            rest=d-Rb*CAP; hor=Rb*math.sin(CAP)+rest*math.cos(CAP)-d; drop=Rb*(1-math.cos(CAP))+rest*math.sin(CAP)
        v.x+=nx*hor; v.y+=ny*hor; v.z-=drop; moved+=1; maxdrop=max(maxdrop,drop)
    info.update(bend_radius_m=Rb,angle_cap_deg=math.degrees(CAP) if CAP<9 else None,margin_m=M,leaf_verts_moved=moved,max_drop_m=maxdrop)
elif factor in('L','L2','L3'):
    s=1.15 if factor=='L3' else 1.25; ext=[]; skipped=0; MAXEL=math.radians(35)
    for n,c in enumerate(isl):
        if kind[n]!='leaf': continue
        P=[bm.verts[i].co for i in c]
        root=min(P,key=lambda p:math.hypot(p.x,p.y)).copy()
        tip=max(P,key=lambda p:(p-root).length).copy()
        ax=(tip-root).normalized()
        if factor in('L2','L3') and math.asin(max(-1,min(1,ax.z)))>MAXEL: skipped+=1; continue
        for p in P:
            t=(p-root).dot(ax)
            if t>0: p+=ax*t*(s-1)
        ext.append((tip-root).length*(s-1))
    info.update(length_scale=s,max_elevation_deg=35 if factor in('L2','L3') else None,leaf_islands_scaled=len(ext),leaf_islands_skipped=skipped,mean_extension_m=float(np.mean(ext)),max_extension_m=float(np.max(ext)))
elif factor=='W':
    # v02 already has a closed dark core (96 verts) behind the slats; the stripe look comes from slat/core contrast.
    # Single factor: core UVMap -> uniform 17x17 px atlas patch at 70% slat / 30% core tone. Geometry, texture, LightmapUV unchanged.
    TGT=Vector((0.06006,0.36670)); core=None
    for n,c in enumerate(isl):
        if kind[n]=='basket' and len(c)==96: core=c
    allf=set(f for i in core for f in bm.verts[i].link_faces); fs=set(f for f in allf if abs(f.normal.z)<0.5)  # side walls only; top (soil) and bottom keep v02 UV
    before=np.mean([col(*l[uvl].uv) for f in fs for l in f.loops],0)
    for f in fs:
        for l in f.loops: l[uvl].uv=TGT
    info.update(core_verts=len(core),core_faces=len(allf),core_side_faces_remapped=len(fs),core_colour_before=list(map(float,before)),core_colour_after=list(map(float,col(*TGT))),target_uv=list(TGT),
                note='uniform patch 17x17 px (std<0.003); mip levels below ~64 px may blend neighbours')
bm.normal_update()
bm.to_mesh(me); me.update()
# checks
bm2=bmesh.new(); bm2.from_mesh(me); bm2.faces.ensure_lookup_table(); bm2.verts.ensure_lookup_table()
nb=len([1 for n in kind if kind[n]=='basket'])
bas_v=set(i for n,c in enumerate(isl) if kind[n]=='basket' for i in c)
nv0=len(uv_before['UVMap'])
def sub_bvh(pred):
    b=bmesh.new(); vm={}
    for f in bm2.faces:
        if not pred(f): continue
        vs=[]
        for v in f.verts:
            if v.index not in vm: vm[v.index]=b.verts.new(v.co)
            vs.append(vm[v.index])
        try: b.faces.new(vs)
        except ValueError: pass
    t=BVHTree.FromBMesh(b); b.free(); return t
NV=sum(len(c) for c in isl)
isfol=lambda f: f.verts[0].index<NV and f.verts[0].index not in bas_v
isbas=lambda f: f.verts[0].index<NV and f.verts[0].index in bas_v
isnew=lambda f: f.verts[0].index>=NV
info['foliage_basket_tri_overlaps']=len(sub_bvh(isfol).overlap(sub_bvh(isbas)))
if False:
    info['liner_basket_tri_overlaps']=len(sub_bvh(isnew).overlap(sub_bvh(isbas)))
    info['liner_foliage_tri_overlaps']=len(sub_bvh(isnew).overlap(sub_bvh(isfol)))
zs=[v.co.z for v in me.vertices]
co=np.array([v.co[:] for v in me.vertices])
info.update(zmin=min(zs),zmax=max(zs),dims=list(map(float,np.ptp(co,0))),tris=sum(len(p.vertices)-2 for p in me.polygons),
 nonmanifold=sum(1 for e in bm2.edges if not e.is_manifold),boundary=sum(1 for e in bm2.edges if e.is_boundary),
 zero_area=sum(1 for f in bm2.faces if f.calc_area()<1e-12),
 uv_unchanged=all(uv_before[u.name]==[tuple(l.uv) for l in u.data][:len(uv_before[u.name])] for u in me.uv_layers) if False else uv_before=={u.name:[tuple(l.uv) for l in u.data] for u in me.uv_layers})
bpy.ops.wm.save_as_mainfile(filepath=f'c9/basket_{tag}.blend',compress=False)
json.dump(info,open(f'c9/basket_{tag}.json','w'),indent=1); print(json.dumps(info))
