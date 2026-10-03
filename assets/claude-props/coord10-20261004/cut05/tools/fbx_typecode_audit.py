# audit: FBX property type codes in every FBX under the given roots. 'B' is not a documented FBX binary type
# (booleans are 'C', 1 byte); Blender reads it, other importers (Autodesk FBX SDK / Unity) are unverified.
import sys,os,json,collections,bpy,addon_utils
p=[m for m in addon_utils.modules() if m.__name__=='io_scene_fbx'][0].__file__; sys.path.insert(0,os.path.dirname(os.path.dirname(p)))
from io_scene_fbx import parse_fbx
roots=sys.argv[sys.argv.index('--')+1:-1]; out=[]
def walk(e,where,path=''):
    for t,v in zip(e.props_type,e.props):
        if chr(t)=='B': where.append(path+'/'+e.id.decode(errors='replace'))
    for c in e.elems: walk(c,where,path+'/'+e.id.decode(errors='replace'))
for r in roots:
    for d,_,fs in os.walk(r):
        for f in sorted(fs):
            if not f.lower().endswith('.fbx'): continue
            fp=os.path.join(d,f); w=[]
            try: root,_=parse_fbx.parse(fp); walk(root,w)
            except Exception as ex: w=[f'PARSE ERROR {ex}']
            out.append({'file':os.path.relpath(fp,os.path.dirname(os.path.dirname(r.rstrip('/')))),'B_typed_props':len(w),'where':sorted(set(w))})
json.dump({'note':"'B' type code found = written by the earlier tools/fbx_strip_paths.py (bool -> 'B'); value is the same as the standard 'C' 1-byte bool",'files':out},open(sys.argv[-1],'w'),indent=1)
print('AUD',sum(1 for o in out if o['B_typed_props']),'of',len(out),'files have B'); [print('  ',o['file'],o['B_typed_props']) for o in out if o['B_typed_props']]
