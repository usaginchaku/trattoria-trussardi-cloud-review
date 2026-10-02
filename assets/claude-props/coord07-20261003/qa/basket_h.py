import bpy,bmesh,json,sys,math
from mathutils.bvhtree import BVHTree
src_blend,objname,k,tag=sys.argv[sys.argv.index('--')+1:]; k=float(k)
bpy.ops.wm.open_mainfile(filepath=src_blend)
o=bpy.data.objects[objname]; me=o.data
uv_before={u.name:[tuple(l.uv) for l in u.data] for u in me.uv_layers}
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
seen=set(); islands=[]
for v in bm.verts:
    if v.index in seen: continue
    st=[v]; comp=[]
    while st:
        x=st.pop()
        if x.index in seen: continue
        seen.add(x.index); comp.append(x.index)
        for e in x.link_edges: st.append(e.other_vert(x))
    islands.append(comp)
zs=[v.co.z for v in bm.verts]; zmin_all=min(zs)
FOLIAGE_Z=0.1135  # rim top 0.1125 (measured); foliage islands start at >=0.115
rim_top=max(bm.verts[i].co.z for isl in islands for i in isl if min(bm.verts[j].co.z for j in isl)<FOLIAGE_Z)
delta=rim_top*(1-k)
stats={'foliage':0,'basket_translate':0,'basket_scale':0}
fol_faces=set(); bas_faces=set()
for isl in islands:
    z=[bm.verts[i].co.z for i in isl]; lo,hi=min(z),max(z)
    if lo>=FOLIAGE_Z:
        for i in isl: bm.verts[i].co.z-=delta
        stats['foliage']+=1; tgt=fol_faces
    elif hi-lo<0.015:
        c=(lo+hi)/2; dz=c*k-c
        for i in isl: bm.verts[i].co.z+=dz
        stats['basket_translate']+=1; tgt=bas_faces
    else:
        for i in isl: bm.verts[i].co.z*=k
        stats['basket_scale']+=1; tgt=bas_faces
    for i in isl:
        for f in bm.verts[i].link_faces: tgt.add(f.index)
bm.to_mesh(me); me.update()
# checks
bm2=bmesh.new(); bm2.from_mesh(me); bm2.faces.ensure_lookup_table()
def sub_bvh(faces):
    b=bmesh.new(); vm={}
    for fi in faces:
        f=bm2.faces[fi]; vs=[]
        for v in f.verts:
            if v.index not in vm: vm[v.index]=b.verts.new(v.co)
            vs.append(vm[v.index])
        try: b.faces.new(vs)
        except ValueError: pass
    t=BVHTree.FromBMesh(b); b.free(); return t
inter=len(sub_bvh(fol_faces).overlap(sub_bvh(bas_faces)))
zs=[v.co.z for v in me.vertices]
info={'tag':tag,'k':k,'rim_top_before_m':rim_top,'foliage_shift_m':-delta,'islands':stats,'leaf_basket_triangle_overlaps':inter,
 'zmin':min(zs),'zmax':max(zs),'dims':list(o.dimensions),'tris':sum(len(p.vertices)-2 for p in me.polygons),
 'uv_unchanged':uv_before=={u.name:[tuple(l.uv) for l in u.data] for u in me.uv_layers},
 'nonmanifold':sum(1 for e in bm2.edges if not e.is_manifold),'zero_area':sum(1 for f in bm2.faces if f.calc_area()<1e-12),
 'basket_height_m':rim_top*k,'basket_ratio':rim_top*k/max(zs)}
bpy.ops.wm.save_as_mainfile(filepath=f'c7/basket_{tag}.blend',compress=False)
json.dump(info,open(f'c7/basket_{tag}.json','w'),indent=1); print(json.dumps(info))
