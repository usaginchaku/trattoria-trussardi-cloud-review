# CAB04BASE audit: read the arrays WRITTEN in each FBX (no Blender import heuristics) and compare
# C3m original / bpy4.3 pass-through baseline / C4. Loop correspondence is accepted only if PolygonVertexIndex
# (vertex index per loop, face order) is identical for the compared range.
# usage: python audit_normals.py C3m.fbx baseline.fbx baseline_unstripped.fbx C4.fbx outdir
import sys,os,json,csv,hashlib,bpy,addon_utils,numpy as np
p=[m for m in addon_utils.modules() if m.__name__=='io_scene_fbx'][0].__file__; sys.path.insert(0,os.path.dirname(os.path.dirname(p)))
from io_scene_fbx import parse_fbx
c3m,base,base_raw,c4,out=sys.argv[-5:]
def find(e,name):
    for c in e.elems:
        if c.id==name: yield c
        yield from find(c,name)
def child(e,name): return [c for c in e.elems if c.id==name][0]
def read(path):
    root,ver=parse_fbx.parse(path); g=next(find(root,b'Geometry'))
    V=np.array(child(g,b'Vertices').props[0]).reshape(-1,3); PVI=np.array(child(g,b'PolygonVertexIndex').props[0])
    ln=child(g,b'LayerElementNormal'); N=np.array(child(ln,b'Normals').props[0]).reshape(-1,3)
    if child(ln,b'ReferenceInformationType').props[0]==b'IndexToDirect': N=N[np.array(child(ln,b'NormalsIndex').props[0])]
    lu=child(g,b'LayerElementUV'); UV=np.array(child(lu,b'UV').props[0]).reshape(-1,2)
    if child(lu,b'ReferenceInformationType').props[0]==b'IndexToDirect': UV=UV[np.array(child(lu,b'UVIndex').props[0])]
    lm=child(g,b'LayerElementMaterial'); M=np.array(child(lm,b'Materials').props[0])
    gs={c.props[0].decode():c.props[-1] for c in child(next(find(root,b'GlobalSettings')),b'Properties70').elems if c.props[0] in (b'UpAxis',b'UpAxisSign',b'FrontAxis',b'FrontAxisSign',b'CoordAxis',b'CoordAxisSign',b'UnitScaleFactor')}
    mats=[m.props[1].split(b'\x00')[0].decode() for m in find(root,b'Material') if len(m.props)>1]
    tex=sorted({c.props[0].decode(errors='replace') for t in find(root,b'Texture') for c in t.elems if c.id in (b'FileName',b'RelativeFilename')})
    loopvert=np.where(PVI<0,-PVI-1,PVI); nfaces=int((PVI<0).sum())
    return dict(path=path,sha256=hashlib.sha256(open(path,'rb').read()).hexdigest(),bytes=os.path.getsize(path),fbx_version=ver,V=V,PVI=PVI,loopvert=loopvert,N=N,UV=UV,M=M,gs=gs,mats=mats,tex=tex,
                verts=len(V),loops=len(PVI),faces=nfaces,bbox=[V.min(0).round(6).tolist(),V.max(0).round(6).tolist()])
F={k:read(v) for k,v in (('C3m_original',c3m),('baseline_passthrough',base),('baseline_unstripped_used_for_C4_check',base_raw),('C4',c4))}
ang=lambda x,y: np.degrees(np.arccos(np.clip((x*y).sum(1)/np.linalg.norm(x,axis=1)/np.linalg.norm(y,axis=1),-1,1)))
def cmp(a,b,n=None):
    A,B=F[a],F[b]; n=n or A['loops']
    same_order=bool(len(B['PVI'])>=n and (A['PVI'][:n]==B['PVI'][:n]).all())
    r={'a':a,'b':b,'compared_loops':n,'loop_order_and_vertex_indices_identical':same_order}
    if not same_order: r['normal_comparison']='NOT CONFIRMED (loop/index order differs)'; return r,None
    d=ang(A['N'][:n],B['N'][:n]); nv=min(A['verts'],B['verts'])
    r.update(max_angle_deg=float(d.max()),mean_angle_deg=float(d.mean()),loops_over_0_05deg=int((d>0.05).sum()),loops_over_0_5deg=int((d>0.5).sum()),
             uv_identical=bool(np.allclose(A['UV'][:n],B['UV'][:n],atol=1e-7)),uv_max_diff=float(np.abs(A['UV'][:n]-B['UV'][:n]).max()),
             material_per_face_identical=(bool((A['M'][:A['faces']]==B['M'][:A['faces']]).all()) if len(A['M'])>1 and len(B['M'])>1 else 'single material index (AllSame) in both'))
    r['vertex_position_max_diff_m_common_range']=float(np.abs(A['V'][:nv]-B['V'][:nv]).max())
    return r,d
results={}; diffs={}
for a,b in (('C3m_original','baseline_passthrough'),('baseline_passthrough','C4'),('C3m_original','C4'),('baseline_unstripped_used_for_C4_check','baseline_passthrough')):
    r,d=cmp(a,b); results[f'{a}__vs__{b}']=r; diffs[f'{a}__vs__{b}']=d
files={k:{x:v[x] for x in ('sha256','bytes','fbx_version','verts','loops','faces','bbox','gs','mats','tex')}|{'path':os.path.basename(v['path'])} for k,v in F.items()}
json.dump({'files':files,'comparisons':results,'threshold_deg':0.05,
  'note':'angles from the Normals arrays written in each FBX (expanded through NormalsIndex). C4 has 564 extra loops (new middle tier) after the original 12660; only the common original range is compared.'},open(f'{out}/audit_normals.json','w'),indent=1,default=str)
n=F['C3m_original']['loops']; lv=F['C3m_original']['loopvert']
with open(f'{out}/loop_normal_diff_table.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['loop','vertex','angle_deg_baseline_vs_C3m','angle_deg_C4_vs_baseline','angle_deg_C4_vs_C3m'])
    a1=diffs['C3m_original__vs__baseline_passthrough']; a2=diffs['baseline_passthrough__vs__C4']; a3=diffs['C3m_original__vs__C4']
    for i in range(n): w.writerow([i,int(lv[i]),f'{a1[i]:.5f}',f'{a2[i]:.5f}',f'{a3[i]:.5f}'])
for k,r in results.items(): print('R',k,{x:r.get(x) for x in ('loop_order_and_vertex_indices_identical','max_angle_deg','loops_over_0_05deg','uv_identical','vertex_position_max_diff_m_common_range')})
for k,v in files.items(): print('F',k,v['sha256'][:16],v['verts'],v['faces'],v['loops'],v['gs'].get('UnitScaleFactor'),v['mats'],v['tex'])
