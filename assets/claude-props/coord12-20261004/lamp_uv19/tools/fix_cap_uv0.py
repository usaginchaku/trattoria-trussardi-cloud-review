# COORD12-LAMP19: UV0 end-cap repair only. For the 28 cap triangles (top ring 1070-1085: z constant; wall ring 1390-1405: y constant)
# keep U (= x) and set V to the in-plane coordinate the old tool dropped: top cap V = y, wall cap V = z. Nothing else is touched
# (positions, topology, corner order, materials, custom normals, all other UVs). Saved as new files; existing paths are refused.
# usage: blender-python fix_cap_uv0.py -- src.blend out_dir name
import bpy,sys,os,json,shutil
src,out,name=sys.argv[sys.argv.index('--')+1:]; src=os.path.abspath(src); out=os.path.abspath(out)
for p in (os.path.join(out,'fbx',name+'.fbx'),os.path.join(out,'models',name+'.blend'),os.path.join(out,'fbx','Shade_ARCH01.png')):
    assert not os.path.exists(p),'refuse to overwrite '+p
bpy.ops.wm.open_mainfile(filepath=src); o=bpy.data.objects['StraightLamp']; me=o.data; uv=me.uv_layers['ArchitectureUV'].data
assert len(me.vertices)==1406 and len(me.polygons)==2792 and me.uv_layers[0].name=='ArchitectureUV'
TOP=set(range(1070,1086)); WALL=set(range(1390,1406)); changed=[]
for f in me.polygons:
    vs=set(f.vertices)
    if vs<=TOP or vs<=WALL:
        for li in f.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co; old=tuple(uv[li].uv)
            uv[li].uv=(old[0], v.y if vs<=TOP else v.z)
            changed.append({'face':f.index,'corner':li,'vertex':me.loops[li].vertex_index,'cap':'top' if vs<=TOP else 'wall','uv_old':list(old),'uv_new':list(uv[li].uv)})
assert len(changed)==84
os.makedirs(os.path.join(out,'fbx'),exist_ok=True); os.makedirs(os.path.join(out,'models'),exist_ok=True); os.makedirs(os.path.join(out,'qa'),exist_ok=True)
for im in bpy.data.images:
    base=os.path.basename(im.filepath); srcimg=os.path.normpath(os.path.join(os.path.dirname(src),im.filepath[2:]))
    dst=os.path.join(out,'fbx',base); shutil.copyfile(srcimg,dst); im.filepath=dst
o.select_set(True); bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=os.path.join(out,'fbx',name+'.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=False,mesh_smooth_type='FACE',add_leaf_bones=False,path_mode='RELATIVE')
for sc in bpy.data.scenes: sc.render.filepath='//render/'
for im in bpy.data.images: im.filepath_raw='x'*900; im.filepath_raw='//../fbx/'+os.path.basename(dst)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out,'models',name+'.blend'),compress=True,relative_remap=False)
json.dump({'source':os.path.basename(src),'changed_corners':changed},open(os.path.join(out,'qa','changed_corners.json'),'w'),indent=1)
print('FIX OK',len(changed))
