# shrink-2% triangle crossing test, grouped by the parts involved (crown boxes / new tier / others)
import bpy,sys,collections,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def part(fv,nf0,fi):
    if fi>=nf0: return 'new_mid_tier'
    s=set(fv)
    if s<=set(range(384,480)): return 'cap(top plate)'
    if s<=set(range(576,672)): return 'lower_tier(mould)'
    if s<=set(range(96,288)): return 'side_panels'
    if s<=set(range(0,96)): return 'back_panel'
    if s<=set(range(672,2132)): return 'doors/panes/knobs'
    return 'other'
for p in sys.argv[sys.argv.index('--')+1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p)
    me=[x for x in bpy.data.objects if x.type=='MESH'][0].data; co=[v.co.copy() for v in me.vertices]; V=[];F=[]
    for q in me.polygons:
        c=sum((co[i] for i in q.vertices),Vector())/len(q.vertices); b=len(V); V+=[c+(co[i]-c)*0.98 for i in q.vertices]; F.append(list(range(b,b+len(q.vertices))))
    t=BVHTree.FromPolygons(V,F,all_triangles=False,epsilon=0.0); pv=[set(q.vertices) for q in me.polygons]
    real=[(a,b) for a,b in t.overlap(t) if a<b and not (pv[a]&pv[b])]
    cnt=collections.Counter(tuple(sorted((part(me.polygons[a].vertices,4220,a),part(me.polygons[b].vertices,4220,b)))) for a,b in real)
    print('PP',p.split('/')[-3] if 'C4' in p else 'C3m',len(real),dict(cnt))
