import bpy,bmesh,json,math,os,struct
from mathutils import Vector
V='<home>/dot_v02_src/assets/dot-props/v02/fbx'
R='<home>/trattoria-trussardi-cloud-review/assets/claude-props/coord07-20261003/basket_height'
P='<scratch>/prev/assets/claude-props/v02-review-20261002/fbx'
pairs=[('basket_L2','<scratch>/base7/fbx/02_Flower_Basket.fbx','<home>/trattoria-trussardi-cloud-review/assets/claude-props/coord09-20261003/basket_leaf/L2/fbx/02_Flower_Basket.fbx'),('basket_L3','<scratch>/base7/fbx/02_Flower_Basket.fbx','<home>/trattoria-trussardi-cloud-review/assets/claude-props/coord09-20261003/basket_leaf/L3/fbx/02_Flower_Basket.fbx'),
('basket_LOD1_L2','<scratch>/base7/fbx/LOD1/02_Flower_Basket_LOD1.fbx','<home>/trattoria-trussardi-cloud-review/assets/claude-props/coord09-20261003/basket_leaf/L2/fbx/LOD1/02_Flower_Basket_LOD1.fbx'),('basket_LOD1_L3','<scratch>/base7/fbx/LOD1/02_Flower_Basket_LOD1.fbx','<home>/trattoria-trussardi-cloud-review/assets/claude-props/coord09-20261003/basket_leaf/L3/fbx/LOD1/02_Flower_Basket_LOD1.fbx'),
('water_A','<scratch>/prev/assets/claude-props/v02-review-20261002/fbx/06_Water_Glass.fbx','<home>/trattoria-trussardi-cloud-review/assets/claude-props/coord09-20261003/water_bowl/A/fbx/06_Water_Glass.fbx'),('water_B2','<scratch>/prev/assets/claude-props/v02-review-20261002/fbx/06_Water_Glass.fbx','<home>/trattoria-trussardi-cloud-review/assets/claude-props/coord09-20261003/water_bowl/B2/fbx/06_Water_Glass.fbx')]
def gs(p):
    b=open(p,'rb').read(); out={}
    for k in [b'UpAxis',b'UpAxisSign',b'FrontAxis',b'FrontAxisSign',b'CoordAxis',b'CoordAxisSign',b'UnitScaleFactor']:
        i=b.find(b'S'+struct.pack('<I',len(k))+k); j=i+5+len(k); vals=[]
        while len(vals)<4 and j<len(b):
            t=b[j:j+1]
            if t==b'S': n=struct.unpack('<I',b[j+1:j+5])[0]; vals.append(b[j+5:j+5+n].decode(errors='replace')); j+=5+n
            elif t==b'I': vals.append(struct.unpack('<i',b[j+1:j+5])[0]); j+=5
            elif t==b'D': vals.append(struct.unpack('<d',b[j+1:j+9])[0]); j+=9
            else: break
        out[k.decode()]=vals[-1] if vals else None
    return out
exec(open('uvcheck_lib.py').read().split('L=me.uv_layers')[0])  # defines tris_uv, area, overlap (needs me)
def load(p):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p)
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; return o
def overlaps(me,layer):
    global_me=me
    T=[]
    for pl in me.polygons:
        ls=list(pl.loop_indices)
        for i in range(1,len(ls)-1): T.append([tuple(layer.data[l].uv) for l in (ls[0],ls[i],ls[i+1])])
    G=128; grid={}
    for i,t in enumerate(T):
        xs=[p[0] for p in t]; ys=[p[1] for p in t]
        for gx in range(int(min(xs)*G),int(max(xs)*G)+1):
            for gy in range(int(min(ys)*G),int(max(ys)*G)+1): grid.setdefault((gx,gy),[]).append(i)
    pairs=set()
    for cell in grid.values():
        for a in range(len(cell)):
            for b in range(a+1,len(cell)):
                i,j=cell[a],cell[b]
                if (i,j) not in pairs and overlap(T[i],T[j]): pairs.add((i,j))
    return len(pairs), all(0<=u<=1 and 0<=v<=1 for t in T for u,v in t)
res={}
for name,orig,cand in pairs:
    r={'original':os.path.relpath(orig,'/home/user') if orig.startswith('/home') else 'baseline:'+orig.split('/')[-1],'candidate':os.path.relpath(cand,'/home/user'),'globalSettingsMatch':gs(orig)==gs(cand),'globalSettings':gs(cand)}
    for tag,p in (('orig',orig),('cand',cand)):
        o=load(p); me=o.data
        bm=bmesh.new(); bm.from_mesh(me)
        r[tag]={'object':o.name,'rot_deg':[round(math.degrees(a),3) for a in o.rotation_euler],'scale':[round(s,6) for s in o.scale],'dims_m':[round(d,5) for d in o.dimensions],
          'verts':len(me.vertices),'tris':sum(len(p.vertices)-2 for p in me.polygons),'zmin_m':round(min((o.matrix_world@v.co).z for v in me.vertices),7),
          'uv':[u.name for u in me.uv_layers],'materials':[m.name for m in me.materials],
          'images':sorted({(i.name.split('.')[0],tuple(i.size)) for i in bpy.data.images if i.size[0]>0}),
          'nonmanifold':sum(1 for e in bm.edges if not e.is_manifold),'boundary':sum(1 for e in bm.edges if e.is_boundary),
          'zero_area':sum(1 for f in bm.faces if f.calc_area()<1e-12),'face_normals':[tuple(p.normal) for p in me.polygons]}
        if tag=='cand' and 'LightmapUV' in me.uv_layers:
            n,in01=overlaps(me,me.uv_layers['LightmapUV']); r['cand']['lightmap_overlap_pairs']=n; r['cand']['lightmap_in_0_1']=in01
        bm.free()
    a=r['orig'].pop('face_normals'); b=r['cand'].pop('face_normals')
    if len(a)==len(b):
        dots=[Vector(x).dot(Vector(y)) for x,y in zip(a,b)]
        r['faces_same_count']=True; r['faces_flipped_vs_original(dot<0)']=sum(1 for d in dots if d<0); r['min_face_normal_dot']=round(min(dots),4)
    else: r['faces_same_count']=False
    res[name]=r
json.dump(res,open('c9/verify_coord09.json','w'),indent=1,default=str)
for k,r in res.items():
    c=r['cand']; o=r['orig']
    print(k,'GS',r['globalSettingsMatch'],'rot',c['rot_deg'],'dims',c['dims_m'],'vs',o['dims_m'],'tris',c['tris'],'/',o['tris'],'zmin',c['zmin_m'],'uv',c['uv'],'nm',c['nonmanifold'],'bd',c['boundary'],'za',c['zero_area'],'lm',c.get('lightmap_overlap_pairs'),'flip',r.get('faces_flipped_vs_original(dot<0)'),'imgs',c['images'])
