# revision02 of ../../tools/build_support_c1.py: deselect everything before shade_smooth_by_angle (see qa).
# COORD12-LAMP11 C1 (one factor: the SIDE OUTLINE of the Straight support arm).
# Input: lamp_standoff05/revision02 StraightLamp_ARCH01_C1.blend (read-only). Output files are new; existing paths are refused.
# - removes the arm shell (verts 96-191, a 0.031 x 0.100 x 0.170 m rounded slab) from the mesh with bmesh (other shells untouched),
# - builds a new arm as a swept bar with the SAME front width 0.031 m (x) and a 0.031 m depth across the path, rounded corners r 0.004,
#   following a J path in the YZ plane: straight down from inside the collar, a 0.035 m radius bend toward the wall, straight into the plate
#   face (end embedded 13 mm, as before: y -0.015). Collar entry point (y -0.117 = collar centre) and plate overlap are kept.
# - arm normals: flat sides keep face normals, rounded corners smooth (custom normals set on the separate arm object only), arm UV0 =
#   metric (arc length, perimeter) like the existing box-projected metric UVs; then the arm object is joined (appended last).
# - plate / collar / shade / diffuser: positions, UV0, stored custom normals, material indices, relative order unchanged.
# usage: blender-python build_support_c1.py -- src.blend out_dir name
import bpy,bmesh,sys,os,json,math,shutil
import numpy as np
from mathutils import Vector
src,out,name=sys.argv[sys.argv.index('--')+1:]; src=os.path.abspath(src); out=os.path.abspath(out)
for p in (os.path.join(out,'fbx',name+'.fbx'),os.path.join(out,'models',name+'.blend'),os.path.join(out,'fbx','Shade_ARCH01.png')):
    assert not os.path.exists(p),'refuse to overwrite '+p
bpy.ops.wm.open_mainfile(filepath=src); o=bpy.data.objects['StraightLamp']; me=o.data
assert len(me.vertices)==1166
# 1) remove the old arm shell
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.verts[i] for i in range(96,192)],context='VERTS'); bm.to_mesh(me); bm.free(); me.update()
# 2) path
HW=0.0155; RC=0.004; CS=3; R=0.035
Y0,ZTOP,ZB,ZEND,YEND=-0.117,0.165,0.090,0.055,-0.015
pts=[]
for z in np.linspace(ZTOP,ZB,6): pts.append((Y0,z))
cy,cz=Y0+R,ZB
for k in range(1,10):
    a=math.pi+ (math.pi/2)*k/9          # from angle pi (point at y0) sweeping toward the bottom
    pts.append((cy+R*math.cos(a),cz+R*math.sin(a)))
for y in np.linspace(cy,YEND,7)[1:]: pts.append((y,ZEND))
P=np.array(pts); T=np.gradient(P,axis=0); T/=np.linalg.norm(T,axis=1)[:,None]
assert abs(P[14,1]-ZEND)<1e-9 and abs(P[14,0]-cy)<1e-9   # last bend point = start of the straight run into the plate
# 3) rounded-square section in (x, n) with n = tangent rotated +90 deg in YZ
sec=[]
for cx,cn,a0 in ((HW-RC,HW-RC,0),(-(HW-RC),HW-RC,90),(-(HW-RC),-(HW-RC),180),(HW-RC,-(HW-RC),270)):
    for k in range(CS+1):
        a=math.radians(a0+90*k/CS); sec.append((cx+RC*math.cos(a),cn+RC*math.sin(a)))
sec=np.array(sec); NS=len(sec)
perim=np.concatenate([[0],np.cumsum(np.linalg.norm(np.diff(np.vstack([sec,sec[:1]]),axis=0),axis=1))])
abm=bmesh.new(); rings=[]
for (py,pz),(ty,tz) in zip(P,T):
    ny,nz=-tz,ty
    rings.append([abm.verts.new((sx,py+sn*ny,pz+sn*nz)) for sx,sn in sec])
uvl=abm.loops.layers.uv.new('ArchitectureUV')
s=np.concatenate([[0],np.cumsum(np.linalg.norm(np.diff(P,axis=0),axis=1))])
faces=[]
for i in range(len(rings)-1):
    for j in range(NS):
        j2=(j+1)%NS; f=abm.faces.new((rings[i][j],rings[i][j2],rings[i+1][j2],rings[i+1][j])); faces.append((f,i,j))
        for l,(ii,jj) in zip(f.loops,((i,j),(i,j+1),(i+1,j+1),(i+1,j))): l[uvl].uv=(s[ii]-0.03,perim[jj]-0.032)
c0=abm.faces.new(rings[0][::-1]); c1=abm.faces.new(rings[-1])
for f in (c0,c1):
    for l in f.loops: v=l.vert.co; l[uvl].uv=(v.x,(v.y if f is c1 else v.z))
abm.normal_update(); bmesh.ops.recalc_face_normals(abm,faces=abm.faces)
bmesh.ops.triangulate(abm,faces=abm.faces[:])
am=bpy.data.meshes.new('arm'); abm.to_mesh(am); abm.free()
am.polygons.foreach_set('use_smooth',[True]*len(am.polygons))
ao=bpy.data.objects.new('arm',am); bpy.context.scene.collection.objects.link(ao)
for m in me.materials: am.materials.append(m)
am.polygons.foreach_set('material_index',[0]*len(am.polygons))
# arm normals: smooth across the rounded corners and along the path, sharp at the end caps (face normal)
for x in bpy.context.view_layer.objects: x.select_set(False)   # r2 fix: only the new arm may be affected (r1 also cleared the lamp body's custom normals)
bpy.context.view_layer.objects.active=ao; ao.select_set(True)
assert list(bpy.context.selected_objects)==[ao]
bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
for mm in list(ao.modifiers): bpy.ops.object.modifier_apply(modifier=mm.name)
cn=[tuple(l.vector) for l in am.corner_normals]; am.normals_split_custom_set(cn)
# 4) join: arm appended after the remaining shells
bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); ao.select_set(True); bpy.context.view_layer.objects.active=o; bpy.ops.object.join()
o=bpy.context.view_layer.objects.active; assert o.name=='StraightLamp'
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
json.dump({'factor':'support arm side outline: rounded slab 0.031 x 0.100 x 0.170 -> J-bent bar 0.031 x 0.031','path_yz':P.round(5).tolist(),
  'bend_radius_m':R,'section':{'half_width_m':HW,'corner_radius_m':RC,'verts_per_ring':NS},'rings':len(P),'arm_verts':len(P)*NS,
  'collar_entry':[Y0,ZTOP],'plate_entry':[YEND,ZEND],'removed_arm_verts':96},open(os.path.join(out,'qa','build_log.json'),'w'),indent=1)
print('BUILD OK',len(P),NS)
