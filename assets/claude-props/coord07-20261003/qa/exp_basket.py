import bpy,os,sys
blend,objname,outdir,fbxname=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=blend)
o=bpy.data.objects[objname]
for x in list(bpy.data.objects):
    if x is not o: bpy.data.objects.remove(x)
o.location=(0,0,0)
os.makedirs(outdir+'/models',exist_ok=True)
sub='/fbx/LOD1' if 'LOD1' in objname else '/fbx'
fbm=outdir+sub+'/'+fbxname+'.fbm'; os.makedirs(fbm,exist_ok=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=outdir+'/models/'+fbxname+'.blend',compress=True)
for im in bpy.data.images:
    base=os.path.basename(im.filepath) or im.name
    if base.startswith('Trussardi_Atlas'):
        if im.packed_file: im.unpack(method='REMOVE')
        im.filepath=fbm+'/'+base
o.select_set(True); bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=outdir+sub+'/'+fbxname+'.fbx',use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',bake_space_transform=False,mesh_smooth_type='FACE',add_leaf_bones=False,path_mode='RELATIVE')
print('OK',fbxname)
