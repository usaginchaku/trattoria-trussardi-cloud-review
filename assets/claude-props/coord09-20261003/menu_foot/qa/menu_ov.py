import bpy,bmesh,numpy as np,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def load(p):
    bpy.ops.wm.open_mainfile(filepath=p); me=bpy.data.objects['MenuStand'].data
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table(); return bm
res={}
for tag in ('M0','M1lin','M1'):
    bm=load(f'c9/menu_{tag}.blend')
    def bvh(r):
        b=bmesh.new(); vm={}; fl=[]
        for f in bm.faces:
            if r[0]<=f.verts[0].index<=r[1]:
                vv=[]
                for v in f.verts:
                    if v.index not in vm: vm[v.index]=b.verts.new(v.co)
                    vv.append(vm[v.index])
                b.faces.new(vv); fl.append(f)
        return BVHTree.FromBMesh(b),fl
    post=bvh((0,337)); legs=[bvh((338,709)),bvh((710,1081)),bvh((1082,1453))]
    out=[]
    for i,(t,fl) in enumerate(legs):
        for j,(t2,fl2) in [(-1,post)]+[(k,legs[k]) for k in range(i+1,3)]:
            for a,b in t.overlap(t2):
                c=(fl[a].calc_center_median()+fl2[b].calc_center_median())/2
                out.append((i,j,float(np.hypot(c.x,c.y)),float(c.z)))
    o=np.array([(x[2],x[3]) for x in out])
    res[tag]={'pairs':len(out),'max_r_from_axis':float(o[:,0].max()),'max_z':float(o[:,1].max()),'n_r_gt_0.045':int((o[:,0]>0.045).sum())}
    # nonmanifold location
    nm=[e for e in bm.edges if not e.is_manifold]; res[tag]['nonmanifold']=[(e.verts[0].index,e.verts[1].index) for e in nm]
print(res)
