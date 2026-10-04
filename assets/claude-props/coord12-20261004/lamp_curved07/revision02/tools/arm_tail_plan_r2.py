# revision02 plan: same smoothstep tail as ../tools/arm_tail_plan.py, but the chosen start ring must ALSO keep the arm centre-line free
# of new inflections (signed curvature of the YZ centre line keeps one sign, like the original arm) in addition to
# max ring-to-ring bend <= original max and a monotonic rising branch. Reason: C1 (S=26) passed the old criteria but showed an S-shaped
# plateau on the rising branch in the side view.
# usage: blender-python arm_tail_plan_r2.py -- curved.blend out.json
import bpy,sys,json
import numpy as np
bl,out=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=bl); me=bpy.data.objects['CurvedLamp'].data
co=np.array([v.co[:] for v in me.vertices]); C=co[96:588].reshape(41,12,3).mean(1)
Hs=float(co[710:1416,2].max()-co[710:1416,2].min()); DZ=-0.29*Hs
def bends(c):
    t=np.diff(c[:,1:],axis=0); t/=np.linalg.norm(t,axis=1)[:,None]; return np.degrees(np.arccos(np.clip((t[1:]*t[:-1]).sum(1),-1,1)))
def signed_curv(c):
    t=np.diff(c[:,1:],axis=0); cr=t[:-1,0]*t[1:,1]-t[:-1,1]*t[1:,0]; return cr
c0=signed_curv(C); sgn0=np.sign(c0[np.abs(c0)>1e-9])
res={'Hs':Hs,'DZ':DZ,'orig_max_bend_deg':float(bends(C).max()),'orig_curvature_sign_changes':int((np.diff(sgn0)!=0).sum()),'candidates':[]}
ib=int(np.argmin(C[:,2]))
for s in range(ib,40):
    w=np.zeros(41); u=(np.arange(41)-s)/(40-s); m=np.arange(41)>s; w[m]=3*u[m]**2-2*u[m]**3
    c=C.copy(); c[:,2]+=DZ*w; k=signed_curv(c); sg=np.sign(k[np.abs(k)>1e-9])
    res['candidates'].append({'s':s,'rings_moved':int((w>0).sum()),'max_bend_deg':float(bends(c).max()),'rising_monotonic':bool((np.diff(c[ib:,2])>0).all()),
        'curvature_sign_changes':int((np.diff(sg)!=0).sum()),'min_signed_curv':float(k.min()),'max_signed_curv':float(k.max())})
ok=[x for x in res['candidates'] if x['max_bend_deg']<=res['orig_max_bend_deg']+1e-9 and x['rising_monotonic'] and x['curvature_sign_changes']==res['orig_curvature_sign_changes']]
res['chosen']=max(ok,key=lambda x:x['s']) if ok else None
json.dump(res,open(out,'w'),indent=1)
print('orig sign changes',res['orig_curvature_sign_changes']); [print(x['s'],x['rings_moved'],round(x['max_bend_deg'],2),x['rising_monotonic'],x['curvature_sign_changes']) for x in res['candidates']]; print('chosen',res['chosen'])
