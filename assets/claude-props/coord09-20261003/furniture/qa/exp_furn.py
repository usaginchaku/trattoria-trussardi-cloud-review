# furniture export: FBX_SCALE_UNITS reproduces the Codex source convention (UnitScaleFactor 100, model Lcl Scaling 1, Lcl Rotation -90 X)
import bpy,os,sys,shutil
blend,objname,outdir,fbxname,texsrc=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=blend)
o=bpy.data.objects[objname]
for x in list(bpy.data.objects):
    if x is not o: bpy.data.objects.remove(x)
os.makedirs(outdir+'/fbx',exist_ok=True); os.makedirs(outdir+'/models',exist_ok=True)
for im in bpy.data.images:
    if not im.filepath: continue
    base=os.path.basename(im.filepath); dst=os.path.join(outdir,'fbx',base)
    shutil.copyfile(os.path.join(texsrc,base),dst); im.filepath=dst
o.select_set(True); bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=f'{outdir}/fbx/{fbxname}.fbx',use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=False,mesh_smooth_type='FACE',add_leaf_bones=False,path_mode='RELATIVE')
for sc in bpy.data.scenes: sc.render.filepath='//render/'
for im in bpy.data.images:
    if im.filepath: im.filepath_raw='//../fbx/'+os.path.basename(im.filepath)
bpy.ops.wm.save_as_mainfile(filepath=f'{outdir}/models/{fbxname}.blend',compress=True,relative_remap=False)
print('OK',fbxname)
