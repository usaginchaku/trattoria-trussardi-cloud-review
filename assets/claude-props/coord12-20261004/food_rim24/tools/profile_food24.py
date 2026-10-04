# upper-surface cross-section (Blender z up) per ring of the welded upper surface, B0 vs C1, with segment slopes. usage: blender-python profile_food24.py -- b0.blend c1.blend out.json
import bpy,sys,json,math
import numpy as np
b0,c1,out=sys.argv[sys.argv.index('--')+1:]
def prof(p):
    bpy.ops.wm.open_mainfile(filepath=p); me=[o for o in bpy.data.objects if o.type=='MESH'][0].data
    co=np.array([v.co[:] for v in me.vertices]); nz=np.empty(len(me.vertices)*3); me.vertices.foreach_get('normal',nz)
    up=set(v for p_ in me.polygons for v in p_.vertices if p_.normal.z>0.2)
    rings={}
    for v in up: rings.setdefault(round(float(np.hypot(co[v,0],co[v,1])),4),[]).append(float(co[v,2]))
    pts=sorted((r,float(np.mean(z))) for r,z in rings.items())
    seg=[{'from_r':a[0],'to_r':b[0],'rise_m':round(b[1]-a[1],5),'slope_deg':round(math.degrees(math.atan2(b[1]-a[1],b[0]-a[0])),2)} for a,b in zip(pts,pts[1:])]
    return {'rings_r_z':pts,'segments':seg}
res={'B0':prof(b0),'C1':prof(c1)}; json.dump(res,open(out,'w'),indent=1)
for k in res: print(k,[(r,round(z,4)) for r,z in res[k]['rings_r_z']]); print('  ',[(s['from_r'],s['to_r'],s['slope_deg']) for s in res[k]['segments']])
