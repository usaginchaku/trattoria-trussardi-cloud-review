import bpy,numpy as np,json,collections
from PIL import Image
R='src2/assets/codex-source/coord10-art02-input-20261004/'
FA=np.array(Image.open(R+'FinishAtlas_FUR06.png').convert('RGB'))
out={}
for n in (1,2,3):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=R+f'LAY03_UpperFrame_{n}.fbx')
    obs=[o for o in bpy.data.objects if o.type=='MESH']; o=obs[0]; me=o.data; uvl=me.uv_layers[0].data
    co=np.array([v.co[:] for v in me.vertices])
    pi=[i for i,m in enumerate(me.materials) if 'Painting' in m.name]
    pf=[p for p in me.polygons if p.material_index in pi]; P=co[sorted({v for p in pf for v in p.vertices})]
    front=[p for p in pf if p.normal.y<-0.9]
    uv=np.array([uvl[l].uv[:] for p in front for l in p.loop_indices])
    cells=collections.Counter()
    for p in me.polygons:
        if p.material_index in pi: continue
        u=np.array([uvl[l].uv[:] for l in p.loop_indices]).mean(0); cells[(int(u[0]*4),int((1-u[1])*4))]+=1
    colors={str(k):FA[k[1]*256+128,k[0]*256+128].tolist() for k in cells}
    out[n]={'object':o.name,'n_objects':len(obs),'uv_layers':[u.name for u in me.uv_layers],'mats':[m.name for m in me.materials],'verts':len(co),'tris':len(me.polygons),
            'loc':list(o.location),'rot':list(o.rotation_euler),'scale':list(o.scale),'bbox':[co.min(0).round(4).tolist(),co.max(0).round(4).tolist()],
            'painting_extent':np.ptp(P,0).round(4).tolist(),'painting_min':P.min(0).round(4).tolist(),'painting_front_uv':[uv.min(0).round(5).tolist(),uv.max(0).round(5).tolist()],
            'finish_cells':{str(k):v for k,v in cells.items()},'cell_centre_colors':colors,'custom_normals':me.has_custom_normals,'images':[i.name for i in bpy.data.images]}
    print('U',n,json.dumps(out[n]))
json.dump(out,open('art2/upper_frames.json','w'),indent=1)
