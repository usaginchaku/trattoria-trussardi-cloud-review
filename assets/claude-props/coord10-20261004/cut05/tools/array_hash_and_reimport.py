# per-file: sha256 of every array/value in the FBX tree (by path) for old and new, plus Blender re-import comparison (geometry/UV/normals).
import sys,os,json,hashlib,bpy,addon_utils,numpy as np
p=[m for m in addon_utils.modules() if m.__name__=='io_scene_fbx'][0].__file__; sys.path.insert(0,os.path.dirname(os.path.dirname(p)))
from io_scene_fbx import parse_fbx
pairs=json.loads(sys.argv[-2]); out={}
def arrays(path):
    root,_=parse_fbx.parse(path); A={}
    def walk(e,pth):
        for i,(v,t) in enumerate(zip(e.props,e.props_type)):
            if chr(t) in 'fdilbc': A[f'{pth}/p{i}']=hashlib.sha256(np.ascontiguousarray(np.asarray(v)).tobytes()).hexdigest()
        cnt={}
        for c in e.elems:
            nm=c.id.decode(errors='replace'); k=cnt.get(nm,0); cnt[nm]=k+1; walk(c,pth+'/'+nm+(f'[{k}]' if k else ''))
    walk(root,''); return A
def imp(path):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=path)
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
    return {'name':o.name,'co':np.array([v.co[:] for v in me.vertices]),'loops':np.array([l.vertex_index for l in me.loops]),'cn':np.array([c.vector[:] for c in me.corner_normals]),
            'uv':{u.name:np.array([d.uv[:] for d in u.data]) for u in me.uv_layers},'mats':[m.name for m in me.materials],'imgs':sorted(i.name for i in bpy.data.images),'tf':(tuple(o.location),tuple(o.rotation_euler),tuple(o.scale))}
for k,(a,b) in pairs.items():
    A,B=arrays(a),arrays(b); ia,ib=imp(a),imp(b)
    out[k]={'old_sha256':hashlib.sha256(open(a,'rb').read()).hexdigest(),'new_sha256':hashlib.sha256(open(b,'rb').read()).hexdigest(),
      'arrays_compared':len(A),'array_value_hashes_identical':A==B,'array_hashes':A,
      'reimport':{'object_name':[ia['name'],ib['name']],'verts_identical':bool(np.array_equal(ia['co'],ib['co'])),'loop_order_identical':bool(np.array_equal(ia['loops'],ib['loops'])),
        'corner_normals_identical':bool(np.array_equal(ia['cn'],ib['cn'])),'uv_identical':{n:bool(np.array_equal(ia['uv'][n],ib['uv'][n])) for n in ia['uv']},
        'materials':[ia['mats'],ib['mats']],'images':[ia['imgs'],ib['imgs']],'transform_identical':ia['tf']==ib['tf'],'bbox':[ib['co'].min(0).round(5).tolist(),ib['co'].max(0).round(5).tolist()]}}
    r=out[k]['reimport']; print('H',k,out[k]['array_value_hashes_identical'],out[k]['arrays_compared'],r['object_name'],r['verts_identical'],r['loop_order_identical'],r['corner_normals_identical'],r['uv_identical'],r['transform_identical'])
json.dump(out,open(sys.argv[-1],'w'),indent=1)
