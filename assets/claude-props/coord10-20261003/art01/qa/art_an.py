import bpy,numpy as np,json
R='src9/assets/codex-source/coord10-art01-20261003/'
out={}
for n in ('22','23','24','25'):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=R+f'Frame_{n}_FUR06.fbx')
    objs=[o for o in bpy.data.objects if o.type=='MESH']; o=objs[0]; me=o.data
    co=np.array([v.co[:] for v in me.vertices])
    mats=[m.name for m in me.materials]
    pi=[i for i,m in enumerate(me.materials) if 'Painting' in m.name]
    pf=[p for p in me.polygons if p.material_index in pi]
    pv=sorted({v for p in pf for v in p.vertices}); P=co[pv]
    uv=np.array([me.uv_layers[0].data[li].uv[:] for p in pf for li in p.loop_indices])
    out[n]={'objects':[x.name for x in objs],'verts':len(co),'tris':sum(len(p.vertices)-2 for p in me.polygons),'dims':np.ptp(co,0).round(4).tolist(),'min':co.min(0).round(4).tolist(),
      'mats':mats,'uv_layers':[u.name for u in me.uv_layers],'painting_faces':len(pf),'painting_extent':np.ptp(P,0).round(4).tolist(),'painting_min':P.min(0).round(4).tolist(),
      'painting_uv_min':uv.min(0).round(5).tolist(),'painting_uv_max':uv.max(0).round(5).tolist(),'custom':me.has_custom_normals,
      'images':[(i.name,i.filepath.split('/')[-1].split('\\\\')[-1]) for i in bpy.data.images]}
    print('P',n,json.dumps(out[n]))
json.dump(out,open('c9/art_frames.json','w'),indent=1)
