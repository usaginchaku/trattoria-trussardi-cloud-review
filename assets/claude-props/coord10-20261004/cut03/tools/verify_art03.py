# verify candidate FBX vs source FBX (both imported with bpy 4.3.0): FBX GlobalSettings, transform, dims, back/mount face,
# topology, UV, normals, manifold/boundary, zero-area, flipped faces, which vertices moved.
import bpy,bmesh,json,sys,math,struct,numpy as np
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
def load(p):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p)
    o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
    bm=bmesh.new(); bm.from_mesh(me)
    cn=np.array([c.vector[:] for c in me.corner_normals])
    lf=np.zeros(len(me.loops),int)
    for q in me.polygons: lf[q.loop_start:q.loop_start+q.loop_total]=q.index
    fn=np.array([q.normal[:] for q in me.polygons])
    co=np.array([v.co[:] for v in me.vertices])
    d={'object':o.name,'loc':[round(x,6) for x in o.location],'rot_deg':[round(math.degrees(a),4) for a in o.rotation_euler],'scale':[round(x,6) for x in o.scale],
       'bbox_min':co.min(0).round(5).tolist(),'bbox_max':co.max(0).round(5).tolist(),'verts':len(co),'faces':len(me.polygons),'tris':sum(len(q.vertices)-2 for q in me.polygons),
       'uv_layers':[u.name for u in me.uv_layers],'materials':[m.name for m in me.materials],'texture_names':sorted(i.name for i in bpy.data.images),
       'nonmanifold_edges':sum(1 for e in bm.edges if not e.is_manifold),'boundary_edges':sum(1 for e in bm.edges if e.is_boundary),
       'zero_area_faces':sum(1 for f in bm.faces if f.calc_area()<1e-10),'zero_len_corner_normals':int((np.linalg.norm(cn,axis=1)<1e-6).sum()),
       'corner_normal_max_dev_from_face_normal':float((1-(cn*fn[lf]).sum(1)).max()),'custom_normals':me.has_custom_normals,
       'mount_face_y0_verts':int((np.abs(co[:,1])<1e-5).sum())}
    A={'co':co,'fn':fn,'cn':cn,'uv':np.array([l.uv[:] for l in me.uv_layers[0].data]),'fv':[tuple(q.vertices) for q in me.polygons],'mat':[q.material_index for q in me.polygons]}
    return d,A
pairs=json.loads(sys.argv[sys.argv.index('--')+1]); outp=sys.argv[sys.argv.index('--')+2]; res={}
for name,(a,b) in pairs.items():
    da,A=load(a); db,B=load(b)
    r={'source':a.split('/')[-1],'candidate':'/'.join(b.split('/')[-4:]),'fbx_global_settings_source':gs(a),'fbx_global_settings_candidate':gs(b),'gs_match':gs(a)==gs(b),
       'source_info':da,'candidate_info':db,'bbox_identical':da['bbox_min']==db['bbox_min'] and da['bbox_max']==db['bbox_max'],
       'transform_identical':(da['loc'],da['rot_deg'],da['scale'])==(db['loc'],db['rot_deg'],db['scale']),'mount_face_verts_same':da['mount_face_y0_verts']==db['mount_face_y0_verts']}
    nv=len(A['co'])
    if len(B['co'])>=nv:
        mv=np.linalg.norm(B['co'][:nv]-A['co'],axis=1)
        r['original_verts_moved']=int((mv>1e-6).sum()); r['original_verts_moved_idx']=np.where(mv>1e-6)[0].tolist()[:400]; r['max_move_m']=float(mv.max())
        r['added_verts']=len(B['co'])-nv
    if len(A['fv'])==len(B['fv']) and A['fv']==B['fv']:
        r['topology_identical']=True; r['uv_identical']=bool(np.allclose(A['uv'],B['uv'],atol=1e-6))
        r['corner_normals_changed']=int((np.abs(A['cn']-B['cn']).max(1)>1e-3).sum()); r['faces_flipped']=int(((A['fn']*B['fn']).sum(1)<0).sum())
    else:
        r['topology_identical']=False
        # faces of source kept verbatim (same vertex tuple) and their UV/normal
        sa={fv:i for i,fv in enumerate(A['fv'])}; kept=[(sa[fv],j) for j,fv in enumerate(B['fv']) if fv in sa]
        r['source_faces_kept_verbatim']=len(kept); r['source_faces_total']=len(A['fv'])
        r['kept_faces_normal_max_dev']=float(max(1-(A['fn'][i]*B['fn'][j]).sum() for i,j in kept))
        from collections import Counter
        r['material_face_count_source']=dict(Counter(A['mat'])); r['material_face_count_candidate']=dict(Counter(B['mat']))
    res[name]=r
    print(name,{k:v for k,v in r.items() if k not in ('source_info','candidate_info','fbx_global_settings_source','original_verts_moved_idx')})
    print('  cand',{k:db[k] for k in ('rot_deg','scale','verts','tris','nonmanifold_edges','boundary_edges','zero_area_faces','zero_len_corner_normals','corner_normal_max_dev_from_face_normal')},'src b/nm',da['boundary_edges'],da['nonmanifold_edges'],da['tris'])
json.dump(res,open(outp,'w'),indent=1,default=str)
