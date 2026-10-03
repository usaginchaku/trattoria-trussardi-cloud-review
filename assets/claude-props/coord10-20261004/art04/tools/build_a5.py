# COORD10-ART04 A5/A6 on Frame_22.
# A5: widen the wooden (olive) frame inward by SHIFT at its inner edge, keeping outer size .35x.52, depth, origin, axes, mount face.
#     One 1-D piecewise-linear map g(d) on the distance d from the outer edge is applied to x (d=0.175-|x|) and z (d=z or 0.52-z):
#     bevel clusters move rigidly, only the flat spans stretch (frame bands) or shrink (cream rim flat + visible mat strip).
#     Same g on both axes keeps the mitred corners straight. Painting board (8 verts) untouched. Topology/UV unchanged;
#     face directions are unchanged (in-plane stretch / rigid shift), so the source custom normals are re-applied as they are.
# A6 (optional, GROOVES=1): a few shallow V grooves only on the two flat front bands (outer y=-0.036, inner y=-0.031),
#     stopping MARGIN short of each band edge, so no bevel/side/back face is moved.
# args: -- tag outdir texdir shift [grooves(0/1) depth width margin]
import bpy,bmesh,os,sys,json,numpy as np
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]; tag,outdir,texdir,SHIFT=a[0],a[1],a[2],float(a[3])
GROOVES=len(a)>4 and a[4]=='1'
if GROOVES: DEPTH,WID,MARGIN=float(a[5]),float(a[6]),float(a[7])
R=os.environ.get('ART_SRC','src9/assets/codex-source/coord10-art01-20261003')
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=f'{R}/Frame_22_FUR06.fbx')
o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
cn0=[c.vector.copy() for c in me.corner_normals]
HX,HZ=0.175,0.52
# distance levels of the source profile (same for x and z), grouped into clusters wherever the gap between levels is <1.5 mm
co0=np.array([v.co[:] for v in me.vertices])
_d=np.concatenate([HX-np.abs(co0[:,0]),np.minimum(co0[:,2],HZ-co0[:,2])]); PAINT=float(_d[(_d>0.054)&(_d<0.056)].min())  # painting-board edge distance
_l=np.unique(_d[_d<PAINT-1e-6]); C=[[_l[0],_l[0]]]
for x in _l[1:]:
    if x-C[-1][1]<0.0015: C[-1][1]=x
    else: C.append([x,x])
C=[(float(a),float(b)) for a,b in C]; assert len(C)==4,C
F1,F2,F3,F4=C[1][0]-C[0][1],C[2][0]-C[1][1],C[3][0]-C[2][1],PAINT-C[3][1]
s1=(F1+F2+SHIFT)/(F1+F2); s2=(F3+F4-SHIFT)/(F3+F4)
kd=[0,C[0][1],C[1][0],C[1][1],C[2][0],C[2][1],C[3][0],C[3][1],PAINT]
kg=[0,C[0][1]]; kg.append(kg[-1]+F1*s1); kg.append(kg[-1]+(C[1][1]-C[1][0])); kg.append(kg[-1]+F2*s1); kg.append(kg[-1]+(C[2][1]-C[2][0]))
kg.append(kg[-1]+F3*s2); kg.append(kg[-1]+(C[3][1]-C[3][0])); kg.append(kg[-1]+F4*s2)
assert abs(kg[-1]-PAINT)<1e-9 and abs(kg[4]-(C[2][0]+SHIFT))<1e-9
g=lambda d: np.interp(d,kd,kg) if d<PAINT else d
co=np.array([v.co[:] for v in me.vertices])
paint=set(np.where((np.abs(co[:,0])<=0.1198)&(co[:,2]>=0.0552)&(co[:,2]<=0.4648)&(co[:,1]<-0.0244)&(co[:,1]>-0.0256))[0].tolist()); assert len(paint)==8
# sanity: every vertex level with d<PAINT lies inside a cluster or at a flat end (no vertex inside a flat span) -> rigid clusters are well defined
def inside_flat(d): return any(lo+1e-9<d<hi-1e-9 for lo,hi in [(C[0][1],C[1][0]),(C[1][1],C[2][0]),(C[2][1],C[3][0]),(C[3][1],PAINT)])
for i,v in enumerate(me.vertices):
    if i in paint: continue
    x,y,z=v.co
    dx=HX-abs(x); dz=min(z,HZ-z)
    if dx<PAINT: assert not inside_flat(dx),(i,dx); v.co.x=np.sign(x)*(HX-g(dx))
    if dz<PAINT:
        assert not inside_flat(dz),(i,dz); nz=g(dz); v.co.z=nz if z<HZ/2 else HZ-nz
me.update()
# the source is flat-shaded (custom normal = face normal); mark every edge sharp so each corner keeps its own normal (no fan averaging)
for e in me.edges: e.use_edge_sharp=True
me.normals_split_custom_set(cn0); me.update()
info={'tag':tag,'shift_m':SHIFT,'clusters_d':[[round(a,5),round(b,5)] for a,b in C],'knots_d':[round(x,5) for x in kd],'knots_g':[round(x,5) for x in kg],'flat_scale_frame':round(s1,4),'flat_scale_rim_mat':round(s2,4),
      'frame_inner_edge_d':[0.027,round(float(g(0.027)),5)],'rim_inner_edge_d':[C[3][1],round(float(g(C[3][1])),5)],'mat_panel_edge_d':[0.03638,round(float(g(0.03638)),5)],'painting_edge_d':PAINT}
if GROOVES:
    bm=bmesh.new(); bm.from_mesh(me); uvl=bm.loops.layers.uv[0]
    fin=[i for i,m in enumerate(me.materials) if 'Finish' in m.name][0]
    def olive(f):
        u=sum((l[uvl].uv for l in f.loops),Vector((0,0)))/len(f.loops); return f.material_index==fin and int(u.x*4)==2 and int((1-u.y)*4)==0
    def band(f,yb): return olive(f) and f.normal.y<-0.99 and all(abs(v.co.y-yb)<2e-4 for v in f.verts)
    # band extents in d after A5
    BANDS=[(-0.036,kg[1],kg[2]),(-0.031,kg[3],kg[4])]
    side_z=[0.075,0.1675,0.26,0.3525,0.445]; tb_x=[-0.096,-0.048,0.0,0.048,0.096]
    grooves=[('L',t) for t in side_z]+[('R',t) for t in side_z]+[('B',t) for t in tb_x]+[('T',t) for t in tb_x]
    def inbar(f,kind):
        # a face belongs to a bar when all its vertices lie within 0.06 m of that bar's outer edge
        xs=[v.co.x for v in f.verts]; zs=[v.co.z for v in f.verts]
        return {'L':max(xs)<-HX+0.06,'R':min(xs)>HX-0.06,'B':max(zs)<0.06,'T':min(zs)>HZ-0.06}[kind]
    pushed=set()
    for kind,t in grooves:
        ax=2 if kind in 'LR' else 0; ac=0 if ax==2 else 2   # ax: along-bar axis (cut planes normal), ac: across-bar axis
        for yb,d0,d1 in BANDS:
            lo,hi=d0+MARGIN,d1-MARGIN
            for off in (-WID/2,WID/2,0.0):
                fs=[f for f in bm.faces if band(f,yb) and inbar(f,kind)]
                geom=list(set(fs)|{e for f in fs for e in f.edges}|{v for f in fs for v in f.verts})
                n=Vector((0,0,0)); n[ax]=1; p=Vector((0,0,0)); p[ax]=t+off
                bmesh.ops.bisect_plane(bm,geom=geom,plane_co=p,plane_no=n,dist=1e-7)
            # limit the groove across the band: cut the strip between t±WID/2 at the margin lines
            def dacross(v):
                return (HX-abs(v.co.x)) if ac==0 else min(v.co.z,HZ-v.co.z)
            strip=[f for f in bm.faces if band(f,yb) and inbar(f,kind) and all(t-WID/2-1e-6<=v.co[ax]<=t+WID/2+1e-6 for v in f.verts)]
            sgn=-1 if kind in 'LB' else 1
            for dd in (lo,hi):
                geom=list(set(strip)|{e for f in strip for e in f.edges}|{v for f in strip for v in f.verts})
                n=Vector((0,0,0)); n[ac]=1; p=Vector((0,0,0))
                p[ac]=(sgn*(HX-dd)) if ac==0 else (dd if kind=='B' else HZ-dd)
                bmesh.ops.bisect_plane(bm,geom=geom,plane_co=p,plane_no=n,dist=1e-7)
                strip=[f for f in bm.faces if band(f,yb) and inbar(f,kind) and all(t-WID/2-1e-6<=v.co[ax]<=t+WID/2+1e-6 for v in f.verts)]
            for v in bm.verts:
                if abs(v.co[ax]-t)<1e-6 and abs(v.co.y-yb)<2e-4 and lo-1e-6<=dacross(v)<=hi+1e-6 and all(band(f,yb) and all(t-WID/2-1e-6<=u.co[ax]<=t+WID/2+1e-6 for u in f.verts) for f in v.link_faces):
                    pushed.add(v)
    for v in pushed: v.co.y+=DEPTH
    ng=[f for f in bm.faces if len(f.verts)>4 and not any(v in pushed for v in f.verts)]
    bmesh.ops.poke(bm,faces=ng,center_mode='MEAN')
    bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>3],quad_method='BEAUTY',ngon_method='BEAUTY')
    bm.normal_update(); bm.to_mesh(me); me.update()
    lf=[0]*len(me.loops)
    for p in me.polygons:
        for li in p.loop_indices: lf[li]=p.index
    # flat shading like the source: custom normal = face normal (source deviation from face normals <1e-4)
    for e in me.edges: e.use_edge_sharp=True
    me.normals_split_custom_set([me.polygons[lf[i]].normal.copy() for i in range(len(me.loops))]); me.update()
    info.update(grooves={'side_z':side_z,'top_bottom_x':tb_x,'count':len(grooves),'depth_m':DEPTH,'width_m':WID,'margin_m':MARGIN,'bands_y':[-0.036,-0.031],'pushed_vertices':len(pushed),'poked_ngons':len(ng)})
info['verts']=len(me.vertices); info['tris']=len(me.polygons)
os.makedirs(f'{outdir}/fbx',exist_ok=True); os.makedirs(f'{outdir}/models',exist_ok=True)
o.select_set(True); bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=f'{outdir}/fbx/Frame_22_FUR06_{tag}.fbx',use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=False,mesh_smooth_type='FACE',add_leaf_bones=False,path_mode='STRIP')
for m in me.materials:
    if 'Painting' in m.name: m.name='PaintingAtlas_FUR06_A1'; img='PaintingAtlas_FUR06_A1.png'
    else: m.name='FinishAtlas_FUR06_A2_F22'; img='FinishAtlas_FUR06_A2_F22.png'
    for nd in m.node_tree.nodes:
        if nd.type=='TEX_IMAGE': nd.image=bpy.data.images.load(os.path.abspath(f'{texdir}/{img}'))
for im in list(bpy.data.images):
    if im.users==0: bpy.data.images.remove(im)
for im in bpy.data.images:
    b=os.path.basename(im.filepath); im.filepath_raw='x'*1000; im.filepath_raw='//'+os.path.relpath(os.path.abspath(texdir),os.path.abspath(f'{outdir}/models')).replace(os.sep,'/')+'/'+b
for sc in bpy.data.scenes: sc.render.filepath='x'*1000; sc.render.filepath='//render/'
bpy.ops.wm.save_as_mainfile(filepath=f'{outdir}/models/Frame_22_FUR06_{tag}.blend',compress=True,relative_remap=False)
json.dump(info,open(f'{outdir}/build_{tag}.json','w'),indent=1); print('INFO',json.dumps(info))
