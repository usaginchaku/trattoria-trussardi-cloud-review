# C4 vs C3m checks: original indices/loops/UV kept, only the crown verts moved, new tier = top-plate copy, normals, degeneracy, flips.
import bpy,bmesh,sys,json,numpy as np
a,b,ident,outp=sys.argv[-4:]
def load(p):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p)
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
    return dict(o=o,co=np.array([v.co[:] for v in me.vertices]),faces=[tuple(p.vertices) for p in me.polygons],
        loopv=np.array([l.vertex_index for l in me.loops]),uv=np.array([l.uv[:] for l in me.uv_layers[0].data]),cn=np.array([c.vector[:] for c in me.corner_normals]),
        fn=np.array([p.normal[:] for p in me.polygons]),area=np.array([p.area for p in me.polygons]),mats=[p.material_index for p in me.polygons],
        rot=list(o.rotation_euler),scale=list(o.scale),loc=list(o.location),uvnames=[u.name for u in me.uv_layers],matnames=[m.name for m in me.materials])
A=load(a); B=load(b); I=load(ident)
nv,nf,nl=len(A['co']),len(A['faces']),len(A['loopv'])
mv=np.linalg.norm(B['co'][:nv]-A['co'],axis=1); moved=np.where(mv>1e-6)[0]
crown=set(range(384,480))|set(range(576,672))
r={'bbox_C3m':[A['co'].min(0).round(5).tolist(),A['co'].max(0).round(5).tolist()],'bbox_C4':[B['co'].min(0).round(5).tolist(),B['co'].max(0).round(5).tolist()],
   'transform_C4':{'loc':B['loc'],'rot':B['rot'],'scale':B['scale']},'uv_layers':B['uvnames'],'materials':B['matnames'],
   'verts':[nv,len(B['co'])],'tris':[nf,len(B['faces'])],'original_faces_identical_order_and_indices':B['faces'][:nf]==A['faces'],
   'original_loops_vertex_identical':bool((B['loopv'][:nl]==A['loopv']).all()),'original_loops_uv_identical':bool(np.allclose(B['uv'][:nl],A['uv'],atol=1e-6)),
   'original_verts_moved':int(len(moved)),'moved_only_crown_boxes':bool(set(moved.tolist())<=crown),'mount_face_y0_verts':[int((np.abs(A['co'][:,1])<1e-5).sum()),int((np.abs(B['co'][:,1])<1e-5).sum())],
   'zero_area_faces':int((B['area']<1e-10).sum()),'faces_flipped_vs_C3m':int(((A['fn']*B['fn'][:nf]).sum(1)<0).sum()),
   'face_normal_max_change_original_faces':float(np.abs(A['fn']-B['fn'][:nf]).max()),
   'new_faces_material':sorted(set(B['mats'][nf:])),'zmax':[float(A['co'][:,2].max()),float(B['co'][:,2].max())],'zmin':[float(A['co'][:,2].min()),float(B['co'][:,2].min())]}
# new tier UV equals top plate UV (loops of new faces map to top-plate loops in the same order)
top_loops=[li for fi,f in enumerate(A['faces']) if set(f)<=set(range(384,480)) for li in range(0)]
newuv=B['uv'][nl:]; tpuv=np.concatenate([B['uv'][sum(len(f) for f in A['faces'][:fi]):sum(len(f) for f in A['faces'][:fi])+len(f)] for fi,f in enumerate(A['faces']) if set(f)<=set(range(384,480))])
r['new_tier_uv_equals_top_plate_uv']=bool(newuv.shape==tpuv.shape and np.allclose(newuv,tpuv,atol=1e-6))
# normals of unchanged loops vs the identity pass-through export (separates bpy4.3 re-encoding from edits)
d=np.abs(B['cn'][:nl]-I['cn']).max(1); r['corner_normals_vs_identity_passthrough_changed_gt1e-3']=int((d>1e-3).sum())
dI=np.abs(I['cn']-A['cn']).max(1); r['identity_passthrough_vs_C3m_import_changed_gt1e-3']=int((dI>1e-3).sum())
json.dump(r,open(outp,'w'),indent=1); print('CHK',json.dumps(r))
