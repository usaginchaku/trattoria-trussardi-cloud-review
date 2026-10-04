# independent check (new process): baseline vs C1, blend-vs-blend or FBX-vs-FBX (default importer). Parts by fixed index ranges, verified
# by connectivity. Reports topology identity, per-part deltas, arm ring map, F1 ratios, clearances, wall, mesh quality, normals, UV.
# usage: blender-python verify_curved_f1_c1.py -- blend|fbx base c1 out.json
import bpy,bmesh,sys,json,os
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
mode,bp,cp,out=sys.argv[sys.argv.index('--')+1:]
PARTS={'plate':(0,96),'arm':(96,588),'collar':(588,710),'shade':(710,1416),'diffuser':(1416,1562)}
def load(p):
    if mode=='blend': bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p))
    else: bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=os.path.abspath(p))
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
    def g(c,a,n,dt=np.float64): x=np.empty(n,dt); c.foreach_get(a,x); return x
    d={'name':o.name,'loc':list(o.location),'rot':list(o.rotation_euler),'scale':list(o.scale),'materials':[m.name for m in me.materials],'uvl':[u.name for u in me.uv_layers],
       'custom':me.has_custom_normals,'units':[bpy.context.scene.unit_settings.system,bpy.context.scene.unit_settings.scale_length],
       'co':g(me.vertices,'co',len(me.vertices)*3).reshape(-1,3),'lv':g(me.loops,'vertex_index',len(me.loops),np.int64),'ls':g(me.polygons,'loop_start',len(me.polygons),np.int64),
       'lt':g(me.polygons,'loop_total',len(me.polygons),np.int64),'mi':g(me.polygons,'material_index',len(me.polygons),np.int64),'ed':g(me.edges,'vertices',len(me.edges)*2,np.int64),
       'uv':g(me.uv_layers[0].data,'uv',len(me.loops)*2).reshape(-1,2),'ln':g(me.corner_normals,'vector',len(me.loops)*3).reshape(-1,3),
       'images':[(i.name,i.filepath,os.path.exists(os.path.normpath(bpy.path.abspath(i.filepath)))) for i in bpy.data.images]}
    bm=bmesh.new(); bm.from_mesh(me)
    d['q']={'nonmanifold':sum(1 for e in bm.edges if not e.is_manifold),'boundary':sum(1 for e in bm.edges if e.is_boundary),'zero_area':sum(1 for f in bm.faces if f.calc_area()<1e-12),
            'zero_len_normals':int((np.linalg.norm(d['ln'],axis=1)<1e-6).sum()),'tris':sum(len(p.vertices)-2 for p in me.polygons)}
    # connectivity check of the index ranges
    n=len(d['co']); par=list(range(n))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for a,b in d['ed'].reshape(-1,2):
        a,b=f(a),f(b)
        if a!=b: par[a]=b
    sh={}
    for i in range(n): sh.setdefault(f(i),[]).append(i)
    d['shell_ranges']=sorted((min(v),max(v)+1) for v in sh.values())
    d['tri_idx']=[list(p.vertices) for p in me.polygons]
    return d
A=load(bp); B=load(cp)
r={'mode':mode,'shell_ranges_match_parts':A['shell_ranges']==sorted(PARTS.values())==B['shell_ranges'],
   'topology':{k:bool(A[k].shape==B[k].shape and (A[k]==B[k]).all()) for k in ('lv','ls','lt','mi','ed')},'vertex_count':[len(A['co']),len(B['co'])],'tris':[A['q']['tris'],B['q']['tris']],'parts':{}}
for nm,(a,b) in PARTS.items():
    d=B['co'][a:b]-A['co'][a:b]; L=(A['lv']>=a)&(A['lv']<b)
    r['parts'][nm]={'verts':b-a,'delta_min':d.min(0).round(7).tolist(),'delta_max':d.max(0).round(7).tolist(),'y_changed_max':float(np.abs(d[:,1]).max()),
        'uv_max_abs':float(np.abs(A['uv'][L]-B['uv'][L]).max()),'normal_max_abs':float(np.abs(A['ln'][L]-B['ln'][L]).max()),'material_slots':sorted(set(A['mi'][[i for i in range(len(A['ls'])) if a<=A['lv'][A['ls'][i]]<b]].tolist()))}
ra=A['co'][96:588].reshape(41,12,3); rb=B['co'][96:588].reshape(41,12,3)
ringd=np.abs(rb-ra).max((1,2)); r['arm_rings_unchanged']=[int(i) for i in np.where(ringd<1e-7)[0]]; r['arm_rings_changed']=[int(i) for i in np.where(ringd>=1e-7)[0]]
r['arm_ring_radius_after']=[float(np.linalg.norm(rb[i]-rb[i].mean(0),axis=1).max()) for i in r['arm_rings_changed']]
Lr=(A['lv']>=96+12*min(r['arm_rings_changed']))&(A['lv']<588) if r['arm_rings_changed'] else None
Lk=(A['lv']>=96)&(A['lv']<96+12*min(r['arm_rings_changed'])) if r['arm_rings_changed'] else None
r['arm_normals_changed_rings_max_abs']=float(np.abs(A['ln'][Lr]-B['ln'][Lr]).max()); r['arm_normals_kept_rings_max_abs']=float(np.abs(A['ln'][Lk]-B['ln'][Lk]).max())
def ratios(D):
    c=D['co']; pl,col,sh=c[0:96],c[588:710],c[710:1416]; Hs=sh[:,2].max()-sh[:,2].min(); cb=col[:,2].min(); C=c[96:588].reshape(41,12,3).mean(1)
    return {'Hs':float(Hs),'collar_bottom_z':float(cb),'plate_top_rel_collar_bottom/Hs':float((pl[:,2].max()-cb)/Hs),'plate_bottom_rel_collar_bottom/Hs':float((pl[:,2].min()-cb)/Hs),
      'arm_exit_rel_collar_bottom/Hs':float((C[0,2]-cb)/Hs),'arm_bottom_outer_rel_collar_bottom/Hs':float((C[:,2].min()-0.012-cb)/Hs),
      'arm_end_center':C[40].tolist(),'collar_center_y':float((col[:,1].min()+col[:,1].max())/2),'arm_end_rel_collar':[float(C[40,1]-(col[:,1].min()+col[:,1].max())/2),float(C[40,2]-cb)],
      'max_y_all':float(c[:,1].max()),'max_y_non_plate':float(c[96:,1].max()),'z_min':float(c[:,2].min()),'bbox':[c.min(0).tolist(),c.max(0).tolist()]}
r['f1_before']=ratios(A); r['f1_after']=ratios(B)
def clearance(D):
    c=D['co']; tris=[t for t in D['tri_idx'] if 710<=t[0]<1416]; bv=BVHTree.FromPolygons([tuple(v) for v in c],tris)
    arm=c[96:588]; dmin=1e9; inside=0
    for i,v in enumerate(arm):
        ring=i//12
        if ring>=38: continue     # last rings sit inside the collar by design
        hit=bv.find_nearest(Vector(v)); dmin=min(dmin,hit[3])
    pl=c[0:96]; ptr=[t for t in D['tri_idx'] if t[0]<96]; bp_=BVHTree.FromPolygons([tuple(v) for v in c],ptr)
    pd=min(bp_.find_nearest(Vector(v))[3] for v in c[588:1562])
    return {'arm_rings_0_37_min_distance_to_shade_m':float(dmin),'cup_group_min_distance_to_plate_m':float(pd)}
r['clearance_before']=clearance(A); r['clearance_after']=clearance(B)
r['other']={'object':[[A['name'],A['loc'],A['rot'],A['scale']],[B['name'],B['loc'],B['rot'],B['scale']]],'materials':[A['materials'],B['materials']],'uv_layers':[A['uvl'],B['uvl']],
  'custom_normals':[A['custom'],B['custom']],'units':[A['units'],B['units']],'uv_all_max_abs':float(np.abs(A['uv']-B['uv']).max()),'uv_negative_count':[int((A['uv']<0).sum()),int((B['uv']<0).sum())],
  'quality':[A['q'],B['q']],'images':[A['images'],B['images']]}
json.dump(r,open(out,'w'),indent=1,default=lambda x:x.tolist() if hasattr(x,'tolist') else str(x))
print(json.dumps({k:r[k] for k in ('shell_ranges_match_parts','topology','tris','arm_rings_changed','arm_normals_changed_rings_max_abs','arm_normals_kept_rings_max_abs')}))
for k,v in r['parts'].items(): print(k,v['delta_min'],v['delta_max'],v['uv_max_abs'],v['normal_max_abs'])
for k in ('plate_top_rel_collar_bottom/Hs','plate_bottom_rel_collar_bottom/Hs','arm_exit_rel_collar_bottom/Hs','arm_bottom_outer_rel_collar_bottom/Hs','arm_end_rel_collar','max_y_non_plate','z_min'): print(k,r['f1_before'][k],r['f1_after'][k])
print(r['clearance_before'],r['clearance_after']); print(r['other']['quality'],r['other']['uv_negative_count'],r['other']['images'])
