# full FBX tree diff (every element, property value and type code) between two FBX files; arrays compared by value.
import sys,os,json,bpy,addon_utils,numpy as np
p=[m for m in addon_utils.modules() if m.__name__=='io_scene_fbx'][0].__file__; sys.path.insert(0,os.path.dirname(os.path.dirname(p)))
from io_scene_fbx import parse_fbx
a,b,outp=sys.argv[-3:]
ra,_=parse_fbx.parse(a); rb,_=parse_fbx.parse(b); diffs=[]
def same(x,y):
    try: return np.array_equal(np.asarray(x),np.asarray(y))
    except Exception: return x==y
def walk(x,y,path):
    if x.id!=y.id: diffs.append({'path':path,'kind':'element id','a':x.id.decode(errors='replace'),'b':y.id.decode(errors='replace')}); return
    for i,(va,vb,ta,tb) in enumerate(zip(x.props,y.props,x.props_type,y.props_type)):
        if ta!=tb or not same(va,vb):
            short=lambda v: (f'array len {len(v)}' if hasattr(v,'__len__') and not isinstance(v,(bytes,str)) else repr(v)[:60])
            diffs.append({'path':path+f'/prop{i}','type_a':chr(ta),'type_b':chr(tb),'a':short(va),'b':short(vb)})
    if len(x.props)!=len(y.props): diffs.append({'path':path,'kind':'prop count'})
    if len(x.elems)!=len(y.elems): diffs.append({'path':path,'kind':'child count'})
    names={}
    for i,(cx,cy) in enumerate(zip(x.elems,y.elems)):
        nm=cx.id.decode(errors='replace'); k=names.get(nm,0); names[nm]=k+1
        lbl=nm+(f'[{k}]' if k else '')
        if cx.id==b'LayerElementUV': lbl+=f"({[c.props[0] for c in cx.elems if c.id==b'Name'][0].decode()})"
        walk(cx,cy,path+'/'+lbl)
walk(ra,rb,'')
json.dump({'a':os.path.basename(a),'b':os.path.basename(b),'differences':diffs},open(outp,'w'),indent=1); print('DIFF',len(diffs),[d['path'] for d in diffs])
