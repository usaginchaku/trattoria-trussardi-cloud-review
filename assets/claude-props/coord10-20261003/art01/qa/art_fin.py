import bpy,numpy as np,collections,json
from PIL import Image
R='src9/assets/codex-source/coord10-art01-20261003/'
FA=np.array(Image.open(R+'FinishAtlas_FUR06.png').convert('RGB')); FH,FW=FA.shape[:2]
print('P finish atlas',FA.shape)
res={}
for n in ('22','23','24','25'):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=R+f'Frame_{n}_FUR06.fbx')
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data; uvl=me.uv_layers[0].data
    groups=collections.defaultdict(list)
    for p in me.polygons:
        if 'Painting' in me.materials[p.material_index].name: continue
        uv=np.array([uvl[li].uv[:] for li in p.loop_indices]); c=uv.mean(0)
        px=FA[min(FH-1,int((1-c[1])*FH)),min(FW-1,int(c[0]*FW))]
        key=(round(uv[:,0].min(),3),round(uv[:,1].min(),3),round(uv[:,0].max(),3),round(uv[:,1].max(),3))
        groups[tuple(px)].append((p.index,key,p.center.y))
    res[n]={str(k):{'faces':len(v),'uv_boxes':sorted({b for _,b,_ in v})[:3],'y_range':[round(min(y for *_,y in v),4),round(max(y for *_,y in v),4)]} for k,v in groups.items()}
    print('P',n,json.dumps(res[n]))
json.dump(res,open('c9/art_finish_regions.json','w'),indent=1)
