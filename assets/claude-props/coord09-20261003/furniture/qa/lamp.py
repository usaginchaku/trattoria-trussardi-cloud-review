# COORD09 wall lamp shade candidates (Codex source ARCH01 Curved/Straight). Shade material only; metal untouched; UV untouched.
#  L1: shade proportion -> straight wall shortened (z-scale above the bottom taper) so width/height ~1.05; width, bottom taper, bracket unchanged
#  L2: shade flare -> straight wall becomes conical (bottom of straight part narrowed, top rim unchanged); height unchanged
import bpy,bmesh,sys,json,math,numpy as np
from mathutils import Vector,Matrix
src,objname,mode,tag=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=src)
o=bpy.data.objects[objname]; me=o.data
uv_before=[tuple(l.uv) for l in me.uv_layers[0].data]; cn=[Vector(c.vector) for c in me.corner_normals]
isS=lambda p: me.materials[p.material_index].name.startswith('Shade')
sv=sorted({v for p in me.polygons if isS(p) for v in p.vertices}); mv_=sorted({v for p in me.polygons if not isS(p) for v in p.vertices})
co=np.array([v.co[:] for v in me.vertices]); S=co[sv]
cx,cy=S[:,0].mean(),S[:,1].mean(); z0,ztop=S[:,2].min(),S[:,2].max()
ZC=z0+0.084   # start of straight wall (measured: taper ends at +0.084 m)
W=2*np.hypot(S[:,0]-cx,S[:,1]-cy).max(); H0=ztop-z0
info={'mode':mode,'shade_width_m':float(W),'shade_height_before_m':float(H0),'wh_before':float(W/H0)}
J={}
new=co.copy()
for i in sv:
    x,y,z=co[i]
    if z<=ZC+1e-6: continue
    if mode=='L1':
        target_h=W/1.05; k=(target_h-(ZC-z0))/(ztop-ZC)
        new[i,2]=ZC+k*(z-ZC); J[i]=Matrix(((1,0,0),(0,1,0),(0,0,k)))
        info['wall_scale_z']=k; info['shade_height_after_m']=float(target_h); info['wh_after']=float(W/target_h)
    elif mode=='L2':
        A=0.14  # radius reduction at bottom of straight wall (fraction), 0 at the rim
        t=(ztop-z)/(ztop-ZC); f=1-A*t; df=A/(ztop-ZC)
        dx,dy=x-cx,y-cy; new[i,0]=cx+f*dx; new[i,1]=cy+f*dy
        J[i]=Matrix(((f,0,df*dx),(0,f,df*dy),(0,0,1)))
        info['flare_radius_reduction_at_wall_bottom']=A
if mode=='L2':
    # keep the taper joined: scale the taper ring radii smoothly toward the reduced wall-bottom radius
    for i in sv:
        x,y,z=co[i]
        if z>ZC+1e-6 or z<=z0+1e-6: continue
        t=(z-z0)/(ZC-z0); f=1-0.14*t**2; df=-0.14*2*t/(ZC-z0)
        dx,dy=x-cx,y-cy; new[i,0]=cx+f*dx; new[i,1]=cy+f*dy; J[i]=Matrix(((f,0,df*dx),(0,f,df*dy),(0,0,1)))
for i in J: me.vertices[i].co=new[i]
me.update()
loops=[]
for p in me.polygons:
    for li in p.loop_indices:
        vi=me.loops[li].vertex_index
        loops.append((J[vi].inverted().transposed()@cn[li]).normalized() if vi in J else cn[li])
me.normals_split_custom_set(loops); me.update()
bm=bmesh.new(); bm.from_mesh(me)
co2=np.array([v.co[:] for v in me.vertices]); S2=co2[sv]
info.update(shade_verts=len(sv),moved=len(J),metal_unchanged=bool(np.allclose(co2[mv_],co[mv_])),dims_before=list(map(float,np.ptp(co,0))),dims_after=list(map(float,np.ptp(co2,0))),
  shade_top_after=float(S2[:,2].max()),uv_unchanged=uv_before==[tuple(l.uv) for l in me.uv_layers[0].data],tris=sum(len(p.vertices)-2 for p in me.polygons),
  nonmanifold=sum(1 for e in bm.edges if not e.is_manifold),boundary=sum(1 for e in bm.edges if e.is_boundary),zero_area=sum(1 for f in bm.faces if f.calc_area()<1e-12),
  zero_len_normals=sum(1 for c in me.corner_normals if Vector(c.vector).length<1e-6))
bpy.ops.wm.save_as_mainfile(filepath=f'c9/lamp_{tag}.blend',compress=False)
json.dump(info,open(f'c9/lamp_{tag}.json','w'),indent=1); print(json.dumps(info))
