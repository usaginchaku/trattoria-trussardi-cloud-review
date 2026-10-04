# (revision02: Normals are expanded through NormalsIndex when the file stores IndexToDirect normals)
# compare the raw FBX normal / UV / index arrays (as written in the files, before any importer processing) and the header
# usage: blender-python fbx_raw_normals.py -- a.fbx b.fbx out.json
import sys,os,json,bpy,addon_utils
import numpy as np
p=[m for m in addon_utils.modules() if m.__name__=='io_scene_fbx'][0].__file__; sys.path.insert(0,os.path.dirname(os.path.dirname(p)))
from io_scene_fbx import parse_fbx
a,b,out=sys.argv[sys.argv.index('--')+1:]
def grab(f):
    root,ver=parse_fbx.parse(f); r={'version':ver,'B':0,'props':{}}
    def walk(e,path):
        for t,v in zip(e.props_type,e.props):
            if chr(t)=='B': r['B']+=1
        if e.id==b'P' and e.props and e.props[0] in (b'UnitScaleFactor',b'Lcl Rotation',b'Lcl Scaling',b'Lcl Translation',b'UpAxis',b'FrontAxis'):
            r['props'].setdefault(e.props[0].decode(),[]).append([x for x in e.props[4:]])
        if e.id in (b'Normals',b'NormalsIndex',b'UV',b'UVIndex',b'PolygonVertexIndex',b'Vertices',b'Materials'):
            r.setdefault(path+'/'+e.id.decode(),[]).append(np.array(e.props[0]))
        for c in e.elems: walk(c,path+'/'+e.id.decode())
    walk(root,''); return r
def expand(r):
    k='//Objects/Geometry/LayerElementNormal/'
    if k+'NormalsIndex' in r:
        n=r[k+'Normals'][0].reshape(-1,3); r[k+'Normals(expanded per polygon-vertex)']=[n[r[k+'NormalsIndex'][0]].ravel()]
    return r
A,B=expand(grab(a)),expand(grab(b)); res={'header_a':{'version':A['version'],'B_typed_props':A['B'],'props':A['props']},'header_b':{'version':B['version'],'B_typed_props':B['B'],'props':B['props']},'arrays':{}}
for k in A:
    if isinstance(A[k],list) and k in B and isinstance(A[k][0],np.ndarray):
        x,y=A[k][0],B[k][0]
        res['arrays'][k]={'len':[len(x),len(y)],'identical':bool(len(x)==len(y) and (x==y).all()),'max_abs_diff':float(np.abs(x.astype(float)-y.astype(float)).max()) if len(x)==len(y) else None}
json.dump(res,open(out,'w'),indent=1,default=str); [print(k,v) for k,v in res['arrays'].items()]; print(res['header_a']['props']==res['header_b']['props'],A['B'],B['B'])
