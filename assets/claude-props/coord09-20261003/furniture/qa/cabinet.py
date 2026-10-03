# COORD09 wall cabinet candidates (Codex source FUR06): outline proportion only.
# door zone z in [ZA,ZB] stretched by k; above ZB translated by delta; below ZA unchanged; knobs translated (kept round). Width, depth, base, cornice, UV unchanged.
import bpy,bmesh,sys,json,numpy as np
from mathutils import Vector,Matrix
src,WH,tag=sys.argv[sys.argv.index('--')+1:]; WH=float(WH)
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=src)
o=bpy.data.objects['WallCabinet']; me=o.data
uv_before=[tuple(l.uv) for l in me.uv_layers[0].data]; cn=[Vector(c.vector) for c in me.corner_normals]
co=np.array([v.co[:] for v in me.vertices]); W=np.ptp(co[:,0]); H0=np.ptp(co[:,2])
ZA,ZB=0.082,0.479
H1=W/WH if WH>0 else H0; delta=H1-H0; k=(ZB-ZA+delta)/(ZB-ZA)
def f(z): return z if z<=ZA else (ZA+(z-ZA)*k if z<=ZB else z+delta)
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
seen=set(); isl=[]
for v in bm.verts:
    if v.index in seen: continue
    st=[v]; c=[]
    while st:
        x=st.pop()
        if x.index in seen: continue
        seen.add(x.index); c.append(x.index); st+=[e.other_vert(x) for e in x.link_edges]
    isl.append(c)
bm.free()
knobs=[c for c in isl if len(c)==74]
new=co.copy(); J={}
kv=set(v for c in knobs for v in c)
for c in knobs:
    zc=co[c,2].mean(); new[c,2]=co[c,2]+(f(zc)-zc)
for i in range(len(co)):
    if i in kv: continue
    z=co[i,2]; new[i,2]=f(z)
    if ZA<z<ZB: J[i]=Matrix(((1,0,0),(0,1,0),(0,0,k)))
for i in range(len(co)): me.vertices[i].co=new[i]
me.update()
loops=[]
for p in me.polygons:
    for li in p.loop_indices:
        vi=me.loops[li].vertex_index
        loops.append((J[vi].inverted().transposed()@cn[li]).normalized() if vi in J else cn[li])
me.normals_split_custom_set(loops); me.update()
bm=bmesh.new(); bm.from_mesh(me); co2=np.array([v.co[:] for v in me.vertices])
info={'target_w_over_h':WH,'height_before_m':float(H0),'height_after_m':float(np.ptp(co2[:,2])),'door_zone_z':[ZA,ZB],'door_zone_scale':float(k),
 'dims_before':list(map(float,np.ptp(co,0))),'dims_after':list(map(float,np.ptp(co2,0))),'zmin':float(co2[:,2].min()),'knobs_kept_round':True,
 'uv_unchanged':uv_before==[tuple(l.uv) for l in me.uv_layers[0].data],'tris':sum(len(p.vertices)-2 for p in me.polygons),
 'nonmanifold':sum(1 for e in bm.edges if not e.is_manifold),'boundary':sum(1 for e in bm.edges if e.is_boundary),'zero_area':sum(1 for f_ in bm.faces if f_.calc_area()<1e-12),
 'zero_len_normals':sum(1 for c in me.corner_normals if Vector(c.vector).length<1e-6)}
bpy.ops.wm.save_as_mainfile(filepath=f'c9/cab_{tag}.blend',compress=False)
json.dump(info,open(f'c9/cab_{tag}.json','w'),indent=1); print(json.dumps(info))
