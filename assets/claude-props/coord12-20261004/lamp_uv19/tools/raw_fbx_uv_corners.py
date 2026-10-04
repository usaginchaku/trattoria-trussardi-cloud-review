# raw FBX (Blender's parse_fbx, before any importer processing): expand UV through UVIndex per polygon-vertex (raw 0-based corner order)
# and list the corners whose UV differ; map them to raw triangles (corner // 3) and check the 3D area of the differing triangles.
# usage: blender-python raw_fbx_uv_corners.py -- in.fbx fixed.fbx out.json
import sys,os,json,bpy,addon_utils
import numpy as np
p=[m for m in addon_utils.modules() if m.__name__=='io_scene_fbx'][0].__file__; sys.path.insert(0,os.path.dirname(os.path.dirname(p)))
from io_scene_fbx import parse_fbx
a,b,out=sys.argv[sys.argv.index('--')+1:]
def grab(f):
    root,_=parse_fbx.parse(f); d={}
    def walk(e,path):
        if e.id in (b'UV',b'UVIndex',b'PolygonVertexIndex',b'Vertices'): d.setdefault(e.id.decode(),np.array(e.props[0]))
        for c in e.elems: walk(c,path)
    walk(root,''); uv=d['UV'].reshape(-1,2)[d['UVIndex']]; pvi=d['PolygonVertexIndex']; vi=np.where(pvi<0,-pvi-1,pvi); V=d['Vertices'].reshape(-1,3)
    return uv,vi,V
ua,via,Va=grab(a); ub,vib,Vb=grab(b)
diff=np.where(np.any(ua!=ub,axis=1))[0]; tris=sorted(set((diff//3).tolist()))
def area(t,vi,V): q=V[vi[3*t:3*t+3]]; return 0.5*float(np.linalg.norm(np.cross(q[1]-q[0],q[2]-q[0])))
def uarea(t,u): q=u[3*t:3*t+3]; return 0.5*abs((q[1,0]-q[0,0])*(q[2,1]-q[0,1])-(q[1,1]-q[0,1])*(q[2,0]-q[0,0]))
r={'corners_total':len(ua),'corner_order_identical':bool(np.array_equal(via,vib)),'vertices_identical':bool(np.array_equal(Va,Vb)),'changed_corners':diff.tolist(),'changed_corner_count':len(diff),
   'changed_triangles':tris,'U_identical_all':bool(np.array_equal(ua[:,0],ub[:,0])),'raw_tri_area3d_sum':sum(area(t,vib,Vb) for t in tris),
   'uv_area_before_zero':sum(1 for t in tris if uarea(t,ua)<1e-14),'uv_area_after_zero':sum(1 for t in tris if uarea(t,ub)<1e-14),
   'note':'area in raw FBX vertex units (this exporter writes metres with UnitScaleFactor 100; matches the 0.00189 m2 reported by Root)'}
json.dump(r,open(out,'w'),indent=1); print({k:(v if k not in ('changed_corners',) else (v[:6]+['...']+v[-6:])) for k,v in r.items()})
