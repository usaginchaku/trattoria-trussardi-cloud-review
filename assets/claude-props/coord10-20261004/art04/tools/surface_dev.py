# A6 vs A5: distance of every A6 vertex from the A5 surface. Only groove-bottom vertices may leave the surface,
# and only on the two flat front bands (y=-0.036 / -0.031) by at most the groove depth.
import bpy,sys,json,numpy as np
from mathutils.bvhtree import BVHTree
a,b,outp=sys.argv[-3:]
def load(p):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p)
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; return o.data
ma=load(a); ta=BVHTree.FromPolygons([v.co.copy() for v in ma.vertices],[list(p.vertices) for p in ma.polygons])
mb=load(b)
d=[]; off=[]
for v in mb.vertices:
    loc,n,i,dist=ta.find_nearest(v.co); d.append(dist)
    if dist>1e-6: off.append((round(v.co.x,4),round(v.co.y,5),round(v.co.z,4),round(dist,5)))
ys=sorted({o[1] for o in off})
import collections
r={'dist_histogram_by_y':{str(k):[len(g),round(max(x[3] for x in g),6)] for k,g in collections.defaultdict(list,{y:[o for o in off if o[1]==y] for y in ys}).items()},'verts_off_A5_surface':len(off),'max_dist_m':float(max(d)),'y_levels_of_off_verts':ys,'verts_deeper_than_0.1mm':sum(1 for o in off if o[3]>1e-4),'all_deeper_verts_are_groove_bottoms_on_bands':all(abs(o[1]-(-0.0345))<2e-5 or abs(o[1]-(-0.0295))<2e-5 for o in off if o[3]>1e-4)}
json.dump(r,open(outp,'w'),indent=1); print('SD',json.dumps(r))
