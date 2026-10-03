# COORD09 MENU02: menu stand tripod foot-only candidate.
# Selection (deterministic): the three 372-vertex Timber islands with min z < 0.01 and max z < 0.3 (swept feet; each = 31 rings x 12 verts, contiguous indices).
# Transform: per ring j (u = arc-length fraction from post joint 0 -> tip 1), centre horizontal offset from post axis scaled by s(u)=1-(1-S_TIP)*u**P, z of centre kept;
#            ring vertices moved rigidly: translated with the centre and rotated by the minimal rotation old tangent -> new tangent. Normals rotated identically.
# Everything else (post, board, lettering, UV, all non-foot normals) untouched.
import bpy,bmesh,sys,json,math,numpy as np
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
src,S_TIP,P,tag=sys.argv[sys.argv.index('--')+1:]; S_TIP=float(S_TIP); P=float(P)
YAW=math.degrees(2*math.asin(0.06975647062063217))  # parent yaw about Unity Y (deg)
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=src)
o=bpy.data.objects['MenuStand']; me=o.data
uv_before=[tuple(l.uv) for l in me.uv_layers[0].data]; cn=[Vector(c.vector) for c in me.corner_normals]
co=np.array([v.co[:] for v in me.vertices])
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
seen=set(); isl=[]
for v in bm.verts:
    if v.index in seen: continue
    st=[v]; c=[]
    while st:
        x=st.pop()
        if x.index in seen: continue
        seen.add(x.index); c.append(x.index); st+=[e.other_vert(x) for e in x.link_edges]
    isl.append(sorted(c))
feet=[c for c in isl if len(c)==372 and co[c,2].min()<0.01 and co[c,2].max()<0.3]
assert len(feet)==3
post=[c for c in isl if len(c)==338][0]
ax=co[post][:,:2].mean(0)   # post axis (x,y)
def world_x(p):  # relative world X (design m) of local points, yaw about Unity Y; Unity x=Bx, Unity z=By
    t=math.radians(YAW); return np.cos(t)*p[:,0]+np.sin(t)*p[:,1]
def footprint(C,feet_idx):
    zmin=C[feet_idx,2].min(); m=[i for i in feet_idx if C[i,2]<=zmin+0.002]
    return float(np.ptp(world_x(C[m]))),m
allfeet=[i for c in feet for i in c]
fp0,_=footprint(co,allfeet)
new=co.copy(); Rv={}
legs=[]
for c in feet:
    R=co[c].reshape(31,12,3); cen=R.mean(1)
    rr=np.linalg.norm(cen[:,:2]-ax,axis=1)
    if rr[0]>rr[-1]: order=list(range(30,-1,-1))
    else: order=list(range(31))
    cen_o=cen[order]; seg=np.linalg.norm(np.diff(cen_o,axis=0),axis=1); u=np.r_[0,np.cumsum(seg)]/seg.sum()
    s=1-(1-S_TIP)*u**P
    newc=cen_o.copy(); newc[:,:2]=ax+(cen_o[:,:2]-ax)*s[:,None]
    def tang(C):
        T=np.gradient(C,axis=0); return T/np.linalg.norm(T,axis=1)[:,None]
    T0,T1=tang(cen_o),tang(newc)
    for k,j in enumerate(order):
        a=Vector(T0[k]); b=Vector(T1[k]); rot=a.rotation_difference(b).to_matrix()
        for m in range(12):
            vi=c[j*12+m]; p=Vector(co[vi])-Vector(cen_o[k])
            new[vi]=np.array(rot@p)+newc[k]; Rv[vi]=rot
    legs.append({'joint_ring_radius_m':float(rr[order[0]]),'tip_ring_radius_before_m':float(rr[order[-1]]),'tip_ring_radius_after_m':float(np.linalg.norm(newc[-1,:2]-ax))})
# re-level: keep each leg's lowest point at its original z (rings rotate slightly) -> vertical correction blended toward tip (u^4)
lev=[]
for c,L in zip(feet,legs):
    dz=co[c,2].min()-new[c,2].min()
    R=co[c].reshape(31,12,3); cen=R.mean(1); rr=np.linalg.norm(cen[:,:2]-ax,axis=1)
    order=list(range(30,-1,-1)) if rr[0]>rr[-1] else list(range(31))
    seg=np.linalg.norm(np.diff(cen[order],axis=0),axis=1); u=np.r_[0,np.cumsum(seg)]/seg.sum()
    for k,j in enumerate(order):
        for m in range(12): new[c[j*12+m],2]+=dz*u[k]**4
    lev.append(float(dz))
for i in Rv: me.vertices[i].co=new[i]
me.update()
loops=[]
for p in me.polygons:
    for li in p.loop_indices:
        vi=me.loops[li].vertex_index
        loops.append((Rv[vi]@cn[li]).normalized() if vi in Rv else cn[li])
me.normals_split_custom_set(loops); me.update()
co2=np.array([v.co[:] for v in me.vertices])
fp1,mlow=footprint(co2,allfeet)
nonfoot=sorted(set(range(len(co)))-set(allfeet))
cn2=[Vector(c.vector) for c in me.corner_normals]
nf_loops=[li for p in me.polygons for li in p.loop_indices if me.loops[li].vertex_index not in Rv]
bm2=bmesh.new(); bm2.from_mesh(me); bm2.faces.ensure_lookup_table()
def bvh(vs):
    s=set(vs); b=bmesh.new(); vm={}
    for f in bm2.faces:
        if f.verts[0].index in s:
            vv=[]
            for v in f.verts:
                if v.index not in vm: vm[v.index]=b.verts.new(v.co)
                vv.append(vm[v.index])
            b.faces.new(vv)
    return BVHTree.FromBMesh(b)
def bvh0(vs):
    s=set(vs); b=bmesh.new(); vm={}
    for f in bm.faces:
        if f.verts[0].index in s:
            vv=[]
            for v in f.verts:
                if v.index not in vm: vm[v.index]=b.verts.new(Vector(co[v.index]))
                vv.append(vm[v.index])
            b.faces.new(vv)
    return BVHTree.FromBMesh(b)
bm.faces.ensure_lookup_table()
ov_before={'leg_post':[len(bvh0(c).overlap(bvh0(post))) for c in feet],'leg_leg':[len(bvh0(a).overlap(bvh0(b))) for i,a in enumerate(feet) for b in feet[i+1:]]}
ov_after={'leg_post':[len(bvh(c).overlap(bvh(post))) for c in feet],'leg_leg':[len(bvh(a).overlap(bvh(b))) for i,a in enumerate(feet) for b in feet[i+1:]]}
tips=[]
for c in feet:
    z=co2[c,2]; tips.append({'min_z_before':float(co[c,2].min()),'min_z_after':float(z.min())})
info={'tag':tag,'S_TIP':S_TIP,'P':P,'parent_yaw_deg':YAW,'post_axis_xy':ax.tolist(),'selection':'3 Timber islands of 372 verts (31 rings x 12), min z<0.01, max z<0.3',
 'foot_vertex_index_ranges':[[c[0],c[-1]] for c in feet],'footprint_worldX_lowest2mm_before_m':fp0,'footprint_worldX_lowest2mm_after_m':fp1,
 'footprint_world_scaled_after_m':fp1*0.7825509309768677,'legs':legs,'tip_relevel_dz_m':lev,'tips':tips,
 'tip_contact_plane_spread_m':float(max(t['min_z_after'] for t in tips)-min(t['min_z_after'] for t in tips)),
 'nonfoot_verts':len(nonfoot),'nonfoot_positions_identical':bool(np.array_equal(co2[nonfoot],co[nonfoot])),
 'nonfoot_corner_normals_max_dev':float(max((cn2[li]-cn[li]).length for li in nf_loops)),
 'uv_identical':uv_before==[tuple(l.uv) for l in me.uv_layers[0].data],
 'dims_before':list(map(float,np.ptp(co,0))),'dims_after':list(map(float,np.ptp(co2,0))),'zmin_after':float(co2[:,2].min()),'zmax_after':float(co2[:,2].max()),
 'triangle_overlaps_before':ov_before,'triangle_overlaps_after':ov_after,'tris':sum(len(p.vertices)-2 for p in me.polygons),
 'nonmanifold':sum(1 for e in bm2.edges if not e.is_manifold),'boundary':sum(1 for e in bm2.edges if e.is_boundary),'zero_area':sum(1 for f in bm2.faces if f.calc_area()<1e-12),
 'zero_len_normals':sum(1 for n in cn2 if n.length<1e-6)}
np.save(f'c9/menu_{tag}_delta.npy',co2-co)
bpy.ops.wm.save_as_mainfile(filepath=f'c9/menu_{tag}.blend',compress=False)
json.dump(info,open(f'c9/menu_{tag}.json','w'),indent=1); print(json.dumps(info))
