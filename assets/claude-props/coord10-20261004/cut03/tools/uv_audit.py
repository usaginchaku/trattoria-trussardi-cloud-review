# Independent UV audit (geometry, not sampling):
#  UV0: per triangle UV area vs 3D area; triangles with UV0 area ~0 (degenerate in UV) and their 3D area share.
#  UV2 (LightmapUV): exact triangle-triangle intersection area for every pair whose UV bboxes overlap (grid hashing);
#      area > EPS_AREA = overlap; touching pairs with area <= EPS_AREA (shared edge / shared vertex / point contact) are listed separately.
import bpy,sys,json,itertools,collections,numpy as np
EPS_AREA=1e-12; TINY=1e-10
def clip(poly,a,b):
    out=[]; n=len(poly)
    def side(p): return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
    for i in range(n):
        p,q=poly[i],poly[(i+1)%n]; sp,sq=side(p),side(q)
        if sp>=0: out.append(p)
        if (sp>=0)!=(sq>=0):
            t=sp/(sp-sq); out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
    return out
def area(poly):
    if len(poly)<3: return 0.0
    return 0.5*abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly))))
def ccw(t):
    a,b,c=t; return t if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])>0 else (a,c,b)
def inter(t1,t2):
    poly=list(ccw(t1)); t2=ccw(t2)
    for i in range(3):
        poly=clip(poly,t2[i],t2[(i+1)%3])
        if not poly: return 0.0
    return area(poly)
res={}
for p in sys.argv[sys.argv.index('--')+1:-1]:
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p)
    me=[o for o in bpy.data.objects if o.type=='MESH'][0].data; me.calc_loop_triangles()
    co=np.array([v.co[:] for v in me.vertices]); uv0=np.array([l.uv[:] for l in me.uv_layers['UVMap'].data]); uv2=np.array([l.uv[:] for l in me.uv_layers['LightmapUV'].data])
    T=list(me.loop_triangles)
    a3=np.array([lt.area for lt in T])
    def uva(U,lt): A,B,C=U[list(lt.loops)]; return 0.5*abs((B[0]-A[0])*(C[1]-A[1])-(B[1]-A[1])*(C[0]-A[0]))
    a0=np.array([uva(uv0,lt) for lt in T]); a2=np.array([uva(uv2,lt) for lt in T])
    zero0=a0<1e-12
    r={'tris':len(T),'mesh_area_m2':float(a3.sum()),
       'uv0':{'tris_uv_area_lt_1e-12':int(zero0.sum()),'their_3d_area_m2':float(a3[zero0].sum()),'their_3d_area_fraction':float(a3[zero0].sum()/a3.sum()),'tris_uv_area_lt_1e-9':int((a0<1e-9).sum())},
       'uv2':{'tiny_tris_uv_area_lt_1e-10':int((a2<TINY).sum()),'eps_area':EPS_AREA}}
    # UV2 pairwise exact test
    tris=[tuple(map(tuple,uv2[list(lt.loops)])) for lt in T]; verts=[set(lt.vertices) for lt in T]
    G=collections.defaultdict(list); cell=0.02
    bb=[(min(x for x,_ in t),min(y for _,y in t),max(x for x,_ in t),max(y for _,y in t)) for t in tris]
    for i,(x0,y0,x1,y1) in enumerate(bb):
        for gx in range(int(x0/cell),int(x1/cell)+1):
            for gy in range(int(y0/cell),int(y1/cell)+1): G[(gx,gy)].append(i)
    pairs=set()
    for lst in G.values():
        for i,j in itertools.combinations(lst,2):
            a,b=(i,j) if i<j else (j,i)
            A,B=bb[a],bb[b]
            if A[0]<=B[2] and B[0]<=A[2] and A[1]<=B[3] and B[1]<=A[3]: pairs.add((a,b))
    over=[];touch=collections.Counter()
    for a,b in pairs:
        s=inter(tris[a],tris[b])
        if s>EPS_AREA: over.append((a,b,s))
        else:
            sh=len(verts[a]&verts[b]); touch['shared_edge' if sh==2 else 'shared_vertex' if sh==1 else 'bbox_or_point_contact_no_shared_vertex']+=1
    r['uv2'].update(candidate_pairs_bbox=len(pairs),overlapping_pairs_area_gt_eps=len(over),max_overlap_area=float(max([o[2] for o in over],default=0.0)),
                    non_overlapping_contacts=dict(touch),note='3D-adjacent triangles in the same UV island share UV edges; such pairs have zero intersection area and are classified as contacts, not overlaps')
    res[p.split('/')[-3]+'/'+p.split('/')[-1]]=r; print('U',p.split('/')[-3],json.dumps(r))
json.dump(res,open(sys.argv[-1],'w'),indent=1)
