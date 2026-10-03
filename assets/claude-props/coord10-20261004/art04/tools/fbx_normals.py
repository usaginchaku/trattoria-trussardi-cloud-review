# compare the per-polygon-vertex normals actually WRITTEN in two FBX files (no Blender import heuristics)
import sys,os,bpy,addon_utils,numpy as np
p=[m for m in addon_utils.modules() if m.__name__=='io_scene_fbx'][0].__file__; sys.path.insert(0,os.path.dirname(os.path.dirname(p)))
from io_scene_fbx import parse_fbx
def find(e,name):
    for c in e.elems:
        if c.id==name: yield c
        yield from find(c,name)
def normals(path):
    root,_=parse_fbx.parse(path)
    ln=next(find(root,b'LayerElementNormal'))
    arr=[c for c in ln.elems if c.id==b'Normals'][0].props[0]
    mapping=[c for c in ln.elems if c.id==b'MappingInformationType'][0].props[0]
    ref=[c for c in ln.elems if c.id==b'ReferenceInformationType'][0].props[0]
    v=np.array(arr).reshape(-1,3)
    if ref==b'IndexToDirect':
        idx=np.array([c for c in ln.elems if c.id==b'NormalsIndex'][0].props[0]); v=v[idx]
    return v,mapping+b'/'+ref
a,ma=normals(sys.argv[-2]); b,mb=normals(sys.argv[-1])
print('FN',ma,mb,len(a),len(b))
if len(a)==len(b):
    d=np.abs(a-b).max(1); print('FN loops differing >1e-3:',int((d>1e-3).sum()),'max',float(d.max()))
