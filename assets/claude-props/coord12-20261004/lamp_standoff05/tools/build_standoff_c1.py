# COORD12-LAMP05 C1: Straight L1 - move the cup group (collar shell 2, shade shell 3, diffuser shell 4) by DY toward the room (-Y) and
# extend the connecting arm (shell 1) by moving only its front vertex layer (y <= -0.060) by the same DY. Plate (shell 0) untouched.
# Positions only: topology, vertex/face order, UV0 (ArchitectureUV, incl. negative repeat coords), material indices are not touched.
# Loop normals: the stored custom normals are left as they are (no recompute, no re-set). Translation / stretch along Y does not change any
# face orientation of the moved parts; a re-set via normals_split_custom_set was tried and re-quantized the shade normals (max 4.9e-4),
# so it is not used (qa: max loop-normal difference 1.2e-5).
# usage: blender-python build_standoff_c1.py -- src.blend out_dir name
import bpy,sys,os,json
import numpy as np
src,out,name=sys.argv[sys.argv.index('--')+1:]
DY=-0.050
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(src))
o=bpy.data.objects['StraightLamp']; me=o.data
co=np.empty(len(me.vertices)*3,np.float32); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
ln=np.empty(len(me.loops)*3,np.float32); me.corner_normals.foreach_get('vector',ln); ln=ln.reshape(-1,3)
# shells by contiguous index ranges (verified: 0-95 plate, 96-191 arm, 192-313 collar, 314-1019 shade, 1020-1165 diffuser)
R={'plate':(0,96),'arm':(96,192),'collar':(192,314),'shade':(314,1020),'diffuser':(1020,1166)}
assert len(co)==1166
new=co.copy()
for k in ('collar','shade','diffuser'): a,b=R[k]; new[a:b,1]+=DY
a,b=R['arm']; front=np.where(co[a:b,1]<=-0.060)[0]+a; back=np.where(co[a:b,1]>=-0.020)[0]+a
assert len(front)+len(back)==96 and len(front)==48
new[front,1]+=DY
me.vertices.foreach_set('co',new.ravel()); me.update()
os.makedirs(os.path.join(out,'fbx'),exist_ok=True); os.makedirs(os.path.join(out,'models'),exist_ok=True)
# required image: byte copy of the input Shade_ARCH01.png beside the FBX, blend keeps '//../fbx/Shade_ARCH01.png'
import shutil
for im in bpy.data.images:
    base=os.path.basename(im.filepath); srcimg=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(src)),im.filepath[2:]))
    dst=os.path.join(os.path.abspath(out),'fbx',base); shutil.copyfile(srcimg,dst); im.filepath=dst
for x in list(bpy.data.objects):
    if x is not o: bpy.data.objects.remove(x)
o.select_set(True); bpy.context.view_layer.objects.active=o
# same export call as the input's exporter (coord09 furniture/qa/exp_furn.py)
bpy.ops.export_scene.fbx(filepath=os.path.join(os.path.abspath(out),'fbx',name+'.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=False,mesh_smooth_type='FACE',add_leaf_bones=False,path_mode='RELATIVE')
for sc in bpy.data.scenes: sc.render.filepath='//render/'
for im in bpy.data.images: im.filepath_raw='x'*900; im.filepath_raw='//../fbx/'+os.path.basename(dst)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.abspath(out),'models',name+'.blend'),compress=True,relative_remap=False)
json.dump({'DY_m':DY,'moved_shells':['collar','shade','diffuser'],'arm_front_vertices_moved':len(front),'arm_back_vertices_kept':len(back),
  'plate_vertices_kept':96},open(os.path.join(out,'qa','build_log.json'),'w'),indent=1)
print('BUILD OK')
