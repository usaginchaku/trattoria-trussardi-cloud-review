# Local LOD1 health fix for COORD09 candidates only:
#  (1) reverse the closed components with negative signed volume (inside-out shells)
#  (2) faces touching a vertex whose smooth normal is degenerate (area-weighted face normals cancel, ratio<0.01) are set flat;
#      all other faces keep their smooth flag (no global recalculation, no custom normals added)
import bpy,bmesh,sys,json,numpy as np
from mathutils import Vector
src,dst=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=src)
o=bpy.data.objects['02_Flower_Basket_LOD1_Mesh']; me=o.data
def uvsets(): return {u.name:[frozenset(tuple(round(c,6) for c in u.data[li].uv) for li in p.loop_indices) for p in me.polygons] for u in me.uv_layers}
uv_before=uvsets()
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
seen=set(); flipped=[]
for f in bm.faces:
    if f.index in seen: continue
    st=[f]; c=[]
    while st:
        x=st.pop()
        if x.index in seen: continue
        seen.add(x.index); c.append(x)
        for e in x.edges:
            for g in e.link_faces:
                if g.index not in seen: st.append(g)
    if all(e.is_manifold for x in c for e in x.edges):
        vol=sum(x.verts[0].co.dot(x.verts[k].co.cross(x.verts[k+1].co))/6 for x in c for k in range(1,len(x.verts)-1))
        if vol<0: bmesh.ops.reverse_faces(bm,faces=c); flipped.append(len(c))
bm.to_mesh(me); me.update(); bm.free()
# degenerate smooth normals: area-weighted face-normal sum / area < 0.01 (opposite faces cancel)
fn=[Vector(p.normal) for p in me.polygons]
vs=[Vector((0,0,0)) for _ in me.vertices]; va=[0.0]*len(me.vertices)
for p in me.polygons:
    for vi in p.vertices: vs[vi]+=fn[p.index]*p.area; va[vi]+=p.area
badv={i for i in range(len(vs)) if va[i]>0 and vs[i].length/va[i]<0.01}
flat=0
for p in me.polygons:
    if p.use_smooth and any(v in badv for v in p.vertices): p.use_smooth=False; flat+=1
me.update()
# probe: FBX import stores corner normals as custom normals; corners whose lnor space cannot encode them become zero.
# find those corners with a temporary custom-normal set on a copy, flatten their faces, repeat until none.
probe_rounds=[]
for it in range(6):
    tmp=me.copy()
    tmp.normals_split_custom_set([Vector(c.vector) for c in tmp.corner_normals]); tmp.update()
    zc={i for i,c in enumerate(tmp.corner_normals) if Vector(c.vector).length<1e-6}
    zp=[p.index for p in tmp.polygons if any(li in zc for li in p.loop_indices)]
    bpy.data.meshes.remove(tmp)
    probe_rounds.append(len(zp))
    if not zp: break
    zv={v for pi in zp for v in me.polygons[pi].vertices}
    for p in me.polygons:
        if p.use_smooth and any(v in zv for v in p.vertices): p.use_smooth=False; flat+=1
    me.update()
fixed=flat  # corners of these faces now use the face normal; no custom normals written (source LOD blend has none)
info={'reversed_components_faces':flipped,'degenerate_verts':len(badv),'faces_set_flat':flat,'probe_zero_polys_per_round':probe_rounds,'uv_per_face_unchanged':uv_before==uvsets(),
 'zero_len_corners_after':int(sum(1 for c in me.corner_normals if Vector(c.vector).length<1e-6))}
bpy.ops.wm.save_as_mainfile(filepath=dst,compress=False); print(json.dumps(info))
