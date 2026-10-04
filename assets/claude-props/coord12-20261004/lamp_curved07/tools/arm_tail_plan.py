# analysis (read-only): for each candidate start ring s of the arm tail region, apply dz(i) = DZ * smoothstep((i-s)/(40-s)) to the
# ring centres (rings s..40, ring 40 = collar end) and report the max bend angle between consecutive ring tangents, compared with the
# original arm's max bend. DZ = -0.29 * Hs (Hs = measured shade height).
# usage: blender-python arm_tail_plan.py -- curved.blend out.json
import bpy,sys,json,math
import numpy as np
bl,out=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=bl); me=bpy.data.objects['CurvedLamp'].data
co=np.array([v.co[:] for v in me.vertices]); arm=co[96:588].reshape(41,12,3); C=arm.mean(1)
sh=co[1020-314+314:0] if False else None
shade=co[710:1416] if False else None
# shells by fixed index ranges verified in LAMP03: plate 0-95, arm 96-587, collar 588-709, shade 710-1415, diffuser 1416-1561
Hs=float(co[710:1416,2].max()-co[710:1416,2].min()); DZ=-0.29*Hs
def bends(c):
    t=np.diff(c[:,1:],axis=0); t/=np.linalg.norm(t,axis=1)[:,None]
    return np.degrees(np.arccos(np.clip((t[1:]*t[:-1]).sum(1),-1,1)))
b0=bends(C); res={'Hs':Hs,'DZ':DZ,'orig_max_bend_deg':float(b0.max()),'candidates':[]}
ib=int(np.argmin(C[:,2]))
for s in range(ib+1,40):
    w=np.zeros(41); u=(np.arange(41)-s)/(40-s); m=np.arange(41)>=s; w[m]=3*u[m]**2-2*u[m]**3
    c=C.copy(); c[:,2]+=DZ*w; b=bends(c)
    mono=bool((np.diff(c[ib:,2])>0).all())
    res['candidates'].append({'s':s,'rings_moved':int((w>0).sum()),'max_bend_deg':float(b.max()),'rising_branch_monotonic':mono,'end_z':float(c[-1,2])})
ok=[x for x in res['candidates'] if x['max_bend_deg']<=res['orig_max_bend_deg']+1e-9 and x['rising_branch_monotonic']]
res['bottom_ring']=ib; res['chosen']=max(ok,key=lambda x:x['s']) if ok else None
json.dump(res,open(out,'w'),indent=1); print('Hs',Hs,'DZ',DZ,'orig max bend',b0.max(),'bottom ring',ib); [print(x) for x in res['candidates']]; print('chosen',res['chosen'])
