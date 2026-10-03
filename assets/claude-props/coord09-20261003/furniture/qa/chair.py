# COORD09 dining chair candidates (Codex source FUR01). One factor per candidate; UV untouched; seat height/legs/footprint untouched.
#  C0: identity through the same pipeline
#  C1: back divisions -> 4 existing rails enlarged along the back plane into wide boards separated by narrow grooves (topology unchanged)
#  C2: crest notch shape -> rounded U dip reshaped into a sharp V (same width & depth) on frame + inset panel top
import bpy,bmesh,sys,json,math,numpy as np
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
src,mode,tag=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=src)
o=bpy.data.objects['DiningChair']; me=o.data
uv_before=[tuple(l.uv) for l in me.uv_layers[0].data]
cn=[Vector(c.vector) for c in me.corner_normals]
co0=np.array([v.co[:] for v in me.vertices])
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
seen=set(); isl=[]
for v in bm.verts:
    if v.index in seen: continue
    st=[v]; c=[]
    while st:
        x=st.pop()
        if x.index in seen: continue
        seen.add(x.index); c.append(x.index); st+=[e.other_vert(x) for e in x.link_edges]
    isl.append(c)
bm.free()
byz=sorted(isl,key=lambda c:-co0[c,2].max())
frame,inset=byz[0],byz[1]
rails=sorted([c for c in isl if len(c)==464],key=lambda c:co0[c,2].mean())
info={'mode':mode}
vmap={}   # vertex -> 3x3 linear part for normal transform
newco=co0.copy()
if mode=='C1':
    cen=np.array([co0[c].mean(0) for c in rails])
    # back-plane up axis from rail centres (y,z)
    A=np.polyfit(cen[:,2],cen[:,1],1); u=np.array([0,A[0],1.0]); u/=np.linalg.norm(u)
    ZLO,ZHI,GROOVE=0.470,0.900,0.008
    H=(ZHI-ZLO-3*GROOVE)/4
    info.update(back_axis=u.tolist(),board_height_along_axis_m=H,groove_m=GROOVE,span_z=[ZLO,ZHI],rail_height_before_m=[float(np.ptp(co0[c]@u)) for c in rails])
    for k,c in enumerate(rails):
        p=co0[c]; t=p@u; h0=np.ptp(t); c0=(t.max()+t.min())/2
        s=H/h0; tc=ZLO/u[2]+ (k*(H+GROOVE)+H/2)/1.0  # target centre along u (approx: use z-param)
        # target centre in z, converted to along-axis offset at the rail's current centre
        zc_target=ZLO+k*(H+GROOVE)+H/2
        d_along=(zc_target-p[:,2].mean())/u[2]
        newp=p+np.outer((t-c0)*(s-1),u)+np.outer(np.full(len(p),d_along),u)
        newco[c]=newp
        S=np.eye(3)+(s-1)*np.outer(u,u)
        for vi in c: vmap[vi]=S
    info['rail_scale']=[float(H/np.ptp(co0[c]@u)) for c in rails]
elif mode=='C2':
    # current dip: top profile of frame; reshape top region near x=0: z' = z - (Ucurve(x) - Vcurve(x)) * w(z)
    p=co0[frame]
    def topz(x0): m=np.abs(p[:,0]-x0)<0.006; return p[m,2].max()
    zmax=max(topz(x) for x in np.linspace(-0.2,0.2,41)); z0=topz(0.0); half=0.09
    xs=np.linspace(0,half,30); U=np.array([topz(x) for x in xs])        # rounded dip (measured)
    V=z0+(zmax-z0)*np.clip(xs/half,0,1)                                   # straight V sides, same bottom & width
    # keep shoulders: blend only inside |x|<half
    def delta(x): return np.interp(np.abs(x),xs,V-U,right=0.0)            # <=0 means lower
    ZW0=0.90  # below this height nothing moves
    targets=frame+inset
    for vi in targets:
        x,y,z=co0[vi]
        if z<=ZW0 or abs(x)>=half: continue
        w=min(1,(z-ZW0)/(z0-0.03-ZW0)) if z< z0-0.03 else 1.0
        newco[vi,2]=z+delta(x)*w
    info.update(dip_width_half_m=half,dip_bottom_z=float(z0),shoulder_z=float(zmax),depth_m=float(zmax-z0),moved_below_z=ZW0)
moved=np.where(np.linalg.norm(newco-co0,axis=1)>1e-9)[0]
for vi in moved: me.vertices[vi].co=newco[vi]
me.update()
# normals: rails (C1) get exact affine normal transform; C2 moved verts get recomputed default normals for faces touching them; others keep stored normals
if mode in('C1','C2'):
    tmp=me.copy(); tmp.normals_split_custom_set([(0,0,0)]*len(tmp.loops)); dn=[Vector(c.vector) for c in tmp.corner_normals]; bpy.data.meshes.remove(tmp)
    mv=set(moved.tolist()); loops=[]
    for p_ in me.polygons:
        touch=any(v in mv for v in p_.vertices)
        for li in p_.loop_indices:
            vi=me.loops[li].vertex_index
            if mode=='C1' and vi in vmap:
                S=Matrix(vmap[vi].tolist()); loops.append((S.inverted().transposed()@cn[li]).normalized())
            elif mode=='C2' and touch: loops.append(dn[li])
            else: loops.append(cn[li])
    me.normals_split_custom_set(loops); me.update()
# checks
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
def bvh(vs):
    s=set(vs); b=bmesh.new(); vm={}
    for f in bm.faces:
        if f.verts[0].index in s:
            vv=[]
            for v in f.verts:
                if v.index not in vm: vm[v.index]=b.verts.new(v.co)
                vv.append(vm[v.index])
            b.faces.new(vv)
    return BVHTree.FromBMesh(b)
railv=[v for c in rails for v in c]
info['rail_frame_tri_overlaps']=len(bvh(railv).overlap(bvh(frame)))
info['rail_rail_overlaps']=sum(len(bvh(a).overlap(bvh(b))) for i,a in enumerate(rails) for b in rails[i+1:])
co1=np.array([v.co[:] for v in me.vertices]); cna=[Vector(c.vector) for c in me.corner_normals]
info.update(verts_moved=len(moved),dims_before=list(map(float,np.ptp(co0,0))),dims_after=list(map(float,np.ptp(co1,0))),zmin=float(co1[:,2].min()),
  seat_top_z=float(co1[[v for c in isl if len(c)==180 for v in c],2].max()),tris=sum(len(p.vertices)-2 for p in me.polygons),
  uv_unchanged=uv_before==[tuple(l.uv) for l in me.uv_layers[0].data],nonmanifold=sum(1 for e in bm.edges if not e.is_manifold),
  boundary=sum(1 for e in bm.edges if e.is_boundary),zero_area=sum(1 for f in bm.faces if f.calc_area()<1e-12),zero_len_normals=sum(1 for n in cna if n.length<1e-6))
bpy.ops.wm.save_as_mainfile(filepath=f'c9/chair_{tag}.blend',compress=False)
json.dump(info,open(f'c9/chair_{tag}.json','w'),indent=1); print(json.dumps(info))
