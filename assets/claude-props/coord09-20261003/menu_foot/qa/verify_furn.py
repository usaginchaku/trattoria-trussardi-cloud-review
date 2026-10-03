# compare candidate FBX against Codex source FBX (bpy 4.3.0 import of both)
import bpy,bmesh,json,sys,math,numpy as np
exec(open('verify9.py').read().split('def gs(')[1].join(['def gs(','']) if False else '')
import struct
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
pairs=json.loads(sys.argv[sys.argv.index('--')+1])
res={}
def load(p):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p)
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
    bm=bmesh.new(); bm.from_mesh(me)
    cn=np.array([c.vector[:] for c in me.corner_normals])
    d={'object':o.name,'rot':[round(math.degrees(a),3) for a in o.rotation_euler],'scale':[round(s,6) for s in o.scale],'dims':[round(x,5) for x in o.dimensions],
       'verts':len(me.vertices),'tris':sum(len(p.vertices)-2 for p in me.polygons),'zmin':round(min(v.co.z for v in me.vertices),6),
       'uv':[u.name for u in me.uv_layers],'mats':[m.name for m in me.materials],'images':sorted({(i.name,tuple(i.size)) for i in bpy.data.images if i.size[0]>0}),
       'nonmanifold':sum(1 for e in bm.edges if not e.is_manifold),'boundary':sum(1 for e in bm.edges if e.is_boundary),'zero_area':sum(1 for f in bm.faces if f.calc_area()<1e-12),
       'zero_len_corner_normals':int((np.linalg.norm(cn,axis=1)<1e-6).sum()),'custom_normals':me.has_custom_normals}
    arr={'co':np.array([v.co[:] for v in me.vertices]),'fn':np.array([p.normal[:] for p in me.polygons]),'cn':cn,'uv':np.array([l.uv[:] for l in me.uv_layers[0].data])}
    return d,arr
for name,(a,b) in pairs.items():
    da,A=load(a); db,Bv=load(b)
    r={'source':a.split('/')[-1],'candidate':'/'.join(b.split('/')[-4:]),'gs_source':gs(a),'gs_candidate':gs(b),'gs_match':gs(a)==gs(b),'source_info':da,'candidate_info':db}
    if da['verts']==db['verts'] and len(A['fn'])==len(Bv['fn']):
        mv=np.linalg.norm(Bv['co']-A['co'],axis=1)
        dots=(A['fn']*Bv['fn']).sum(1)
        r.update(verts_moved=int((mv>1e-5).sum()),max_move_m=float(mv.max()),faces_flipped_vs_source=int((dots<0).sum()),
                 uv_identical=bool(np.allclose(A['uv'],Bv['uv'],atol=1e-6)),
                 corner_normals_changed=int((np.abs(A['cn']-Bv['cn']).max(1)>1e-3).sum()))
    res[name]=r
json.dump(res,open('c9/verify_furniture.json','w'),indent=1,default=str)
for k,r in res.items():
    c=r['candidate_info']; s=r['source_info']
    print(k,'GS',r['gs_match'],'rot',c['rot'],'scale',c['scale'],'dims',c['dims'],'vs',s['dims'],'tris',c['tris'],'/',s['tris'],'zmin',c['zmin'],'uv',c['uv'],'mats',c['mats']==s['mats'],'imgs',len(c['images']),'/',len(s['images']),
      'nm',c['nonmanifold'],'bd',c['boundary'],'/',s['boundary'],'za',c['zero_area'],'zeroN',c['zero_len_corner_normals'],'/',s['zero_len_corner_normals'],'moved',r.get('verts_moved'),'flip',r.get('faces_flipped_vs_source'),'uvSame',r.get('uv_identical'),'cnChanged',r.get('corner_normals_changed'))
