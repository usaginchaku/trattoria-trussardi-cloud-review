# A4 extra checks: non-olive faces (mat/rim/painting) unchanged as geometry; olive faces only gained; BVH self-overlap; bbox.
import bpy,bmesh,sys,json,numpy as np
from mathutils.bvhtree import BVHTree
src,cand,outp=sys.argv[-3:]
def load(p):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p)
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data; uvl=me.uv_layers[0].data
    fin=[i for i,m in enumerate(me.materials) if 'Finish' in m.name][0]
    def olive(p):
        u=np.mean([uvl[l].uv[:] for l in p.loop_indices],0); return p.material_index==fin and int(u[0]*4)==2 and int((1-u[1])*4)==0
    co=np.array([v.co[:] for v in me.vertices])
    non=sorted(tuple(sorted(tuple(np.round(co[v],5)) for v in p.vertices))+(p.material_index,) for p in me.polygons if not olive(p))
    nonuv=sorted(tuple(sorted(tuple(np.round(uvl[l].uv[:],5)) for l in p.loop_indices)) for p in me.polygons if not olive(p))
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    tree=BVHTree.FromBMesh(bm); ov=tree.overlap(tree)
    adj=lambda a,b: bool(set(v.index for v in bm.faces[a].verts)&set(v.index for v in bm.faces[b].verts))
    bm.faces.ensure_lookup_table(); real=[(a,b) for a,b in ov if a<b and not adj(a,b)]
    return {'non_olive_faces':len(non),'olive_faces':sum(1 for p in me.polygons if olive(p)),'bbox':[co.min(0).round(5).tolist(),co.max(0).round(5).tolist()],
            'self_overlap_pairs_nonadjacent':len(real),'min_face_area':float(min(p.area for p in me.polygons))},non,nonuv
a,na,ua=load(src); b,nb,ub=load(cand)
r={'source':a,'candidate':b,'non_olive_faces_geometry_identical':na==nb,'non_olive_faces_uv_identical':ua==ub,'bbox_identical':a['bbox']==b['bbox']}
json.dump(r,open(outp,'w'),indent=1); print('CHK',json.dumps(r))
