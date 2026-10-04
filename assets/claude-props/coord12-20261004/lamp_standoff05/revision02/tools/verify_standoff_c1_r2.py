# independent check, new process: baseline vs C1 (blend-vs-blend, or FBX-vs-FBX re-imported with default importer settings)
# usage: blender-python verify_standoff_c1.py -- blend|fbx base_path c1_path out.json
import bpy,bmesh,sys,json,os,hashlib
import numpy as np
mode,bp,cp,out=sys.argv[sys.argv.index('--')+1:]
def load(p):
    if mode=='blend': bpy.ops.wm.open_mainfile(filepath=p)
    else: bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p)
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
    g=lambda coll,attr,n,dt=np.float32:(lambda a:(coll.foreach_get(attr,a),a)[1])(np.empty(n,dt))
    co=g(me.vertices,'co',len(me.vertices)*3).reshape(-1,3)
    d={'name':o.name,'loc':list(o.location),'rot':list(o.rotation_euler),'scale':list(o.scale),'materials':[m.name for m in me.materials],
       'uv_layers':[u.name for u in me.uv_layers],'custom_normals':me.has_custom_normals,'units':[bpy.context.scene.unit_settings.system,bpy.context.scene.unit_settings.scale_length],
       'co':co,'lv':g(me.loops,'vertex_index',len(me.loops),np.int32),'ls':g(me.polygons,'loop_start',len(me.polygons),np.int32),
       'lt':g(me.polygons,'loop_total',len(me.polygons),np.int32),'mi':g(me.polygons,'material_index',len(me.polygons),np.int32),
       'ed':g(me.edges,'vertices',len(me.edges)*2,np.int32),'uv':np.array([x.uv[:] for x in me.uv_layers[0].data],np.float64),
       'ln':g(me.corner_normals,'vector',len(me.loops)*3).reshape(-1,3),'tris':sum(len(p.vertices)-2 for p in me.polygons),
       'images':[(i.name,i.filepath,os.path.exists(bpy.path.abspath(i.filepath))) for i in bpy.data.images]}
    bm=bmesh.new(); bm.from_mesh(me)
    d['nonmanifold_edges']=sum(1 for e in bm.edges if not e.is_manifold); d['boundary_edges']=sum(1 for e in bm.edges if e.is_boundary)
    d['zero_area_faces']=sum(1 for f in bm.faces if f.calc_area()<1e-12); d['zero_len_normals']=int((np.linalg.norm(d['ln'],axis=1)<1e-6).sum())
    # shells by connectivity
    n=len(co); par=list(range(n))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    e=d['ed'].reshape(-1,2)
    for a,b in e:
        a,b=f(a),f(b)
        if a!=b: par[a]=b
    sh={}
    for i in range(n): sh.setdefault(f(i),[]).append(i)
    d['shells']=sorted(sh.values(),key=min)
    return d
A=load(os.path.abspath(bp)); B=load(os.path.abspath(cp))
names=['plate','arm','collar','shade','diffuser']
assert [len(s) for s in A['shells']]==[len(s) for s in B['shells']]
r={'mode':mode,'topology':{}, 'per_shell':{}, 'checks':{}}
for k in ('lv','ls','lt','mi','ed'): r['topology'][k+'_identical']=bool(A[k].shape==B[k].shape and (A[k]==B[k]).all())
r['topology']['vertex_count']=[len(A['co']),len(B['co'])]; r['topology']['tris']=[A['tris'],B['tris']]
# in FBX mode the importer may reorder? (it keeps order for Blender-written FBX); compare by index and report
for nm,va,vb in zip(names,A['shells'],B['shells']):
    d=B['co'][vb]-A['co'][va]
    loops=np.isin(A['lv'],va)
    r['per_shell'][nm]={'verts':len(va),'same_vertex_indices':va==vb,'delta_min':d.min(0).round(7).tolist(),'delta_max':d.max(0).round(7).tolist(),
        'y_max_before':float(A['co'][va][:,1].max()),'y_max_after':float(B['co'][vb][:,1].max()),'y_min_before':float(A['co'][va][:,1].min()),'y_min_after':float(B['co'][vb][:,1].min()),
        'verts_y_gt_0_before':int((A['co'][va][:,1]>1e-6).sum()),'verts_y_gt_0_after':int((B['co'][vb][:,1]>1e-6).sum()),
        'uv_max_diff':float(np.abs(A['uv'][loops]-B['uv'][loops]).max()),'loop_normal_max_diff':float(np.abs(A['ln'][loops]-B['ln'][loops]).max())}
arm=B['shells'][1]; ca=B['co'][arm]; pl=B['co'][B['shells'][0]]; colr=B['co'][B['shells'][2]]; sha=B['co'][B['shells'][3]]
r['checks']={
 'plate_back_y_max':float(pl[:,1].max()),'non_plate_max_y_after':float(B['co'][[i for s in B['shells'][1:] for i in s]][:,1].max()),
 'arm_plate_overlap_depth_m':float(-0.0 + (ca[:,1].max()-pl[:,1].min())),'arm_back_y':float(ca[:,1].max()),'plate_front_y':float(pl[:,1].min()),
 'arm_front_y':float(ca[:,1].min()),'collar_y_range':[float(colr[:,1].min()),float(colr[:,1].max())],'collar_center_y':float((colr[:,1].min()+colr[:,1].max())/2),
 'arm_z_range':[float(ca[:,2].min()),float(ca[:,2].max())],'collar_z_range':[float(colr[:,2].min()),float(colr[:,2].max())],
 'shade_back_y':float(sha[:,1].max()),'shade_min_z_where_y_gt_plate_front':float(sha[sha[:,1]>pl[:,1].min()][:,2].min()) if (sha[:,1]>pl[:,1].min()).any() else None,'plate_top_z':float(pl[:,2].max()),
 'bbox_before':[A['co'].min(0).tolist(),A['co'].max(0).tolist()],'bbox_after':[B['co'].min(0).tolist(),B['co'].max(0).tolist()],
 'ground_z_min':[float(A['co'][:,2].min()),float(B['co'][:,2].min())],
 'object':{'before':[A['name'],A['loc'],A['rot'],A['scale']],'after':[B['name'],B['loc'],B['rot'],B['scale']]},
 'materials':[A['materials'],B['materials']],'uv_layers':[A['uv_layers'],B['uv_layers']],'custom_normals':[A['custom_normals'],B['custom_normals']],'units':[A['units'],B['units']],
 'uv_all_loops_max_diff':float(np.abs(A['uv']-B['uv']).max()),'uv_negative_coords_count':[int((A['uv']<0).sum()),int((B['uv']<0).sum())],
 'loop_normals_all_max_diff':float(np.abs(A['ln']-B['ln']).max()),
 'mesh_quality':{'nonmanifold_edges':[A['nonmanifold_edges'],B['nonmanifold_edges']],'boundary_edges':[A['boundary_edges'],B['boundary_edges']],
    'zero_area_faces':[A['zero_area_faces'],B['zero_area_faces']],'zero_len_normals':[A['zero_len_normals'],B['zero_len_normals']]},
 'images':[A['images'],B['images']]}
json.dump(r,open(out,'w'),indent=1,default=lambda x:x.tolist() if hasattr(x,'tolist') else (bool(x) if isinstance(x,np.bool_) else str(x)))
print(json.dumps(r['topology'])); [print(k,v['delta_min'],v['delta_max'],v['verts_y_gt_0_before'],v['verts_y_gt_0_after'],v['uv_max_diff'],round(v['loop_normal_max_diff'],6)) for k,v in r['per_shell'].items()]
print({k:r['checks'][k] for k in ('plate_back_y_max','non_plate_max_y_after','arm_back_y','plate_front_y','arm_front_y','collar_y_range','shade_back_y','shade_min_z_where_y_gt_plate_front','plate_top_z','uv_all_loops_max_diff','loop_normals_all_max_diff','mesh_quality','units','images')})
