# COORD09 water glass: single factor = bowl width (radial). Height, stem, foot, mouth height, topology, UV unchanged.
import bpy,sys,json,math,numpy as np
from mathutils import Vector,Matrix
a=sys.argv[sys.argv.index('--')+1:]; s_max,tag=float(a[0]),a[1]; MODE=a[2] if len(a)>2 else 'smooth'
bpy.ops.wm.open_mainfile(filepath='cand/Trussardi_Reference_Props_v02_waterfix_candidate.blend')
o=bpy.data.objects['06_Water_Glass_Mesh']; me=o.data
uv_before={u.name:[tuple(l.uv) for l in u.data] for u in me.uv_layers}
Z0,Z1=(0.0600,0.0850) if MODE=='smooth' else (0.0600,0.1050)   # blend zone: stem junction (unchanged) -> full scale
def g(z):
    if z<=Z0: return 1.0,0.0
    if z>=Z1: return s_max,0.0
    t=(z-Z0)/(Z1-Z0)
    if MODE=='smooth': sm=t*t*(3-2*t); dsm=6*t*(1-t)/(Z1-Z0)
    else: sm=math.sin(t*math.pi/2); dsm=math.cos(t*math.pi/2)*math.pi/2/(Z1-Z0)
    return 1+(s_max-1)*sm,(s_max-1)*dsm
cn=[Vector(c.vector) for c in me.corner_normals]
newco=[]; Jit={}
for v in me.vertices:
    x,y,z=v.co; gz,dg=g(z)
    newco.append((gz*x,gz*y,z))
    J=Matrix(((gz,0,dg*x),(0,gz,dg*y),(0,0,1)))
    Jit[v.index]=J.inverted().transposed()
for v,c in zip(me.vertices,newco): v.co=c
loops_n=[]
for li,l in enumerate(me.loops):
    n=(Jit[l.vertex_index]@cn[li]).normalized(); loops_n.append(n)
me.normals_split_custom_set(loops_n); me.update()
co=np.array([v.co[:] for v in me.vertices]); r=np.hypot(co[:,0],co[:,1])
bowl=co[:,2]>0.0615
rim=np.abs(co[:,2]-co[:,2].max())<1e-5
# wall thickness at z=115 mm level (outer-inner)
lev=np.abs(co[:,2]-0.1148)<1e-4; rr=np.unique(r[lev].round(6))
info={'tag':tag,'profile':MODE,'bowl_radial_scale':s_max,'blend_zone_z_m':[Z0,Z1],'dims_m':list(map(float,np.ptp(co,0))),'zmin':float(co[:,2].min()),
 'bowl_max_diameter_m':float(2*r[bowl].max()),'bowl_height_m':float(co[:,2].max()-0.0607),'mouth_outer_diameter_m':float(2*r[rim].max()),
 'width_to_height':float(2*r[bowl].max()/(co[:,2].max()-0.0607)),'mouth_to_max':float(r[rim].max()/r[bowl].max()),
 'wall_thickness_at_115mm_m':float(rr.max()-rr.min()),'tris':sum(len(p.vertices)-2 for p in me.polygons),
 'uv_unchanged':uv_before=={u.name:[tuple(l.uv) for l in u.data] for u in me.uv_layers},'custom_normals':me.has_custom_normals}
import bmesh
bm=bmesh.new(); bm.from_mesh(me)
info.update(nonmanifold=sum(1 for e in bm.edges if not e.is_manifold),boundary=sum(1 for e in bm.edges if e.is_boundary),zero_area=sum(1 for f in bm.faces if f.calc_area()<1e-12))
bpy.ops.wm.save_as_mainfile(filepath=f'c9/water_{tag}.blend',compress=False)
json.dump(info,open(f'c9/water_{tag}.json','w'),indent=1); print(json.dumps(info))
