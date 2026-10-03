# menu stand export: source convention (FBX_SCALE_UNITS: UnitScaleFactor 100, model Lcl Scaling 1); texture refs written as bare file names (STRIP) like the source's relative names
import bpy,os,sys
blend,outdir,name=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=blend)
o=bpy.data.objects['MenuStand']
for x in list(bpy.data.objects):
    if x is not o: bpy.data.objects.remove(x)
os.makedirs(outdir+'/fbx',exist_ok=True); os.makedirs(outdir+'/models',exist_ok=True)
o.select_set(True); bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=f'{outdir}/fbx/{name}.fbx',use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=False,mesh_smooth_type='FACE',add_leaf_bones=False,path_mode='STRIP')
for sc in bpy.data.scenes: sc.render.filepath='x'*1000; sc.render.filepath='//render/'
for im in bpy.data.images:
    if im.filepath: b=os.path.basename(im.filepath.replace('\\','/')); im.filepath_raw='x'*1000; im.filepath_raw='//'+b
bpy.ops.wm.save_as_mainfile(filepath=f'{outdir}/models/{name}.blend',compress=True,relative_remap=False)
print('OK')
