# COORD12-LAMP07 C1 (F1 only): Curved L1 - lower the cup group (collar, shade, diffuser) by DZ = -0.29 * Hs relative to the FIXED plate,
# and let only the arm tail follow so the arm still enters the collar exactly as before.
# - plate (verts 0-95): untouched (origin = plate bottom centre, plate back Y=0).
# - collar 588-709, shade 710-1415, diffuser 1416-1561: translated by (0,0,DZ).
# - arm 96-587 = 41 rings x 12 verts (ring 0 at the plate, ring 40 inside the collar). Rings 0..S are untouched (plate connection, thickness,
#   Y reach, U bottom ring 15, exit). For rings i > S: ring centre z += DZ * smoothstep((i-S)/(40-S)); each moved ring is rotated about the
#   X axis through its centre by the change of its centre-line tangent, so the tube cross-section stays perpendicular to the path.
#   S = 26 from qa/arm_tail_plan.json (smallest tail region whose max ring-to-ring bend does not exceed the original arm's max bend 5.90 deg).
# - Y is not changed anywhere. Topology, vertex/face order, UV0 and material indices untouched. Stored custom normals are NOT re-set.
# usage: blender-python build_curved_f1_c1.py -- src.blend out_dir name plan.json
import bpy,sys,os,json,shutil,math
import numpy as np
src,out,name,plan=sys.argv[sys.argv.index('--')+1:]
P=json.load(open(plan)); S=P['chosen']['s']; DZ=P['DZ']
out=os.path.abspath(out); src=os.path.abspath(src)
bpy.ops.wm.open_mainfile(filepath=src)
o=bpy.data.objects['CurvedLamp']; me=o.data
co=np.empty(len(me.vertices)*3,np.float64); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); assert len(co)==1562
new=co.copy()
for a,b in ((588,710),(710,1416),(1416,1562)): new[a:b,2]+=DZ
arm=co[96:588].reshape(41,12,3); C=arm.mean(1)
w=np.zeros(41); u=(np.arange(41)-S)/(40-S); m=np.arange(41)>S; w[m]=3*u[m]**2-2*u[m]**3
C2=C.copy(); C2[:,2]+=DZ*w
def tang(c):
    t=np.gradient(c[:,1:],axis=0); return np.arctan2(t[:,1],t[:,0])   # angle in the YZ plane
ang=tang(C2)-tang(C)
narm=arm.copy(); moved=[]
for i in range(41):
    if w[i]==0: continue
    a=ang[i]; ca,sa=math.cos(a),math.sin(a); rel=arm[i]-C[i]
    ry=rel[:,1]*ca-rel[:,2]*sa; rz=rel[:,1]*sa+rel[:,2]*ca
    narm[i,:,0]=arm[i,:,0]; narm[i,:,1]=C2[i,1]+ry; narm[i,:,2]=C2[i,2]+rz; moved.append(i)
new[96:588]=narm.reshape(-1,3)
me.vertices.foreach_set('co',new.astype(np.float32).ravel()); me.update()
os.makedirs(os.path.join(out,'fbx'),exist_ok=True); os.makedirs(os.path.join(out,'models'),exist_ok=True)
for p in (os.path.join(out,'fbx',name+'.fbx'),os.path.join(out,'models',name+'.blend'),os.path.join(out,'fbx','Shade_ARCH01.png')):
    assert not os.path.exists(p), 'refuse to overwrite '+p
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
json.dump({'Hs_m':P['Hs'],'factor':-0.29,'DZ_m':DZ,'tail_start_ring_S':S,'arm_rings_moved':moved,'arm_rings_kept':[i for i in range(41) if i not in moved],
  'max_ring_tangent_rotation_deg':float(np.degrees(np.abs(ang[moved]).max())),'translated_parts':['collar','shade','diffuser'],'plate':'untouched'},
  open(os.path.join(out,'qa','build_log.json'),'w'),indent=1)
print('BUILD OK',S,DZ,moved)
