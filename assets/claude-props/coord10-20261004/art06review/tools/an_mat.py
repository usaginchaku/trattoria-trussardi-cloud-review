# classify slot-0 faces of Frame_17/18/19 by the FinishAtlas 4x4 cell their UVs fall in; locate the faces geometrically.
import bpy,bmesh,json,sys,collections,numpy as np
from PIL import Image
I=sys.argv[-2]; outp=sys.argv[-1]
FA=np.array(Image.open(f'{I}/FinishAtlas_FUR06.png').convert('RGB')).astype(int)
cellstat=lambda c,r: (FA[r*256:(r+1)*256,c*256:(c+1)*256].reshape(-1,3).mean(0).round(1).tolist(),FA[r*256:(r+1)*256,c*256:(c+1)*256].reshape(-1,3).std(0).round(1).tolist())
res={}
for n in (17,18,19):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=f'{I}/Frame_{n}_FUR06.fbx')
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data; uvl=me.uv_layers[0].data
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    # shells (connected parts)
    seen={};sid=0
    for v in bm.verts:
        if v.index in seen: continue
        st=[v]; seen[v.index]=sid
        while st:
            x=st.pop()
            for e in x.link_edges:
                w=e.other_vert(x)
                if w.index not in seen: seen[w.index]=sid; st.append(w)
        sid+=1
    co=np.array([v.co[:] for v in me.vertices])
    groups=collections.defaultdict(list)
    for p in me.polygons:
        if p.material_index!=0: continue
        U=np.array([uvl[l].uv[:] for l in p.loop_indices]); c=U.mean(0); cell=(int(c[0]*4),int((1-c[1])*4))
        groups[cell].append(p.index)
    d={}
    for cell,fs in sorted(groups.items()):
        vs=sorted({v for f in fs for v in me.polygons[f].vertices}); P=co[vs]
        shells=sorted({seen[v] for v in vs}); nrm=collections.Counter(tuple(np.round(me.polygons[f].normal[:],0).astype(int).tolist()) for f in fs)
        U=np.array([uvl[l].uv[:] for f in fs for l in me.polygons[f].loop_indices]); span=np.ptp(np.array([[np.ptp([uvl[l].uv[0] for l in me.polygons[f].loop_indices]),np.ptp([uvl[l].uv[1] for l in me.polygons[f].loop_indices])] for f in fs]),0)
        uvmax_face=float(max(max(np.ptp([uvl[l].uv[k] for l in me.polygons[f].loop_indices]) for k in (0,1)) for f in fs))
        d[f'tile{cell[1]*4+cell[0]} (col{cell[0]},row{cell[1]})']={'faces':len(fs),'cell_mean_rgb_std':cellstat(*cell),'shells':shells,'verts':len(vs),
            'bbox_min':P.min(0).round(4).tolist(),'bbox_max':P.max(0).round(4).tolist(),'normals':{str(k):v for k,v in nrm.most_common(6)},
            'uv_min':U.min(0).round(4).tolist(),'uv_max':U.max(0).round(4).tolist(),'largest_single_face_uv_span':round(uvmax_face,4),'face_index_range':[min(fs),max(fs)]}
    pf=[p for p in me.polygons if p.material_index==1]; PP=co[sorted({v for p in pf for v in p.vertices})]
    res[f'Frame_{n}']={'object':o.name,'faces_total':len(me.polygons),'shells_total':sid,'painting_bbox':[PP.min(0).round(4).tolist(),PP.max(0).round(4).tolist()],'slot0_by_cell':d}
    print('F',n,o.name,len(me.polygons),'shells',sid); [print('   ',k,v['faces'],v['cell_mean_rgb_std'][0],'shells',v['shells'],'bbox',v['bbox_min'],v['bbox_max'],'faceUVspan',v['largest_single_face_uv_span']) for k,v in d.items()]
json.dump(res,open(outp,'w'),indent=1)
