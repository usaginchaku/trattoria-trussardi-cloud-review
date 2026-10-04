# raw FBX check (Blender's own FBX parser, read-only): GlobalSettings axes/unit, Model Lcl transforms, property type codes ('B' = non-standard bool),
# absolute-path / scratch strings in the file bytes. usage: blender-python fbx_header_check.py -- a.fbx b.fbx out.json
import sys,os,json,bpy,addon_utils
p=[m for m in addon_utils.modules() if m.__name__=='io_scene_fbx'][0].__file__; sys.path.insert(0,os.path.dirname(os.path.dirname(p)))
from io_scene_fbx import parse_fbx
fs=sys.argv[sys.argv.index('--')+1:-1]; res={}
def walk(e,acc,path=''):
    pth=path+'/'+e.id.decode(errors='replace')
    for t,v in zip(e.props_type,e.props):
        if chr(t)=='B': acc['B'].append(pth)
    if e.id==b'P' and e.props and isinstance(e.props[0],bytes):
        n=e.props[0].decode(errors='replace')
        if n in ('UpAxis','UpAxisSign','FrontAxis','FrontAxisSign','CoordAxis','CoordAxisSign','UnitScaleFactor','OriginalUnitScaleFactor','Lcl Translation','Lcl Rotation','Lcl Scaling','PreRotation'):
            acc['props'].setdefault(path.split('/')[-1]+':'+n,[]).append([x if not isinstance(x,bytes) else x.decode(errors='replace') for x in e.props[4:]])
    for c in e.elems: walk(c,acc,pth)
for f in fs:
    root,ver=parse_fbx.parse(f); acc={'B':[],'props':{}}; walk(root,acc); b=open(f,'rb').read()
    res[os.path.basename(f)]={'fbx_version':ver,'B_typed_props':len(acc['B']),'B_where':sorted(set(acc['B'])),'props':acc['props'],
      'contains_/tmp':b.count(b'/tmp'),'contains_scratchpad':b.count(b'scratchpad'),'contains_/home':b.count(b'/home'),'contains_C:':b.count(b'C:\\'),
      'texture_strings':sorted(set(x.decode(errors='replace') for x in __import__('re').findall(rb'[\w./\\:-]*FUR05\.png',b)))}
json.dump(res,open(sys.argv[-1],'w'),indent=1); print(json.dumps(res,indent=0)[:2500])
