# independent check (new process): B_UVFIX vs COLLARTIP_C1, blend-vs-blend or FBX-vs-FBX. parts: plate 0-95, collar 96-217, shade 218-923,
# diffuser 924-1069, arm 1070-1405. usage: blender-python verify_collartip_c1.py -- blend|fbx base c1 out.json
import bpy,bmesh,sys,json,os,math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
mode,bp,cp,out=sys.argv[sys.argv.index('--')+1:]
def load(p):
    if mode=='blend': bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p))
    else: bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=os.path.abspath(p))
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
    def g(c,a,n,dt=np.float32): x=np.empty(n,dt); c.foreach_get(a,x); return x
    bm=bmesh.new(); bm.from_mesh(me)
    return {'o':[o.name,[list(r) for r in o.matrix_world]],'mats':[m.name for m in me.materials],'uvl':[u.name for u in me.uv_layers],'custom':me.has_custom_normals,
      'units':[bpy.context.scene.unit_settings.system,bpy.context.scene.unit_settings.scale_length],'co':g(me.vertices,'co',len(me.vertices)*3).reshape(-1,3),
      'lv':g(me.loops,'vertex_index',len(me.loops),np.int32),'ls':g(me.polygons,'loop_start',len(me.polygons),np.int32),'lt':g(me.polygons,'loop_total',len(me.polygons),np.int32),
      'mi':g(me.polygons,'material_index',len(me.polygons),np.int32),'ed':g(me.edges,'vertices',len(me.edges)*2,np.int32),'sm':g(me.polygons,'use_smooth',len(me.polygons),bool),
      'uv':g(me.uv_layers[0].data,'uv',len(me.loops)*2).reshape(-1,2),'ln':g(me.corner_normals,'vector',len(me.loops)*3).reshape(-1,3),
      'fn':np.array([p.normal[:] for p in me.polygons]),'fv':[list(p.vertices) for p in me.polygons],
      'images':[(i.name,i.filepath,os.path.exists(os.path.normpath(bpy.path.abspath(i.filepath)))) for i in bpy.data.images],
      'q':{'nonmanifold':sum(1 for e in bm.edges if not e.is_manifold),'boundary':sum(1 for e in bm.edges if e.is_boundary),'zero_area':sum(1 for f in bm.faces if f.calc_area()<1e-12)}}
A=load(bp); B=load(cp)
colV=np.zeros(len(A['co']),bool); colV[96:218]=True; colL=colV[A['lv']]
moved=np.where(np.any(A['co']!=B['co'],axis=1))[0]
r={'mode':mode,'topology_bit':{k:bool(np.array_equal(A[k],B[k])) for k in ('lv','ls','lt','mi','ed','sm')},'object_equal':A['o']==B['o'],'materials_equal':A['mats']==B['mats'],
 'uv0_all_bit_equal':bool(np.array_equal(A['uv'],B['uv'])),'non_collar_positions_bit':bool(np.array_equal(A['co'][~colV],B['co'][~colV])),
 'non_collar_normals_bit':bool(np.array_equal(A['ln'][~colL],B['ln'][~colL])),'moved_vertices':moved.tolist(),'moved_count':len(moved),'moved_all_in_collar_bottom_ring':bool(all(96<=i<218 and abs(A['co'][i][2]-0.145)<1e-5 for i in moved)),
 'moved_z_unchanged':bool(np.array_equal(A['co'][moved][:,2],B['co'][moved][:,2])),'custom':[A['custom'],B['custom']],'units':[A['units'],B['units']],'uv_layers':[A['uvl'],B['uvl']],'quality':[A['q'],B['q']],'images':[A['images'],B['images']]}
cf=[i for i,f in enumerate(B['fv']) if 96<=f[0]<218]
ang=[];dmin=1
for i in cf:
    n=B['fn'][i]
    for l in range(B['ls'][i],B['ls'][i]+B['lt'][i]):
        d=float(np.dot(B['ln'][l],n)/np.linalg.norm(B['ln'][l])); dmin=min(dmin,d); ang.append(math.degrees(math.acos(max(-1,min(1,d)))))
angA=[]
for i in cf:
    n=A['fn'][i]
    for l in range(A['ls'][i],A['ls'][i]+A['lt'][i]): angA.append(math.degrees(math.acos(max(-1,min(1,float(np.dot(A['ln'][l],n)/np.linalg.norm(A['ln'][l])))))))
r['collar_normals']={'loops':len(ang),'min_dot_loop_vs_face':dmin,'max_angle_after_deg':max(ang),'max_angle_before_deg':max(angA),'collar_normal_max_abs_change':float(np.abs(A['ln'][colL]-B['ln'][colL]).max())}
c=B['co']; col=c[96:218]; cy=(col[:,1].min()+col[:,1].max())/2; arm=c[1070:1406]
tree=BVHTree.FromPolygons([tuple(v) for v in c],[f for f in B['fv'] if 96<=f[0]<218])
inside=lambda v:all(tree.ray_cast(Vector(v),Vector(d))[0] is not None for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1)))
top=arm[arm[:,2]>arm[:,2].max()-0.002]; near=arm[(arm[:,2]>0.1449)&(arm[:,2]<0.1451)]
rad=lambda P:np.hypot(P[:,0],P[:,1]-cy)
bot_r=float(rad(col[np.abs(col[:,2]-0.145)<1e-4]).max())
armr=float(rad(arm[(arm[:,2]>=0.140)&(np.abs(arm[:,1]-cy)<0.03)]).max())
r['connection']={'arm_top_verts_inside_collar':int(sum(inside(v) for v in top)),'arm_top_verts':len(top),'collar_bottom_radius':bot_r,'arm_max_radius_above_z0.140':armr,'margin_m':bot_r-armr,
 'collar_z':[float(col[:,2].min()),float(col[:,2].max())],'max_y_non_plate':float(c[96:,1].max()),'verts_y_gt_0':int((c[:,1]>1e-6).sum())}
json.dump(r,open(out,'w'),indent=1,default=lambda x:x.tolist() if hasattr(x,'tolist') else str(x))
print(json.dumps({k:v for k,v in r.items() if k not in ('moved_vertices','images')}))
