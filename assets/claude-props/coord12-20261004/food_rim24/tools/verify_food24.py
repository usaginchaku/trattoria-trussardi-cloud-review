# independent check (new process). Compares A vs B (blend or FBX) against pink_plate_native.json bands.
# usage: blender-python verify_food24.py -- blend|fbx A B native.json out.json
import bpy,bmesh,sys,json,os,math
import numpy as np
mode,ap,bp,nj,out=sys.argv[sys.argv.index('--')+1:]
d=json.load(open(nj)); P=np.array(d['nativeChannels']['positions']); N=np.array(d['nativeChannels']['normals']); C=np.array([1,-1,-1.0]); E=sorted(d['baselineSafetyBoundary']['editableSubsetVertexIds'])
def load(p):
    if mode=='blend': bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p))
    else: bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=os.path.abspath(p))
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
    def g(c,a,n,dt=np.float32): x=np.empty(n,dt); c.foreach_get(a,x); return x
    r={'o':[list(o.location),list(o.rotation_euler),list(o.scale)],'mats':[m.name for m in me.materials],'uvl':[u.name for u in me.uv_layers],'custom':me.has_custom_normals,
       'units':[bpy.context.scene.unit_settings.system,bpy.context.scene.unit_settings.scale_length],'co':g(me.vertices,'co',len(me.vertices)*3).reshape(-1,3),
       'lv':g(me.loops,'vertex_index',len(me.loops),np.int32),'tri':np.array([list(p.vertices) for p in me.polygons],np.int32),'mi':g(me.polygons,'material_index',len(me.polygons),np.int32),
       'uv':g(me.uv_layers[0].data,'uv',len(me.loops)*2).reshape(-1,2),'ln':g(me.corner_normals,'vector',len(me.loops)*3).reshape(-1,3),'fn':np.array([p.normal[:] for p in me.polygons]),
       'area0':sum(1 for p in me.polygons if p.area<1e-12),'attrs':sorted(a.name for a in me.attributes if not a.name.startswith('.')),
       'images':[(i.name,i.filepath,os.path.exists(os.path.normpath(bpy.path.abspath(i.filepath)))) for i in bpy.data.images]}
    if 'sourceNativeVertexId' in me.attributes:
        x=np.empty(len(me.vertices),np.int32); me.attributes['sourceNativeVertexId'].data.foreach_get('value',x); r['snv_ok']=bool((x==np.array(d['sourceNativeVertexIds'])).all())
    bm=bmesh.new(); bm.from_mesh(me); r['nonmanifold_raw']=sum(1 for e in bm.edges if not e.is_manifold); r['boundary_raw']=sum(1 for e in bm.edges if e.is_boundary)
    bmesh.ops.remove_doubles(bm,verts=bm.verts[:],dist=1e-7); r['welded_diag']={'verts':len(bm.verts),'nonmanifold':sum(1 for e in bm.edges if not e.is_manifold),'boundary':sum(1 for e in bm.edges if e.is_boundary)}
    return r
A=load(ap); B=load(bp)
ang=lambda a,b:np.degrees(np.arccos(np.clip((a*b).sum(1)/np.linalg.norm(a,axis=1)/np.linalg.norm(b,axis=1),-1,1)))
moved=np.where(np.any(A['co']!=B['co'],axis=1))[0]
r_n=np.hypot(P[:,0],P[:,1]); contact=np.where((r_n<=0.0513+1e-6)&(N[:,2]<0))[0]; under=np.where(N[:,2]>0)[0]; lip=np.where(r_n>=0.08505-1e-6)[0]
Es=np.zeros(1647,bool); Es[E]=True; eL=Es[B['lv']]
adj=set(B['tri'][np.isin(B['tri'],E).any(1)].ravel())-set(E); adjL=np.isin(B['lv'],list(adj))
res={'mode':mode,'topology':{'tri_equal':bool(np.array_equal(A['tri'],B['tri'])),'loops_equal':bool(np.array_equal(A['lv'],B['lv'])),'mat_equal':bool(np.array_equal(A['mi'],B['mi']))},
 'moved_vertices':int(len(moved)),'moved_subset_of_editable':bool(set(moved.tolist())<=set(E)),'held_positions_bit_equal':bool(np.array_equal(A['co'][~Es],B['co'][~Es])),
 'bands_bit_equal':{'contact_r<=0.0513_up':bool(np.array_equal(A['co'][contact],B['co'][contact])),'underside_nativeNz>0':bool(np.array_equal(A['co'][under],B['co'][under])),'outer_lip_r>=0.08505':bool(np.array_equal(A['co'][lip],B['co'][lip])),
   'counts':[len(contact),len(under),len(lip)],'overlap_with_editable':int(len(set(E)&(set(contact)|set(under)|set(lip))))},
 'uv0_bit_equal':bool(np.array_equal(A['uv'],B['uv'])),'bounds':[[B['co'].min(0).tolist(),B['co'].max(0).tolist()],[A['co'].min(0).tolist(),A['co'].max(0).tolist()]],
 'normals':{'unedited_loops_max_deg_vs_A':float(ang(A['ln'][~eL],B['ln'][~eL]).max()),'unedited_loops_changed_count(>1e-6deg)':int((ang(A['ln'][~eL],B['ln'][~eL])>1e-6).sum()),
   'adjacent_fixed_ring_loops':int(adjL.sum()),'adjacent_loops_max_deg_vs_A':float(ang(A['ln'][adjL],B['ln'][adjL]).max()) if adjL.any() else None,
   'edited_loops':int(eL.sum()),'edited_loops_max_deg_vs_A':float(ang(A['ln'][eL],B['ln'][eL]).max())},
 'quality':{'A':{k:A[k] for k in ('nonmanifold_raw','boundary_raw','welded_diag','area0')},'B':{k:B[k] for k in ('nonmanifold_raw','boundary_raw','welded_diag','area0')}},
 'object':[A['o'],B['o']],'materials':[A['mats'],B['mats']],'uv_layers':[A['uvl'],B['uvl']],'custom':[A['custom'],B['custom']],'units':[A['units'],B['units']],'attrs':[A['attrs'],B['attrs']],
 'sourceNativeVertexId_ok':[A.get('snv_ok'),B.get('snv_ok')],'images':[A['images'],B['images']]}
# health of edited normals: angle to faces they belong to; and fixed boundary ring kept normals vs new geometric (welded) normal
ft=B['tri']; res['normals']['edited_loop_vs_own_face_max_deg']=float(max(ang(B['ln'][[l]],B['fn'][[f]])[0] for f in range(len(ft)) for l in range(3*f,3*f+3) if Es[B['lv'][l]]))
json.dump(res,open(out,'w'),indent=1,default=lambda x:x.tolist() if hasattr(x,'tolist') else str(x))
print(json.dumps({k:v for k,v in res.items() if k not in ('images','attrs')},default=str)[:2500])
