# new process: open the blend copied (byte-identical) to another directory with the same models/ + fbx/ layout; report image resolution
import bpy,sys,os,json,hashlib
bl,out=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=bl); r={'blend_sha256':hashlib.sha256(open(bl,'rb').read()).hexdigest(),'images':[]}
for i in bpy.data.images:
    a=os.path.normpath(bpy.path.abspath(i.filepath)); e=os.path.exists(a); d={'name':i.name,'filepath':i.filepath,'exists':e}
    if e: i.reload(); d.update(size=list(i.size),has_data=bool(i.has_data),png_sha256=hashlib.sha256(open(a,'rb').read()).hexdigest(),resolved_inside_copy=os.path.commonpath([os.path.dirname(bl),a])==os.path.dirname(os.path.dirname(bl)))
    r['images'].append(d)
r['all_resolved']=all(x['exists'] and x.get('has_data') for x in r['images']); json.dump(r,open(out,'w'),indent=1); print(r)
