# COORD10-CUT04: give every face of the CUT02 A1 fork/spoon a positive UV0 area, changing ONLY the UVMap (UV0) arrays.
# Reads the CUT02 FBX arrays directly (io_scene_fbx parse_fbx), computes a per-face box projection (dominant-normal axis plane),
# scales all faces with one uniform scale into the uniform silver patch, writes the corner mapping (CSV/NPZ/JSON) and a new FBX
# in which only LayerElementUV[UVMap].UV / UVIndex differ. All other arrays are re-encoded unchanged and verified by hash.
# usage: python uv0_only.py <cut02_fbx> <out_fbx> <out_prefix>
import sys,os,json,hashlib,csv,bpy,addon_utils,numpy as np
p=[m for m in addon_utils.modules() if m.__name__=='io_scene_fbx'][0].__file__; sys.path.insert(0,os.path.dirname(os.path.dirname(p)))
from io_scene_fbx import parse_fbx,encode_bin
src,dst,prefix=sys.argv[-3:]
REGION=(0.140,0.140,0.185,0.235)      # u0,v0,u1,v1 inside the uniform silver patch used by the v02 sources (u 0.133-0.228, v 0.133-0.242)
def find(e,name):
    for c in e.elems:
        if c.id==name: yield c
        yield from find(c,name)
child=lambda e,n:[c for c in e.elems if c.id==n][0]
def arrays(path):
    root,ver=parse_fbx.parse(path); g=next(find(root,b'Geometry'))
    A={'Vertices':np.array(child(g,b'Vertices').props[0]),'PolygonVertexIndex':np.array(child(g,b'PolygonVertexIndex').props[0]),'Edges':np.array(child(g,b'Edges').props[0])}
    for le in g.elems:
        if le.id==b'LayerElementSmoothing': A['Smoothing']=np.array(child(le,b'Smoothing').props[0])
        if le.id==b'LayerElementNormal': A['Normals']=np.array(child(le,b'Normals').props[0]); A['NormalsIndex']=np.array(child(le,b'NormalsIndex').props[0])
        if le.id==b'LayerElementMaterial': A['Materials']=np.array(child(le,b'Materials').props[0])
        if le.id==b'LayerElementUV':
            nm=child(le,b'Name').props[0].decode(); A[f'UV[{nm}]']=np.array(child(le,b'UV').props[0]); A[f'UVIndex[{nm}]']=np.array(child(le,b'UVIndex').props[0])
    models=[m.props[1].split(b'\x00')[0].decode() for m in find(root,b'Model')]; geoms=[x.props[1].split(b'\x00')[0].decode() for x in find(root,b'Geometry')]
    return root,ver,A,models,geoms
h=lambda a: hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
root,ver,A,models,geoms=arrays(src)
V=A['Vertices'].reshape(-1,3); PVI=A['PolygonVertexIndex']; vid=np.where(PVI<0,-PVI-1,PVI)
ends=np.where(PVI<0)[0]; starts=np.concatenate([[0],ends[:-1]+1]); poly_of=np.repeat(np.arange(len(ends)),ends-starts+1)
uv0_old=A['UV[UVMap]'].reshape(-1,2)[A['UVIndex[UVMap]']]
# per-polygon dominant axis of the geometric face normal
P=V[vid]; nrm=np.zeros((len(ends),3))
for f,(s,e) in enumerate(zip(starts,ends)):
    q=P[s:e+1]; n=np.zeros(3)
    for i in range(1,len(q)-1): n+=np.cross(q[i]-q[0],q[i+1]-q[0])
    nrm[f]=n
ax=np.abs(nrm).argmax(1)                   # 0:x -> plane (z,y) ; 1:y -> plane (x,z) ; 2:z -> plane (x,y)
mn,mx=V.min(0),V.max(0); ext=mx-mn
uv_raw=np.zeros((len(PVI),2))
for c in range(len(PVI)):
    x,y,z=P[c]-mn; a=ax[poly_of[c]]
    uv_raw[c]=(z,y) if a==0 else ((x,z) if a==1 else (x,y))
span=uv_raw.max(0)
s=min((REGION[2]-REGION[0])/span[0],(REGION[3]-REGION[1])/span[1])     # one uniform scale (UV per metre) for every face
uv_new=np.array([REGION[0],REGION[1]])+uv_raw*s
# ---- rewrite: only UVMap UV/UVIndex replaced ----
ADD={b'Y':'add_int16',b'C':'add_char',b'B':'add_char',b'Z':'add_int8',b'I':'add_int32',b'F':'add_float32',b'D':'add_float64',b'L':'add_int64',b'R':'add_bytes',b'S':'add_string',
     b'f':'add_float32_array',b'd':'add_float64_array',b'i':'add_int32_array',b'l':'add_int64_array',b'b':'add_bool_array'}
def conv(e,in_uvmap=False):
    o=encode_bin.FBXElem(e.id)
    is_uvmap=e.id==b'LayerElementUV' and any(c.id==b'Name' and c.props[0]==b'UVMap' for c in e.elems)
    for v,t in zip(e.props,e.props_type):
        t=bytes([t]); f=getattr(o,ADD[t])
        if in_uvmap and e.id==b'UV': f(np.asarray(uv_new.reshape(-1),dtype=np.float64))
        elif in_uvmap and e.id==b'UVIndex': f(np.arange(len(PVI),dtype=np.int32))
        elif t==b'B': f(b'\x01' if v else b'\x00')     # repair: bool 'B' written by the earlier strip tool -> standard FBX 'C' (1 byte), same value
        elif t==b'C': f(v if isinstance(v,bytes) else bytes([int(v)]))
        else: f(v)
    for c in e.elems: o.elems.append(conv(c,in_uvmap or is_uvmap))
    return o
r=encode_bin.FBXElem(b'')
for c in root.elems: r.elems.append(conv(c))
encode_bin.write(dst,r,ver)
# ---- verify by re-reading both files' arrays ----
_,_,B,models2,geoms2=arrays(dst)
inv={k:{'cut02_sha256_of_values':h(A[k]),'cut04_sha256_of_values':h(B[k]),'identical':bool(A[k].shape==B[k].shape and np.array_equal(A[k],B[k]))} for k in A if not k.endswith('[UVMap]')}
uv_back=B['UV[UVMap]'].reshape(-1,2)[B['UVIndex[UVMap]']]
def tri_area2(U,idx): a,b,c=U[idx[0]],U[idx[1]],U[idx[2]]; return 0.5*abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))
def tri_area3(idx): a,b,c=P[idx[0]],P[idx[1]],P[idx[2]]; return 0.5*np.linalg.norm(np.cross(b-a,c-a))
tris=[(s_,s_+1,s_+2) for s_,e_ in zip(starts,ends) if e_-s_==2]
assert len(tris)==len(ends), 'non-triangle polygon found'
a_old=np.array([tri_area2(uv0_old,t) for t in tris]); a_new=np.array([tri_area2(uv_new,t) for t in tris]); a3=np.array([tri_area3(t) for t in tris])
# stretch: singular values of the 3D->UV map per triangle (uniform scale s ideally); report ratio sigma_min/sigma_max and sigma relative to s
sv=[]
for t in tris:
    a,b,c=P[list(t)]; e1,e2=b-a,c-a; u=np.linalg.norm(e1); ex=e1/u; ey=np.cross(np.cross(e1,e2),e1); ey/=np.linalg.norm(ey)
    M3=np.array([[u,0],[e2@ex,e2@ey]]).T; Ua,Ub,Uc=uv_new[list(t)]; M2=np.array([Ub-Ua,Uc-Ua]).T
    J=M2@np.linalg.inv(M3); sv.append(np.linalg.svd(J,compute_uv=False))
sv=np.array(sv)
stats={'source_fbx':os.path.basename(src),'source_sha256':hashlib.sha256(open(src,'rb').read()).hexdigest(),'new_fbx':os.path.basename(dst),'new_sha256':hashlib.sha256(open(dst,'rb').read()).hexdigest(),
 'model_names':models,'geometry_names':geoms,'model_names_new':models2,'vertices':len(V),'polygons':len(ends),'corners':len(PVI),
 'uv0_region_uvmin_uvmax':REGION,'uniform_scale_uv_per_m':float(s),'projection':'per-face box projection by dominant normal axis: |nx|->(z,y), |ny|->(x,z), |nz|->(x,y); all faces share one scale',
 'faces_by_axis':{'x':int((ax==0).sum()),'y':int((ax==1).sum()),'z':int((ax==2).sum())},
 'uv0_old':{'tris_area_lt_1e-12':int((a_old<1e-12).sum()),'their_3d_area_fraction':float(a3[a_old<1e-12].sum()/a3.sum()),'min_area':float(a_old.min())},
 'uv0_new':{'tris_area_lt_1e-12':int((a_new<1e-12).sum()),'tris_positive':int((a_new>0).sum()),'min_area':float(a_new.min()),'min_area_over_s2_times_3d_area':float((a_new/(s*s*a3)).min()),
   'stretch_sigma_max_over_s':[float(sv[:,0].min()/s),float(sv[:,0].max()/s)],'stretch_sigma_min_over_s':[float(sv[:,1].min()/s),float(sv[:,1].max()/s)],'worst_anisotropy_sigma_min_over_max':float((sv[:,1]/sv[:,0]).min()),
   'bbox':[uv_new.min(0).tolist(),uv_new.max(0).tolist()],'margin_to_region':{'left':float(uv_new[:,0].min()-REGION[0]),'bottom':float(uv_new[:,1].min()-REGION[1]),'right':float(REGION[2]-uv_new[:,0].max()),'top':float(REGION[3]-uv_new[:,1].max())},
   'margin_to_silver_patch_used_by_sources(u0.1333-0.2284,v0.133-0.2417)':{'left':float(uv_new[:,0].min()-0.1333),'bottom':float(uv_new[:,1].min()-0.133),'right':float(0.2284-uv_new[:,0].max()),'top':float(0.2417-uv_new[:,1].max())},
   'roundtrip_max_abs_diff':float(np.abs(uv_back-uv_new).max())},
 'unchanged_channels':inv}
json.dump(stats,open(prefix+'_uv0_stats.json','w'),indent=1)
np.savez_compressed(prefix+'_uv0_corner_mapping.npz',corner=np.arange(len(PVI)),polygon=poly_of,vertex=vid,uv0_cut02=uv0_old,uv0_cut04=uv_new)
with open(prefix+'_uv0_corner_mapping.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['corner(FBX polygon-vertex order)','polygon','vertex','u_cut02','v_cut02','u_cut04','v_cut04'])
    for c in range(len(PVI)): w.writerow([c,int(poly_of[c]),int(vid[c]),f'{uv0_old[c,0]:.8f}',f'{uv0_old[c,1]:.8f}',f'{uv_new[c,0]:.8f}',f'{uv_new[c,1]:.8f}'])
print('S',json.dumps({k:stats[k] for k in ('model_names','vertices','polygons','corners','uniform_scale_uv_per_m','faces_by_axis','uv0_old')}),json.dumps({k:stats['uv0_new'][k] for k in ('tris_area_lt_1e-12','min_area','min_area_over_s2_times_3d_area','worst_anisotropy_sigma_min_over_max','margin_to_region','roundtrip_max_abs_diff')}),{k:v['identical'] for k,v in inv.items()})
