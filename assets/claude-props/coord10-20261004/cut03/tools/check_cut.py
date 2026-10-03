# CUT02 checks on re-imported FBX: units/axes/bbox/ground, tris, manifold/boundary, zero-area, outward normals (signed volume),
# self-intersection (shrink-2% triangle test), UV ranges and LightmapUV overlap, material slot, normals finite.
import bpy,bmesh,sys,json,struct,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
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
def info(p):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p)
    obs=[o for o in bpy.data.objects if o.type=='MESH']; o=obs[0]; me=o.data
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.triangulate(bm,faces=bm.faces[:])
    co=np.array([v.co[:] for v in me.vertices])
    vol=sum(f.verts[0].co.dot(f.verts[1].co.cross(f.verts[2].co)) for f in bm.faces)/6
    V=[];F=[]
    for f in bm.faces:
        c=f.calc_center_median(); b=len(V); V+=[c+(v.co-c)*0.98 for v in f.verts]; F.append([b,b+1,b+2])
    t=BVHTree.FromPolygons(V,F,all_triangles=True); pv=[set(v.index for v in f.verts) for f in bm.faces]
    pen=sum(1 for a,b in t.overlap(t) if a<b and not (pv[a]&pv[b]))
    cn=np.array([c.vector[:] for c in me.corner_normals])
    uvs={u.name:np.array([l.uv[:] for l in u.data]) for u in me.uv_layers}
    # LightmapUV overlap: rasterise triangles at 512 and count texels covered twice
    lm=uvs.get('LightmapUV'); over=None; cov=None
    if lm is not None:
        # texel-centre coverage at 1024^2 with strict barycentric inside test (shared edges are not counted as overlap)
        R=1024; acc=np.zeros((R,R),np.uint16)
        for f in bm.faces:
            P=np.array([lm[l.index] if False else None for l in []]) if False else None
        me.calc_loop_triangles()
        for lt in me.loop_triangles:
            T=np.array([lm[li] for li in lt.loops])*R
            x0,y0=np.floor(T.min(0)).astype(int); x1,y1=np.ceil(T.max(0)).astype(int)
            xs,ys=np.meshgrid(np.arange(max(x0,0),min(x1,R))+0.5,np.arange(max(y0,0),min(y1,R))+0.5)
            if xs.size==0: continue
            (ax,ay),(bx,by),(cx,cy)=T; d=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
            if abs(d)<1e-12: continue
            l1=((by-cy)*(xs-cx)+(cx-bx)*(ys-cy))/d; l2=((cy-ay)*(xs-cx)+(ax-cx)*(ys-cy))/d; l3=1-l1-l2
            inside=(l1>1e-6)&(l2>1e-6)&(l3>1e-6)
            acc[ys[inside].astype(int),xs[inside].astype(int)]+=1
        over=int((acc>1).sum()); cov=int((acc>0).sum())
    return {'objects':[x.name for x in obs],'rot':[round(a,6) for a in o.rotation_euler],'scale':list(o.scale),'loc':list(o.location),'gs':gs(p),
            'verts':len(co),'tris':len(bm.faces),'bbox':[co.min(0).round(5).tolist(),co.max(0).round(5).tolist()],'size_m':np.ptp(co,0).round(5).tolist(),'zmin':float(co[:,2].min()),
            'nonmanifold_edges':sum(1 for e in bm.edges if not e.is_manifold),'boundary_edges':sum(1 for e in bm.edges if e.is_boundary),
            'zero_area_tris(<1e-10)':sum(1 for f in bm.faces if f.calc_area()<1e-10),'min_tri_area':float(min(f.calc_area() for f in bm.faces)),
            'signed_volume_m3':float(vol),'outward_normals':bool(vol>0),'self_intersections':pen,'normals_finite_unit':bool(np.isfinite(cn).all() and np.allclose(np.linalg.norm(cn,axis=1),1,atol=1e-3)),
            'materials':[m.name for m in me.materials],'uv_layers':list(uvs),'uv_ranges':{k:[v.min(0).round(4).tolist(),v.max(0).round(4).tolist()] for k,v in uvs.items()},
            'lightmap_texels_overlapping_1024':over,'lightmap_texels_covered_1024':cov}
res={}
for p in sys.argv[sys.argv.index('--')+1:-1]:
    r=info(p); res[p.split('/')[-1]+('@'+p.split('/')[-3] if len(p.split('/'))>2 else '')]=r
    print('C',p.split('/')[-3:],json.dumps({k:r[k] for k in ('tris','size_m','zmin','nonmanifold_edges','boundary_edges','zero_area_tris(<1e-10)','outward_normals','self_intersections','normals_finite_unit','lightmap_texels_overlapping_1024','lightmap_texels_covered_1024')}))
json.dump(res,open(sys.argv[-1],'w'),indent=1)
