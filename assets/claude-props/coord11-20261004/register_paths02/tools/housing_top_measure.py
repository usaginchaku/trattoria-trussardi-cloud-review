# measured top of the upper housing shell (z of the highest vertex of the slot0 shell spanning z 0.068..~0.245), input FBX vs R1 blend
import bpy,sys,json
import numpy as np
fin,bl,out=sys.argv[sys.argv.index('--')+1:]
def shells(me):
    n=len(me.vertices); par=list(range(n))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for e in me.edges:
        a,b=f(e.vertices[0]),f(e.vertices[1])
        if a!=b: par[a]=b
    d={}
    for i in range(n): d.setdefault(f(i),[]).append(i)
    return d.values()
def top(me):
    co=np.array([v.co[:] for v in me.vertices],np.float64)
    hs=[vs for vs in shells(me) if abs(co[vs][:,2].min()-0.068)<1e-3 and co[vs][:,2].max()>0.24]
    assert len(hs)==1; c=co[hs[0]]; return {'housing_z_max_m':float(c[:,2].max()),'housing_bbox_min':c.min(0).tolist(),'housing_bbox_max':c.max(0).tolist(),'overall_z_max_m':float(co[:,2].max())}
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=fin); a=top([o for o in bpy.data.objects if o.type=='MESH'][0].data)
bpy.ops.wm.open_mainfile(filepath=bl); b=top(bpy.data.objects['Register'].data)
r={'input_FBX':a,'R1_blend':b,'housing_top_delta_mm':round((b['housing_z_max_m']-a['housing_z_max_m'])*1000,4),
   'note':'R1 build used core top 0.2431 + bevel offset 0.002 = 0.2451 (bevel offsets inward along the face normals); the original rounded box reaches 0.2454. Overall bbox top 0.25 comes from the unchanged top cap and is kept.'}
json.dump(r,open(out,'w'),indent=1); print(r['housing_top_delta_mm'],a['housing_z_max_m'],b['housing_z_max_m'],a['overall_z_max_m'],b['overall_z_max_m'])
