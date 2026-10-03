# penetration test: shrink every triangle 2% toward its centroid, then BVH self-overlap of non-adjacent pairs.
# touching contacts (shared edges between separate shells, coplanar seams) disappear; real crossings remain.
import bpy,sys,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
res={}
for p in sys.argv[sys.argv.index('--')+1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p)
    me=[x for x in bpy.data.objects if x.type=='MESH'][0].data
    co=[v.co.copy() for v in me.vertices]; V=[]; F=[]
    for q in me.polygons:
        c=sum((co[i] for i in q.vertices),Vector())/len(q.vertices); b=len(V)
        V+= [c+(co[i]-c)*0.98 for i in q.vertices]; F.append(list(range(b,b+len(q.vertices))))
    t=BVHTree.FromPolygons(V,F,all_triangles=False,epsilon=0.0); ov=t.overlap(t)
    pv=[set(q.vertices) for q in me.polygons]
    real=[(a,b) for a,b in ov if a<b and not (pv[a]&pv[b])]
    ys=[round(float(np.mean([co[i].y for i in me.polygons[a].vertices])),4) for a,b in real[:5]]
    print('PEN',p.split('/')[-1],len(real),ys)
