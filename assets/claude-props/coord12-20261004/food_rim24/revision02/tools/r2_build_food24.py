# revision02 copy of ../tools/build_food24.py (profile normals for the edited rings).
# COORD12-FOOD24: pink plate upper inner-boundary / broad-rim shape candidate (one candidate C1) + an equal-pipeline baseline B0.
# Cloud bpy 4.3.0 cannot open the Blender 5.2.2 input .blend (newer file header), so both B0 and C1 are rebuilt from the input FBX
# (verified: positions, triangle order, UV0 identical to pink_plate_native.json; normals <= 0.032 deg) with custom normals set from the
# native normals, native tangents and sourceNativeVertexId stored as attributes. Native (x,y,z) -> Blender (x,-y,-z).
# C1 edits ONLY baselineSafetyBoundary.editableSubsetVertexIds (194 verts, rings r 0.0612 / 0.0738):
#   ring r0.0612 -> radius RA, Blender z ZA ; ring r0.0738 -> radius unchanged, Blender z ZB.
# Normals: loops of the 194 edited verts get geometric area-weighted normals of the welded (position) upper-surface neighbourhood on the
# C1 geometry; every other loop keeps the native normal. Tangents of edited verts: native tangent Gram-Schmidt to the new normal, w kept.
# usage: blender-python build_food24.py -- input_dir out_dir variant(B0|C1)
import bpy,sys,os,json,shutil,math
import numpy as np
I,out,var=sys.argv[sys.argv.index('--')+1:]; I=os.path.abspath(I); out=os.path.abspath(out)
RA,ZA,ZB=0.0560,0.0285,0.0298
name={'B0':'PinkPlate_FOOD24_B0_rebuilt','C1':'PinkPlate_FOOD24_C1r2'}[var]
for p in (os.path.join(out,name+'.blend'),os.path.join(out,name+'.fbx')): assert not os.path.exists(p),'refuse to overwrite '+p
d=json.load(open(os.path.join(I,'pink_plate_native.json'))); P=np.array(d['nativeChannels']['positions']); N=np.array(d['nativeChannels']['normals'])
Tn=np.array(d['nativeChannels']['tangents']); C=np.array([1,-1,-1.0]); E=sorted(d['baselineSafetyBoundary']['editableSubsetVertexIds'])
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=os.path.join(I,'PinkPlate_FOOD23.fbx'))
o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data; assert len(me.vertices)==1647 and len(me.polygons)==2880
co=np.empty(1647*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); assert np.abs(co-P*C).max()==0
newco=co.copy(); r=np.hypot(co[:,0],co[:,1]); ringA=[i for i in E if abs(r[i]-0.0612)<5e-4]; ringB=[i for i in E if abs(r[i]-0.0738)<5e-4]
assert len(ringA)+len(ringB)==194
if var=='C1':
    for i in ringA: s=RA/r[i]; newco[i,0]*=s; newco[i,1]*=s; newco[i,2]=ZA
    for i in ringB: newco[i,2]=ZB
me.vertices.foreach_set('co',newco.astype(np.float32).ravel()); me.update()
lv=np.empty(len(me.loops),np.int64); me.loops.foreach_get('vertex_index',lv)
normB=N*C; loopN=normB[lv].copy(); tanB=Tn[:,:3]*C; newT=tanB.copy(); Es=set(E)
if var=='C1':
    # revision02: axisymmetric profile normals (independent of the triangle fan layout, which caused radial streaks in C1):
    # for ring A / ring B the profile angle is the mean of the adjacent upper-profile segment angles; normal = (-sin t * radial, cos t).
    prof=[(0.0513,0.0222),(RA,ZA),(0.0738,ZB),(0.085,0.0305)]
    seg=[math.atan2(b[1]-a[1],b[0]-a[0]) for a,b in zip(prof,prof[1:])]
    th={'A':(seg[0]+seg[1])/2,'B':(seg[1]+seg[2])/2}
    for ids,k in ((ringA,'A'),(ringB,'B')):
        for i in ids:
            rad=np.array([newco[i,0],newco[i,1],0.0]); rad/=np.linalg.norm(rad); t_=th[k]
            n=np.array([-math.sin(t_)*rad[0],-math.sin(t_)*rad[1],math.cos(t_)]); normB[i]=n
            tt=tanB[i]-np.dot(tanB[i],n)*n; newT[i]=tt/np.linalg.norm(tt)
    m=np.isin(lv,E); loopN[m]=normB[lv[m]]
me.normals_split_custom_set([tuple(x) for x in loopN]); me.update()
a=me.attributes.new('sourceNativeVertexId','INT','POINT'); a.data.foreach_set('value',np.array(d['sourceNativeVertexIds'],dtype=np.int32))
t=me.attributes.new('nativeTangentXYZ','FLOAT_VECTOR','POINT'); t.data.foreach_set('vector',newT.astype(np.float32).ravel())
w=me.attributes.new('nativeTangentW','FLOAT','POINT'); w.data.foreach_set('value',Tn[:,3].astype(np.float32))
os.makedirs(os.path.join(out,'textures'),exist_ok=True)
for fn in ('MatCap_Ceramic_MAT01.png','Normal_CeramicMicro_MAT01.png'):
    dst=os.path.join(out,'textures',fn)
    if not os.path.exists(dst): shutil.copyfile(os.path.join(I,'textures',fn),dst)
for im in bpy.data.images: im.filepath=os.path.join(out,'textures',os.path.basename(im.filepath))
o.name=name
o.select_set(True); bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=os.path.join(out,name+'.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',
    bake_space_transform=False,mesh_smooth_type='FACE',use_tspace=False,add_leaf_bones=False,path_mode='RELATIVE')
for sc in bpy.data.scenes: sc.render.filepath='//render/'
for im in bpy.data.images: im.filepath_raw='x'*900; im.filepath_raw='//textures/'+os.path.basename(im.filepath_raw if False else im.name)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out,name+'.blend'),compress=True,relative_remap=False)
json.dump({'variant':var,'RA':RA,'ZA':ZA,'ZB':ZB,'ringA_vertices':ringA,'ringB_vertices':ringB,
  'native_positions_of_edited':{str(i):(newco[i]*C).tolist() for i in E}},open(os.path.join(out,'build_log_%s.json'%var),'w'),indent=1)
print('BUILD OK',var,len(ringA),len(ringB))
