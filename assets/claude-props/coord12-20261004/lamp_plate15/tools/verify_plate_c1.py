# independent check (new process): baseline ARM_C1r2 vs PLATE_C1 (same topology), blend-vs-blend or FBX-vs-FBX (default importer).
# parts: plate 0-95, collar 96-217, shade 218-923, diffuser 924-1069, arm 1070-1405.
# usage: blender-python verify_plate_c1.py -- blend|fbx base c1 out.json
import bpy,bmesh,sys,json,os,math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
mode,bp,cp,out=sys.argv[sys.argv.index('--')+1:]; S=0.75; ZC=0.09
P={'plate':(0,96),'collar':(96,218),'shade':(218,924),'diffuser':(924,1070),'arm':(1070,1406)}
def load(p):
    if mode=='blend': bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p))
    else: bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=os.path.abspath(p))
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
    def g(c,a,n,dt=np.float64): x=np.empty(n,dt); c.foreach_get(a,x); return x
    d={'o':[o.name,list(o.location),list(o.rotation_euler),list(o.scale)],'mats':[m.name for m in me.materials],'uvl':[u.name for u in me.uv_layers],'custom':me.has_custom_normals,
       'units':[bpy.context.scene.unit_settings.system,bpy.context.scene.unit_settings.scale_length],'co':g(me.vertices,'co',len(me.vertices)*3).reshape(-1,3),
       'lv':g(me.loops,'vertex_index',len(me.loops),np.int64),'ls':g(me.polygons,'loop_start',len(me.polygons),np.int64),'lt':g(me.polygons,'loop_total',len(me.polygons),np.int64),
       'mi':g(me.polygons,'material_index',len(me.polygons),np.int64),'uv':g(me.uv_layers[0].data,'uv',len(me.loops)*2).reshape(-1,2),
       'ln':g(me.corner_normals,'vector',len(me.loops)*3).reshape(-1,3),'tris':[list(p.vertices) for p in me.polygons],
       'images':[(i.name,i.filepath,os.path.exists(os.path.normpath(bpy.path.abspath(i.filepath)))) for i in bpy.data.images]}
    bm=bmesh.new(); bm.from_mesh(me)
    d['q']={'nonmanifold':sum(1 for e in bm.edges if not e.is_manifold),'boundary':sum(1 for e in bm.edges if e.is_boundary),'zero_area':sum(1 for f in bm.faces if f.calc_area()<1e-12),
            'zero_len_normals':int((np.linalg.norm(d['ln'],axis=1)<1e-6).sum()),'tris':len(me.polygons),'verts':len(me.vertices)}
    return d
A=load(bp); B=load(cp)
r={'mode':mode,'topology':{k:bool(A[k].shape==B[k].shape and (A[k]==B[k]).all()) for k in ('lv','ls','lt','mi')},'parts':{}}
for nm,(a,b) in P.items():
    L=(A['lv']>=a)&(A['lv']<b); d=B['co'][a:b]-A['co'][a:b]
    e={'max_pos_diff':float(np.abs(d).max()),'max_uv_diff':float(np.abs(A['uv'][L]-B['uv'][L]).max()),'max_normal_diff':float(np.abs(A['ln'][L]-B['ln'][L]).max())}
    if nm=='plate':
        exp=A['co'][a:b].copy(); exp[:,0]*=S; exp[:,2]=ZC+S*(exp[:,2]-ZC); e['max_pos_diff_vs_expected_scale']=float(np.abs(B['co'][a:b]-exp).max())
        ideal=A['ln'][L]*np.array([1/S,1,1/S]); ideal/=np.linalg.norm(ideal,axis=1)[:,None]; nb=B['ln'][L]/np.linalg.norm(B['ln'][L],axis=1)[:,None]
        e['normal_angle_vs_inverse_transpose_ideal_max_deg']=float(np.degrees(np.arccos(np.clip((nb*ideal).sum(1),-1,1))).max())
    r['parts'][nm]=e
c=B['co']; pl=c[0:96]; arm=c[1070:1406]
tree=BVHTree.FromPolygons([tuple(v) for v in c],[t for t in B['tris'] if t[0]<96])
def inside(v): return all(tree.ray_cast(Vector(v),Vector(dv))[0] is not None for dv in ((0,0,1),(0,0,-1),(1,0,0),(-1,0,0)))
end=arm[arm[:,1]>arm[:,1].max()-0.002]
r['checks']={'plate_x':[float(pl[:,0].min()),float(pl[:,0].max())],'plate_z':[float(pl[:,2].min()),float(pl[:,2].max())],'plate_y':[float(pl[:,1].min()),float(pl[:,1].max())],
 'plate_back_on_wall_Y0':bool(abs(pl[:,1].max())<1e-6),'verts_y_gt_0':int((c[:,1]>1e-6).sum()),'non_plate_max_y':float(c[96:,1].max()),
 'arm_end_verts_inside_plate':int(sum(inside(v) for v in end)),'arm_end_verts':len(end),'arm_end_bbox':[end.min(0).tolist(),end.max(0).tolist()],
 'model_z_min':float(c[:,2].min()),'origin_note':'object transform unchanged; origin stays where the old plate bottom was (z 0); plate bottom now at plate_z[0]',
 'plate_aspect_H_over_W':float((pl[:,2].max()-pl[:,2].min())/(pl[:,0].max()-pl[:,0].min())),'plate_W_over_Ws':float((pl[:,0].max()-pl[:,0].min())/0.222),'plate_H_over_Ws':float((pl[:,2].max()-pl[:,2].min())/0.222)}
r['other']={'object':[A['o'],B['o']],'materials':[A['mats'],B['mats']],'uv_layers':[A['uvl'],B['uvl']],'custom':[A['custom'],B['custom']],'units':[A['units'],B['units']],'quality':[A['q'],B['q']],'images':[A['images'],B['images']],
 'bbox':[[A['co'].min(0).tolist(),A['co'].max(0).tolist()],[B['co'].min(0).tolist(),B['co'].max(0).tolist()]]}
json.dump(r,open(out,'w'),indent=1,default=lambda x:x.tolist() if hasattr(x,'tolist') else str(x))
print(r['topology']); [print(k,v) for k,v in r['parts'].items()]; print(r['checks']); print(r['other']['quality'],r['other']['images'],r['other']['object'][1])
