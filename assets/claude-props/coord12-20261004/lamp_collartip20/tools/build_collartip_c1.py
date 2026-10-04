# COORD12-LAMP20 C1 (one factor: lower collar taper). Input: lamp_uv19/B_UVFIX (read-only).
# Only the collar's bottom ring (verts at z 0.145, 40 ring verts + centre) is scaled in XY about the collar axis (x 0, y collar centre):
# radius 0.036 -> R_B. Rings at z 0.18 (visible top, 0.369 Ws) and z 0.19 (hidden flange), the collar height and Z positions are unchanged.
# R_B = 0.0235 m: inside the reference band at f 0.25-0.5 (qa/collar_taper_compare.json) and >= arm corner radius 0.0202 m + 3.3 mm,
# so the J-arm still enters through the collar bottom (the narrower reference f>=0.8 widths would need an arm change - separate factor).
# Positions only; topology, corner order, UV0 (incl. LAMP19 cap fix), materials untouched; custom normals not re-set.
# usage: blender-python build_collartip_c1.py -- src.blend out_dir name
import bpy,sys,os,json,shutil
import numpy as np
src,out,name=sys.argv[sys.argv.index('--')+1:]; src=os.path.abspath(src); out=os.path.abspath(out)
R0,RB,ZB=0.036,0.0235,0.145
for p in (os.path.join(out,'fbx',name+'.fbx'),os.path.join(out,'models',name+'.blend'),os.path.join(out,'fbx','Shade_ARCH01.png')):
    assert not os.path.exists(p),'refuse to overwrite '+p
bpy.ops.wm.open_mainfile(filepath=src); o=bpy.data.objects['StraightLamp']; me=o.data; assert len(me.vertices)==1406
co=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); col=co[96:218]; cy=float((col[:,1].min()+col[:,1].max())/2)
bot=[i for i in range(96,218) if abs(co[i,2]-ZB)<1e-5]; assert len(bot)==41
r=np.hypot(co[bot,0],co[bot,1]-cy); assert abs(r.max()-R0)<1e-6
s=RB/R0; new=co.copy(); new[bot,0]=co[bot,0]*s; new[bot,1]=cy+(co[bot,1]-cy)*s
me.vertices.foreach_set('co',new.astype(np.float32).ravel()); me.update()
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
json.dump({'collar_axis':[0.0,cy],'bottom_ring_z':ZB,'radius_before':R0,'radius_after':RB,'scale':s,'changed_vertices':[i for i in bot if r[bot.index(i)]>1e-9],'centre_vertex_unchanged':[i for i in bot if r[bot.index(i)]<=1e-9]},
  open(os.path.join(out,'qa','build_log.json'),'w'),indent=1)
print('BUILD OK',len(bot))
