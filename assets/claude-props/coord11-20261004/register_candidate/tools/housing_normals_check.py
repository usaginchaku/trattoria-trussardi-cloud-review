# loop-normal vs face-normal deviation on the upper housing shell (faces > 10 cm^2 = large flat faces; thin 2 mm bevel strips are smooth by design and excluded), input vs candidate
import bpy
import sys,json,math
from mathutils import Vector
r={}
for tag,p in zip(('input','candidate'),sys.argv[sys.argv.index('--')+1:-1]):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p); o=[x for x in bpy.context.scene.objects if x.type=='MESH'][0]; me=o.data
    ln=me.corner_normals; dev=[]
    for f in me.polygons:
        if f.area<1e-3: continue
        c=[me.vertices[v].co for v in f.vertices]
        if not (min(x.z for x in c)>0.0675 and min(abs(x.x) for x in c)<0.146 and f.material_index==0): continue
        if max(x.z for x in c)>0.2455 or min(x.z for x in c)<0.0679: pass
        dev.append(max(math.degrees(ln[l].vector.angle(f.normal)) for l in f.loop_indices))
    r[tag]={'large_faces':len(dev),'max_dev_deg':round(max(dev),3) if dev else None,'mean_dev_deg':round(sum(dev)/len(dev),3) if dev else None}
json.dump(r,open(sys.argv[-1],'w'),indent=1); print(r)
