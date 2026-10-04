# independent check (new process): input vs UVFIX, blend-vs-blend or FBX-vs-FBX (default importer). Bit comparisons with numpy array_equal.
# usage: blender-python verify_uvfix.py -- blend|fbx input fixed out.json
import bpy,bmesh,sys,json,os
import numpy as np
mode,ip,fp,out=sys.argv[sys.argv.index('--')+1:]
def load(p):
    if mode=='blend': bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p))
    else: bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=os.path.abspath(p))
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
    def g(c,a,n,dt=np.float32): x=np.empty(n,dt); c.foreach_get(a,x); return x
    bm=bmesh.new(); bm.from_mesh(me)
    return {'o':[o.name,list(o.location),list(o.rotation_euler),list(o.scale),[list(r) for r in o.matrix_world]],'mats':[m.name for m in me.materials],'uvl':[u.name for u in me.uv_layers],
      'custom':me.has_custom_normals,'units':[bpy.context.scene.unit_settings.system,bpy.context.scene.unit_settings.scale_length],
      'co':g(me.vertices,'co',len(me.vertices)*3).reshape(-1,3),'lv':g(me.loops,'vertex_index',len(me.loops),np.int32),'ls':g(me.polygons,'loop_start',len(me.polygons),np.int32),
      'lt':g(me.polygons,'loop_total',len(me.polygons),np.int32),'mi':g(me.polygons,'material_index',len(me.polygons),np.int32),'ed':g(me.edges,'vertices',len(me.edges)*2,np.int32),
      'sm':g(me.polygons,'use_smooth',len(me.polygons),bool),'uv':g(me.uv_layers[0].data,'uv',len(me.loops)*2).reshape(-1,2),'ln':g(me.corner_normals,'vector',len(me.loops)*3).reshape(-1,3),
      'fv':[tuple(p.vertices) for p in me.polygons],'images':[(i.name,i.filepath,os.path.exists(os.path.normpath(bpy.path.abspath(i.filepath)))) for i in bpy.data.images],
      'q':{'nonmanifold':sum(1 for e in bm.edges if not e.is_manifold),'boundary':sum(1 for e in bm.edges if e.is_boundary)}}
A=load(ip); B=load(fp)
TOP=set(range(1070,1086)); WALL=set(range(1390,1406))
capf=[i for i,f in enumerate(A['fv']) if set(f)<=TOP or set(f)<=WALL]
capL=np.zeros(len(A['lv']),bool)
for i in capf: capL[A['ls'][i]:A['ls'][i]+A['lt'][i]]=True
armL=A['lv']>=1070
r={'mode':mode,'bit_equal':{k:bool(np.array_equal(A[k],B[k])) for k in ('co','lv','ls','lt','mi','ed','sm','ln')},
 'object_equal':A['o']==B['o'],'materials_equal':A['mats']==B['mats'],'uv_layers':[A['uvl'],B['uvl']],'custom_normals':[A['custom'],B['custom']],'units':[A['units'],B['units']],
 'cap_faces':capf,'cap_corners':int(capL.sum()),
 'uv_unchanged_outside_caps_bit':bool(np.array_equal(A['uv'][~capL],B['uv'][~capL])),'arm_side_uv_bit':bool(np.array_equal(A['uv'][armL&~capL],B['uv'][armL&~capL])),
 'non_arm_uv_bit':bool(np.array_equal(A['uv'][~armL],B['uv'][~armL])),'all_U_bit_equal':bool(np.array_equal(A['uv'][:,0],B['uv'][:,0])),
 'changed_corner_count':int((np.any(A['uv']!=B['uv'],axis=1)).sum()),'changed_corners_subset_of_caps':bool(np.all(capL[np.any(A['uv']!=B['uv'],axis=1)])),'quality':[A['q'],B['q']],'images':[A['images'],B['images']]}
def a2(t): return 0.5*abs((t[1][0]-t[0][0])*(t[2][1]-t[0][1])-(t[1][1]-t[0][1])*(t[2][0]-t[0][0]))
def a3(t): return 0.5*float(np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0])))
rows=[]; proj_err=0.0
for i in capf:
    L=list(range(A['ls'][i],A['ls'][i]+A['lt'][i])); vs=A['fv'][i]; top=set(vs)<=TOP
    uvb=B['uv'][L]; pts=B['co'][list(vs)]
    for l,v in zip(L,vs):
        exp=B['co'][v][1] if top else B['co'][v][2]; proj_err=max(proj_err,abs(float(B['uv'][l][1])-float(exp)))
    rows.append({'face':i,'cap':'top' if top else 'wall','uv_area_before':a2(A['uv'][L]),'uv_area_after':a2(uvb),'area3d':a3(pts),'finite':bool(np.isfinite(uvb).all())})
r['caps']={'uv_area_zero_before':sum(1 for x in rows if x['uv_area_before']<1e-14),'uv_area_zero_after':sum(1 for x in rows if x['uv_area_after']<1e-14),'all_finite':all(x['finite'] for x in rows),
  'uv_area_sum_after':sum(x['uv_area_after'] for x in rows),'area3d_sum':sum(x['area3d'] for x in rows),'max_rel_area_diff':max(abs(x['uv_area_after']-x['area3d'])/x['area3d'] for x in rows),
  'max_V_vs_projection_abs':proj_err,'projection':'top cap V = vertex y, wall cap V = vertex z, U unchanged (= vertex x)','faces':rows}
json.dump(r,open(out,'w'),indent=1,default=lambda x:x.tolist() if hasattr(x,'tolist') else str(x))
print(json.dumps({k:v for k,v in r.items() if k not in ('caps','cap_faces','images')}),json.dumps({k:v for k,v in r['caps'].items() if k!='faces'}))
