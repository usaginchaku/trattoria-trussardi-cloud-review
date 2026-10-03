# CAB03 C3: K2 wall cabinet -> smaller glass panes / wider door frames (stiles, top/bottom rails, middle rail), knobs translated (kept round).
# Optional MOLD=1: one-step shading at top/bottom by insetting the strip under/over the slabs (outer dims unchanged).
# Existing topology only; piecewise-linear maps keep bevel band widths; normals via inverse-transpose of the local map.
import bpy,bmesh,sys,json,numpy as np
from mathutils import Vector,Matrix
src,tag,MOLD=sys.argv[sys.argv.index('--')+1:]; MOLD=int(MOLD)
bpy.ops.wm.open_mainfile(filepath=src)
o=bpy.data.objects['WallCabinet']; me=o.data
uv_before=[tuple(l.uv) for l in me.uv_layers[0].data]; cn=[Vector(c.vector) for c in me.corner_normals]
idx_before=[tuple(p.vertices) for p in me.polygons]
co=np.array([v.co[:] for v in me.vertices]); new=co.copy(); J={}
R=lambda a,b: list(range(a,a+b))
doors={'right':{'frame':R(1402,368),'panes':R(1866,96)+R(1962,96),'rail':R(1770,96),'knob':R(2058,74),'sign':1},
       'left': {'frame':R(672,368),'panes':R(1136,96)+R(1232,96),'rail':R(1040,96),'knob':R(1328,74),'sign':-1}}
# target ratios (uncalibrated reference IMG_3591, see ledger): pane width/door width 0.62; top rail 0.085, bottom rail 0.065, middle rail 0.048 m
DX=(0.332-0.62*0.386)/2
X_OLD=[0.002,0.0044,0.027,0.029,0.361,0.363,0.3856,0.388]
X_NEW=[0.002,0.0044,0.027+DX,0.029+DX,0.361-DX,0.363-DX,0.3856,0.388]
TOP,BOT,MID=0.085,0.065,0.048
zc_mid=(0.3804+0.4222)/2
Z_OLD=[0.081,0.0843,0.1205,0.1237,0.3804,0.4222,0.6805,0.6837,0.7196,0.722]
ib=0.0843+(BOT-0.0034-0.0032)  # inner-bottom band start so that rail face = BOT incl. bevels
it=0.7196-(TOP-0.0034-0.0032)
Z_NEW=[0.081,0.0843,ib,ib+0.0032,zc_mid-MID/2,zc_mid+MID/2,it-0.0032,it,0.7196,0.722]
def pw(v,A,B):
    A=np.array(A);B=np.array(B); v=np.asarray(v,float)
    out=np.interp(v,A,B); return out
def dpw(v,A,B):
    i=np.clip(np.searchsorted(A,v)-1,0,len(A)-2); return (B[i+1]-B[i])/(A[i+1]-A[i])
info={'tag':tag,'DX_m':DX,'targets':{'pane_width_over_door':0.62,'top_rail_m':TOP,'bottom_rail_m':BOT,'mid_rail_m':MID},'X_old':X_OLD,'X_new':X_NEW,'Z_old':Z_OLD,'Z_new':Z_NEW}
for name,d in doors.items():
    s=d['sign']
    for vi in d['frame']+d['panes']+d['rail']:
        x,y,z=co[vi]; ax=s*x
        if vi in d['rail']:   # middle rail: ends follow the new inner stile edges (no protrusion onto the widened stiles)
            RA=[0.025,0.0262,0.3638,0.365]; RB=[0.025+DX,0.0262+DX,0.3638-DX,0.365-DX]
            nx=pw(ax,RA,RB); jx=dpw(ax,np.array(RA),np.array(RB))
        else:
            nx=pw(ax,X_OLD,X_NEW); jx=None
        nz=pw(z,Z_OLD,Z_NEW)
        new[vi,0]=s*nx; new[vi,2]=nz
        J[vi]=Matrix(((jx if jx is not None else dpw(ax,np.array(X_OLD),np.array(X_NEW)),0,0),(0,1,0),(0,0,dpw(z,np.array(Z_OLD),np.array(Z_NEW)))))
    # knob: translate so that it is centred on the widened meeting stile, at the middle rail centre height
    k=co[d['knob']]; kc=k.mean(0)
    tx=s*((0.002+0.029+DX)/2)-kc[0]; tz=zc_mid-kc[2]
    new[d['knob'],0]+=tx; new[d['knob'],2]+=tz
    info[f'knob_{name}_translation_m']=[float(tx),0.0,float(tz)]
if MOLD:
    # inset the two thin strips (top 576.., bottom 480..) so the slabs overhang by a visible step; outer dims unchanged
    for start in (480,576):
        for vi in range(start,start+96):
            x,y,z=co[vi]
            new[vi,0]=x*0.97; new[vi,1]=-0.002+(y+0.002)*0.95
            J[vi]=Matrix(((0.97,0,0),(0,0.95,0),(0,0,1)))
    info['mold_strip_scale_xy']=[0.97,0.95]
for i in J: me.vertices[i].co=new[i]
for i in range(len(co)):
    if i not in J and not np.allclose(new[i],co[i]): me.vertices[i].co=new[i]
me.update()
loops=[]
for p in me.polygons:
    for li in p.loop_indices:
        vi=me.loops[li].vertex_index
        loops.append((J[vi].inverted().transposed()@cn[li]).normalized() if vi in J else cn[li])
me.normals_split_custom_set(loops); me.update()
co2=np.array([v.co[:] for v in me.vertices]); moved=np.where(np.linalg.norm(co2-co,axis=1)>1e-9)[0]
bm=bmesh.new(); bm.from_mesh(me)
from mathutils.bvhtree import BVHTree
def bvh(vs):
    s=set(vs); b=bmesh.new(); vm={}
    bm.faces.ensure_lookup_table()
    for f in bm.faces:
        if f.verts[0].index in s:
            vv=[]
            for v in f.verts:
                if v.index not in vm: vm[v.index]=b.verts.new(v.co)
                vv.append(vm[v.index])
            b.faces.new(vv)
    return BVHTree.FromBMesh(b)
info['rail_frame_overlaps']={n:len(bvh(d['rail']).overlap(bvh(d['frame']))) for n,d in doors.items()}
info['knob_frame_overlaps']={n:len(bvh(d['knob']).overlap(bvh(d['frame']))) for n,d in doors.items()}
info['knob_pane_overlaps']={n:len(bvh(d['knob']).overlap(bvh(d['panes']))) for n,d in doors.items()}
info.update(moved_verts=int(len(moved)),moved_ranges=[int(moved.min()),int(moved.max())] if len(moved) else None,
  dims_before=list(map(float,np.ptp(co,0))),dims_after=list(map(float,np.ptp(co2,0))),min_before=co.min(0).tolist(),min_after=co2.min(0).tolist(),
  uv_identical=uv_before==[tuple(l.uv) for l in me.uv_layers[0].data],index_identical=idx_before==[tuple(p.vertices) for p in me.polygons],
  tris=sum(len(p.vertices)-2 for p in me.polygons),nonmanifold=sum(1 for e in bm.edges if not e.is_manifold),boundary=sum(1 for e in bm.edges if e.is_boundary),
  zero_area=sum(1 for f in bm.faces if f.calc_area()<1e-12),zero_len_normals=sum(1 for c in me.corner_normals if Vector(c.vector).length<1e-6))
np.save(f'c9/cab_{tag}_delta.npy',co2-co)
bpy.ops.wm.save_as_mainfile(filepath=f'c9/cab_{tag}.blend',compress=False)
json.dump(info,open(f'c9/cab_{tag}.json','w'),indent=1); print(json.dumps(info))
