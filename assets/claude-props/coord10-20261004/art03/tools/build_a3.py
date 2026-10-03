# COORD10-ART03 A3: Frame_23 painting board scaled down about its own centre (mat = existing backing panel becomes wider).
# Only the 8 vertices of the free-standing painting box move; UV, topology, face normals and custom normals are kept.
# args: -- tag scale outdir texdir
import bpy,os,sys,json,numpy as np
tag,s,outdir,texdir=sys.argv[sys.argv.index('--')+1:]; s=float(s)
R=os.environ.get('ART_SRC','src9/assets/codex-source/coord10-art01-20261003')
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=f'{R}/Frame_23_FUR06.fbx')
o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
cn0=[c.vector.copy() for c in me.corner_normals]
co=np.array([v.co[:] for v in me.vertices])
inn=np.where((np.abs(co[:,0])<=0.1371)&(co[:,2]>=0.0629)&(co[:,2]<=0.4171))[0]
assert len(inn)==8, len(inn)
pf=[p.index for p in me.polygons if any(v in set(inn.tolist()) for v in p.vertices)]
assert len(pf)==12 and all('Painting' in me.materials[me.polygons[i].material_index].name for i in pf)
assert all(set(me.polygons[i].vertices)<=set(inn.tolist()) for i in pf)   # painting box is a separate shell
zc=(co[inn,2].min()+co[inn,2].max())/2; xc=(co[inn,0].min()+co[inn,0].max())/2
for i in inn:
    v=me.vertices[i]; v.co.x=xc+(v.co.x-xc)*s; v.co.z=zc+(v.co.z-zc)*s
me.update(); me.normals_split_custom_set(cn0); me.update()
co1=np.array([v.co[:] for v in me.vertices])
info={'tag':tag,'scale':s,'moved_vertices':inn.tolist(),'painting_faces':pf,'centre_xz':[float(xc),float(zc)],
      'painting_before_m':[float(np.ptp(co[inn,0])),float(np.ptp(co[inn,2]))],'painting_after_m':[float(np.ptp(co1[inn,0])),float(np.ptp(co1[inn,2]))],
      'painting_y_unchanged':bool(np.allclose(co[:,1],co1[:,1])),'other_verts_moved':int((np.linalg.norm(co1-co,axis=1)>0)[np.setdiff1d(np.arange(len(co)),inn)].sum())}
os.makedirs(f'{outdir}/fbx',exist_ok=True); os.makedirs(f'{outdir}/models',exist_ok=True)
o.select_set(True); bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=f'{outdir}/fbx/Frame_23_FUR06_{tag}.fbx',use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=False,mesh_smooth_type='FACE',add_leaf_bones=False,path_mode='STRIP')
# editable blend: candidate-dedicated materials pointing at the ART01 A1/A2 textures copied into art03/textures (relative //../../../textures/)
for m in me.materials:
    if 'Painting' in m.name: m.name='PaintingAtlas_FUR06_A1'; img='PaintingAtlas_FUR06_A1.png'
    else: m.name='FinishAtlas_FUR06_A2_F23'; img='FinishAtlas_FUR06_A2_F23.png'
    for nd in m.node_tree.nodes:
        if nd.type=='TEX_IMAGE':
            im=bpy.data.images.load(os.path.abspath(f'{texdir}/{img}')); nd.image=im
for im in list(bpy.data.images):
    if im.users==0: bpy.data.images.remove(im)
for im in bpy.data.images:
    b=os.path.basename(im.filepath); im.filepath_raw='x'*1000; im.filepath_raw='//../../../textures/'+b
for sc in bpy.data.scenes: sc.render.filepath='x'*1000; sc.render.filepath='//render/'
bpy.ops.wm.save_as_mainfile(filepath=f'{outdir}/models/Frame_23_FUR06_{tag}.blend',compress=True,relative_remap=False)
json.dump(info,open(f'{outdir}/build_{tag}.json','w'),indent=1); print('INFO',json.dumps(info))
