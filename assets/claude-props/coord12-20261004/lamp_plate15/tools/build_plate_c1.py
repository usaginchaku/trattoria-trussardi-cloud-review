# COORD12-LAMP15 C1 (one factor: mounting-plate front size). Input: lamp_support11/revision02 ARM_C1r2 blend (read-only).
# Plate verts 0-95 only: x' = S*x, z' = 0.09 + S*(z-0.09) (plate centre x 0 / z 0.09), y unchanged (thickness, back face Y=0).
# Everything else untouched; topology, order, UV0, material indices unchanged; stored custom normals NOT re-set (decoded plate normals
# follow the deformation within 0.03 deg of the inverse-transpose ideal, see qa). S from qa/plate_reference_measurement.json.
# usage: blender-python build_plate_c1.py -- src.blend out_dir name measurement.json
import bpy,sys,os,json,shutil
import numpy as np
src,out,name,mj=sys.argv[sys.argv.index('--')+1:]; src=os.path.abspath(src); out=os.path.abspath(out)
S=json.load(open(mj))['chosen_uniform_factor']; ZC=0.09
for p in (os.path.join(out,'fbx',name+'.fbx'),os.path.join(out,'models',name+'.blend'),os.path.join(out,'fbx','Shade_ARCH01.png')):
    assert not os.path.exists(p),'refuse to overwrite '+p
bpy.ops.wm.open_mainfile(filepath=src); o=bpy.data.objects['StraightLamp']; me=o.data; assert len(me.vertices)==1406
co=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
pl=co[:96]; assert abs(pl[:,2].min())<1e-6 and abs(pl[:,2].max()-0.18)<1e-6 and abs(pl[:,1].max())<1e-6
new=co.copy(); new[:96,0]=S*co[:96,0]; new[:96,2]=ZC+S*(co[:96,2]-ZC)
me.vertices.foreach_set('co',new.astype(np.float32).ravel()); me.update()
os.makedirs(os.path.join(out,'fbx'),exist_ok=True); os.makedirs(os.path.join(out,'models'),exist_ok=True)
for im in bpy.data.images:
    base=os.path.basename(im.filepath); srcimg=os.path.normpath(os.path.join(os.path.dirname(src),im.filepath[2:]))
    dst=os.path.join(out,'fbx',base); shutil.copyfile(srcimg,dst); im.filepath=dst
for x in list(bpy.data.objects):
    if x is not o: bpy.data.objects.remove(x)
o.select_set(True); bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=os.path.join(out,'fbx',name+'.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=False,mesh_smooth_type='FACE',add_leaf_bones=False,path_mode='RELATIVE')
for sc in bpy.data.scenes: sc.render.filepath='//render/'
for im in bpy.data.images: im.filepath_raw='x'*900; im.filepath_raw='//../fbx/'+os.path.basename(dst)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out,'models',name+'.blend'),compress=True,relative_remap=False)
json.dump({'factor':S,'centre_xz':[0,ZC],'plate_before':{'x':[float(pl[:,0].min()),float(pl[:,0].max())],'z':[float(pl[:,2].min()),float(pl[:,2].max())],'y':[float(pl[:,1].min()),float(pl[:,1].max())]},
  'plate_after':{'x':[float(new[:96,0].min()),float(new[:96,0].max())],'z':[float(new[:96,2].min()),float(new[:96,2].max())],'y':[float(new[:96,1].min()),float(new[:96,1].max())]}},
  open(os.path.join(out,'qa','build_log.json'),'w'),indent=1)
print('BUILD OK',S)
