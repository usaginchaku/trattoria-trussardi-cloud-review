# Rewrite texture path strings (Path / FileName / Filename) in a Blender-written binary FBX to bare file names,
# so no machine-local absolute path is published. Uses Blender's own FBX parser/encoder (io_scene_fbx); all other data is re-encoded unchanged.
# usage: python fbx_strip_paths.py in.fbx out.fbx
import sys,os,bpy,addon_utils
p=[m for m in addon_utils.modules() if m.__name__=='io_scene_fbx'][0].__file__; sys.path.insert(0,os.path.dirname(os.path.dirname(p)))
from io_scene_fbx import parse_fbx,encode_bin
src,dst=sys.argv[-2],sys.argv[-1]
root,ver=parse_fbx.parse(src)
changed=[]
ADD={b'Y':'add_int16',b'C':'add_bool',b'I':'add_int32',b'F':'add_float32',b'D':'add_float64',b'L':'add_int64',b'R':'add_bytes',b'S':'add_string',
     b'f':'add_float32_array',b'd':'add_float64_array',b'i':'add_int32_array',b'l':'add_int64_array',b'b':'add_bool_array'}
def fix(v):
    if isinstance(v,bytes) and (v.startswith(b'/') or b':\\' in v[:4]) and v.lower().endswith((b'.png',b'.jpg',b'.jpeg',b'.tga')):
        nv=v.replace(b'\\',b'/').rsplit(b'/',1)[-1]; changed.append((v.decode(errors='replace')[-40:],nv.decode())); return nv
    return v
def conv(e):
    o=encode_bin.FBXElem(e.id)
    for v,t in zip(e.props,e.props_type):
        t=bytes([t]); f=getattr(o,ADD[t])
        if t==b'C': f(bool(v))
        elif t==b'S': f(fix(v))
        elif t in b'fdilb': f(v)
        else: f(v)
    for c in e.elems: o.elems.append(conv(c))
    return o
r=encode_bin.FBXElem(b'')
for c in root.elems: r.elems.append(conv(c))
encode_bin.write(dst,r,ver)
print('STRIPPED',len(changed),changed)
