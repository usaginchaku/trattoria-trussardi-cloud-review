# COORD10-CUT05: rewrite a binary FBX keeping every element/property/array as parsed, with exactly one kind of change:
# properties typed 'B' (bool, written by the earlier fbx_strip_paths.py) are written back as the standard FBX 'C' (1 byte, same value).
# Every other type code is written with the matching encoder (no implicit conversion). usage: python fbx_bool_typecode_repair.py in.fbx out.fbx
import sys,os,bpy,addon_utils
p=[m for m in addon_utils.modules() if m.__name__=='io_scene_fbx'][0].__file__; sys.path.insert(0,os.path.dirname(os.path.dirname(p)))
from io_scene_fbx import parse_fbx,encode_bin
src,dst=sys.argv[-2:]
root,ver=parse_fbx.parse(src)
ADD={b'Y':'add_int16',b'Z':'add_int8',b'I':'add_int32',b'L':'add_int64',b'F':'add_float32',b'D':'add_float64',b'R':'add_bytes',b'S':'add_string',
     b'f':'add_float32_array',b'd':'add_float64_array',b'i':'add_int32_array',b'l':'add_int64_array',b'b':'add_bool_array',b'c':'add_byte_array'}
changed=[]
def conv(e,path=''):
    o=encode_bin.FBXElem(e.id); here=path+'/'+e.id.decode(errors='replace')
    for v,t in zip(e.props,e.props_type):
        t=bytes([t])
        if t==b'B': o.add_char(b'\x01' if v else b'\x00'); changed.append(here)
        elif t==b'C': o.add_char(v if isinstance(v,bytes) else bytes([int(v)]))
        else: getattr(o,ADD[t])(v)
    for c in e.elems: o.elems.append(conv(c,here))
    return o
r=encode_bin.FBXElem(b'')
for c in root.elems: r.elems.append(conv(c))
encode_bin.write(dst,r,ver)
print('REPAIRED',len(changed),changed)
