# COORD10-CAB04 C4: stepped crown (3 horizontal tiers) inside the existing C3m top band (z 0.7182-0.80, within the top plate's x/y extent).
#  tier1 cap   = existing top plate box (verts 384-479): bottom raised 0.74 -> 0.7779, x/y unchanged (+-0.44, front -0.28)
#  tier2 middle= NEW: duplicate of the top-plate box (same topology/UV/normals), z 0.7462-0.7784, x +-0.4374, front -0.2771, back 0
#  tier3 lower = existing mould box (verts 576-671): x +-0.4181 -> +-0.4336, front -0.268 -> -0.2728, top 0.7395 -> 0.7467, bottom 0.7182 kept
# Overhang ratios cap:middle:lower = 25:21:15 and tier heights 16:24:22 px from the IMG_3591 left silhouette.
# Boxes are reshaped by moving each end's bevel cluster rigidly (flat spans stretch), so every face keeps its direction;
# custom normals are re-applied unchanged (new tier copies the top-plate loop normals). Overall size, origin, axes, mount face (y=0),
# doors/panes/knobs/base moulding, UV and all original indices are untouched; new verts are appended (2132..2227).
import bpy,bmesh,os,sys,json,numpy as np
a=sys.argv[sys.argv.index('--')+1:]; src,outdir,tag=a[0],a[1],a[2]; IDENT=len(a)>3 and a[3]=='identity'
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=src)
o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
nv0,nf0,nl0=len(me.vertices),len(me.polygons),len(me.loops)
cn0=[c.vector.copy() for c in me.corner_normals]
faces0=[list(p.vertices) for p in me.polygons]
TOP=list(range(384,480)); MOULD=list(range(576,672))
info={'tag':tag,'source_verts':nv0,'source_tris':nf0}
if not IDENT:
    co=np.array([v.co[:] for v in me.vertices])
    assert np.allclose(co[TOP].min(0),[-0.44,-0.28,0.74],atol=2e-4) and np.allclose(co[TOP].max(0),[0.44,0.0,0.80],atol=2e-4)
    assert np.allclose(co[MOULD].min(0),[-0.4181,-0.268,0.7182],atol=2e-4) and np.allclose(co[MOULD].max(0),[0.4181,-0.002,0.7395],atol=2e-4)
    # loop normals keyed by (face, vertex) so the duplicated tier can copy them
    lnorm={}
    for p in me.polygons:
        for li in p.loop_indices: lnorm[(p.index,me.loops[li].vertex_index)]=cn0[li]
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    topfaces=[f for f in bm.faces if all(v.index in set(TOP) for v in f.verts)]
    src_face_index={f:f.index for f in topfaces}
    dup=bmesh.ops.duplicate(bm,geom=topfaces+list({e for f in topfaces for e in f.edges})+[bm.verts[i] for i in TOP])
    vmap=dup['vert_map']; fmap=dup['face_map']; bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    newverts=[vmap[bm.verts[i]] for i in TOP]
    def reshape(verts,old_lo,old_hi,new_lo,new_hi):
        # per axis: vertices in the lower half move with the low end, upper half with the high end (bevels stay rigid)
        for v in verts:
            c=list(v.co)
            for ax in range(3):
                mid=(old_lo[ax]+old_hi[ax])/2
                c[ax]= c[ax]-old_lo[ax]+new_lo[ax] if c[ax]<mid else c[ax]-old_hi[ax]+new_hi[ax]
            v.co=c
    tp=[bm.verts[i] for i in TOP]; md=[bm.verts[i] for i in MOULD]
    T=dict(cap=(( -0.44,-0.28,0.7779),(0.44,0.0,0.80)), mid=((-0.4374,-0.2771,0.7462),(0.4374,0.0,0.7784)), low=((-0.4336,-0.2728,0.7182),(0.4336,-0.002,0.7467)))
    reshape(newverts,(-0.44,-0.28,0.74),(0.44,0.0,0.80),*T['mid'])
    reshape(tp,(-0.44,-0.28,0.74),(0.44,0.0,0.80),*T['cap'])
    reshape(md,(-0.4181,-0.268,0.7182),(0.4181,-0.002,0.7395),*T['low'])
    # bevel widths must stay smaller than the new half extents (no inverted bevels)
    for name,vs in (('cap',tp),('mid',newverts),('low',md)):
        P=np.array([v.co[:] for v in vs]); assert (np.ptp(P,0)>0.01).all(),name
    newfaces={fmap[f]:src_face_index[f] for f in topfaces}
    bm.to_mesh(me); me.update()
    assert [list(p.vertices) for p in me.polygons[:nf0]]==faces0, 'original faces/indices must stay first and unchanged'
    # custom normals: original loops keep cn0; new loops copy the source top-plate loop normals
    newv2old={vmap[bm.verts[i]].index:i for i in TOP}
    srcface_of_new={}
    for nf,sf in newfaces.items(): srcface_of_new[nf.index]=sf
    out=[]
    for p in me.polygons:
        for li in p.loop_indices:
            if li<nl0: out.append(cn0[li])
            else: out.append(lnorm[(srcface_of_new[p.index],newv2old[me.loops[li].vertex_index])])
    for e in me.edges: e.use_edge_sharp=True
    me.normals_split_custom_set(out); me.update()
    info.update(tiers={k:{'min':list(v[0]),'max':list(v[1])} for k,v in T.items()},new_verts=[nv0,len(me.vertices)-1],new_vertex_from_top_plate={str(k):v for k,v in sorted(newv2old.items())},
                tris=len(me.polygons),added_tris=len(me.polygons)-nf0,moved_original_verts={'top_plate_cap':[384,479],'mould_lower_tier':[576,671]})
else:
    for e in me.edges: e.use_edge_sharp=True
    me.normals_split_custom_set(cn0); me.update(); info['identity']=True
os.makedirs(f'{outdir}/fbx',exist_ok=True); os.makedirs(f'{outdir}/models',exist_ok=True)
o.select_set(True); bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=f'{outdir}/fbx/WallCabinet_FUR06.fbx',use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=False,mesh_smooth_type='FACE',add_leaf_bones=False,path_mode='STRIP')
for im in bpy.data.images:
    b=os.path.basename(im.filepath.replace('\\','/')); im.filepath_raw='x'*1000; im.filepath_raw='//../fbx/'+b
for sc in bpy.data.scenes: sc.render.filepath='x'*1000; sc.render.filepath='//render/'
bpy.ops.wm.save_as_mainfile(filepath=f'{outdir}/models/WallCabinet_FUR06.blend',compress=True,relative_remap=False)
json.dump(info,open(f'{outdir}/build_{tag}.json','w'),indent=1); print('INFO',json.dumps({k:v for k,v in info.items() if k!='new_vertex_from_top_plate'}))
