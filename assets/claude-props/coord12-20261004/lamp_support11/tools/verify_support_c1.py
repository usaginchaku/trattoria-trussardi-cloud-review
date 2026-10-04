# independent check (new process): baseline (LAMP05 rev02 C1) vs ARM_C1, blend-vs-blend or FBX-vs-FBX (default importer).
# Non-arm shells are mapped by index: base plate 0-95 -> 0-95, collar 192-313 -> 96-217, shade 314-1019 -> 218-923,
# diffuser 1020-1165 -> 924-1069; the new arm is appended (1070-). Non-arm faces are compared in their original relative order.
# usage: blender-python verify_support_c1.py -- blend|fbx base c1 out.json
import bpy,bmesh,sys,json,os,math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
mode,bp,cp,out=sys.argv[sys.argv.index('--')+1:]
def load(p):
    if mode=='blend': bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p))
    else: bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=os.path.abspath(p))
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
    def g(c,a,n,dt=np.float64): x=np.empty(n,dt); c.foreach_get(a,x); return x
    d={'o':[o.name,list(o.location),list(o.rotation_euler),list(o.scale)],'mats':[m.name for m in me.materials],'uvl':[u.name for u in me.uv_layers],'custom':me.has_custom_normals,
       'units':[bpy.context.scene.unit_settings.system,bpy.context.scene.unit_settings.scale_length],
       'co':g(me.vertices,'co',len(me.vertices)*3).reshape(-1,3),'lv':g(me.loops,'vertex_index',len(me.loops),np.int64),'ls':g(me.polygons,'loop_start',len(me.polygons),np.int64),
       'lt':g(me.polygons,'loop_total',len(me.polygons),np.int64),'mi':g(me.polygons,'material_index',len(me.polygons),np.int64),
       'uv':g(me.uv_layers[0].data,'uv',len(me.loops)*2).reshape(-1,2),'ln':g(me.corner_normals,'vector',len(me.loops)*3).reshape(-1,3),
       'fn':np.array([p.normal[:] for p in me.polygons]),'tris':[list(p.vertices) for p in me.polygons],
       'images':[(i.name,i.filepath,os.path.exists(os.path.normpath(bpy.path.abspath(i.filepath)))) for i in bpy.data.images]}
    bm=bmesh.new(); bm.from_mesh(me)
    d['q']={'nonmanifold':sum(1 for e in bm.edges if not e.is_manifold),'boundary':sum(1 for e in bm.edges if e.is_boundary),'zero_area':sum(1 for f in bm.faces if f.calc_area()<1e-12),
            'zero_len_normals':int((np.linalg.norm(d['ln'],axis=1)<1e-6).sum()),'tris':len(me.polygons),'verts':len(me.vertices)}
    return d
A=load(bp); B=load(cp)
vmap=np.full(len(A['co']),-1); vmap[0:96]=np.arange(96); vmap[192:1166]=np.arange(96,1070)
keepA=[i for i,t in enumerate(A['tris']) if not (96<=t[0]<192)]
keepB=[i for i,t in enumerate(B['tris']) if t[0]<1070]
r={'mode':mode,'counts':{'verts':[len(A['co']),len(B['co'])],'faces':[len(A['tris']),len(B['tris'])],'kept_faces':[len(keepA),len(keepB)]}}
same_faces=len(keepA)==len(keepB) and all([vmap[v] for v in A['tris'][i]]==B['tris'][j] for i,j in zip(keepA,keepB))
r['non_arm_face_vertex_order_identical']=bool(same_faces)
parts={'plate':(0,96),'collar':(192,314),'shade':(314,1020),'diffuser':(1020,1166)}
r['parts']={}
for nm,(a,b) in parts.items():
    dpos=np.abs(B['co'][vmap[a:b]]-A['co'][a:b]).max()
    fi=[(i,j) for i,j in zip(keepA,keepB) if a<=A['tris'][i][0]<b]
    la=np.concatenate([np.arange(A['ls'][i],A['ls'][i]+A['lt'][i]) for i,_ in fi]); lb=np.concatenate([np.arange(B['ls'][j],B['ls'][j]+B['lt'][j]) for _,j in fi])
    r['parts'][nm]={'verts':b-a,'max_pos_diff':float(dpos),'max_uv_diff':float(np.abs(A['uv'][la]-B['uv'][lb]).max()),'max_normal_diff':float(np.abs(A['ln'][la]-B['ln'][lb]).max()),
        'material_index_same':bool(all(A['mi'][i]==B['mi'][j] for i,j in fi))}
# new arm
ai=np.arange(1070,len(B['co'])); af=[j for j,t in enumerate(B['tris']) if t[0]>=1070]
al=np.concatenate([np.arange(B['ls'][j],B['ls'][j]+B['lt'][j]) for j in af])
fnl=np.concatenate([[B['fn'][j]]*B['lt'][j] for j in af]); dots=(B['ln'][al]*fnl).sum(1)
arm=B['co'][ai]; pl=B['co'][0:96]; col=B['co'][96:218]; sh=B['co'][218:924]
r['arm']={'verts':len(ai),'faces':len(af),'material_slots':sorted(set(int(B['mi'][j]) for j in af)),'bbox':[arm.min(0).tolist(),arm.max(0).tolist()],
  'loop_normal_vs_face_normal_min_dot':float(dots.min()),'loop_normals_angle_to_face_max_deg':float(np.degrees(np.arccos(np.clip(dots.min(),-1,1)))),
  'uv_range':[B['uv'][al].min(0).tolist(),B['uv'][al].max(0).tolist()]}
bvh=lambda lo,hi:BVHTree.FromPolygons([tuple(v) for v in B['co']],[t for t in B['tris'] if lo<=t[0]<hi])
pb=bvh(0,96); cb=bvh(96,218); sb=bvh(218,924)
inside=lambda tree,v:(tree.ray_cast(Vector(v),Vector((0,0,1)))[0] is not None and tree.ray_cast(Vector(v),Vector((0,0,-1)))[0] is not None and tree.ray_cast(Vector(v),Vector((0,1,0)))[0] is not None)
top=arm[arm[:,2]>arm[:,2].max()-0.002]; end=arm[arm[:,1]>arm[:,1].max()-0.002]
r['connection']={'arm_top_z':float(arm[:,2].max()),'collar_z_range':[float(col[:,2].min()),float(col[:,2].max())],'arm_top_verts_inside_collar':int(sum(inside(cb,v) for v in top)),'arm_top_verts':len(top),
  'arm_end_y':float(arm[:,1].max()),'plate_front_y':float(pl[:,1].min()),'arm_end_embed_m':float(arm[:,1].max()-pl[:,1].min()),'arm_end_verts_inside_plate':int(sum(inside(pb,v) for v in end)),'arm_end_verts':len(end),
  'arm_z_min':float(arm[:,2].min()),'plate_z_range':[float(pl[:,2].min()),float(pl[:,2].max())],
  'arm_min_distance_to_shade_m':float(min(sb.find_nearest(Vector(v))[3] for v in arm)),'arm_verts_y_gt_0':int((arm[:,1]>1e-6).sum()),'non_plate_max_y':float(B['co'][96:,1].max())}
r['other']={'object':[A['o'],B['o']],'materials':[A['mats'],B['mats']],'uv_layers':[A['uvl'],B['uvl']],'custom':[A['custom'],B['custom']],'units':[A['units'],B['units']],
  'quality':[A['q'],B['q']],'images':[A['images'],B['images']],'bbox':[[A['co'].min(0).tolist(),A['co'].max(0).tolist()],[B['co'].min(0).tolist(),B['co'].max(0).tolist()]]}
json.dump(r,open(out,'w'),indent=1,default=lambda x:x.tolist() if hasattr(x,'tolist') else str(x))
print(json.dumps({k:r[k] for k in ('counts','non_arm_face_vertex_order_identical')})); [print(k,v) for k,v in r['parts'].items()]; print('arm',r['arm']); print('conn',r['connection']); print(r['other']['quality'],r['other']['images'],r['other']['bbox'])
