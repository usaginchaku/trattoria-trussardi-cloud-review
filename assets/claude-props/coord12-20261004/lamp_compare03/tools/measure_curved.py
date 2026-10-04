# model-side numbers for the arm comparison (Curved L1 blend, read-only). Units m; ratios use shade height Hs and shade width Ws.
import bpy,sys,json
import numpy as np
bl,out=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=bl); o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
co=np.array([v.co[:] for v in me.vertices]); n=len(co); par=list(range(n))
def f(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
for e in me.edges:
    a,b=f(e.vertices[0]),f(e.vertices[1])
    if a!=b: par[a]=b
sh={}
for i in range(n): sh.setdefault(f(i),[]).append(i)
S=sorted(sh.values(),key=lambda v:min(v)); bb=lambda v:(co[v].min(0),co[v].max(0))
plate,arm,collar,shade=S[0],S[1],S[2],S[3]
(p0,p1),(c0,c1),(s0,s1)=bb(plate),bb(collar),bb(shade)
Hs=s1[2]-s0[2]; Ws=s1[0]-s0[0]
a=co[sorted(arm)].reshape(41,12,3).mean(1)
ib=int(np.argmin(a[:,2])); reach=a[0,1]-a[-1,1]
r={'shade_W':Ws,'shade_H':Hs,'shade_WH':Ws/Hs,'plate_h':p1[2]-p0[2],'plate_w':p1[0]-p0[0],'plate_t':p1[1]-p0[1],'collar_bottom_z':c0[2],'collar_top_w':c1[0]-c0[0],
 'arm_radius':0.012,'arm_rings':41,'arm_exit_center':a[0].tolist(),'arm_bottom_center':a[ib].tolist(),'arm_end_center':a[-1].tolist(),
 'ratios':{'plate_h/Ws':(p1[2]-p0[2])/Ws,'plate_h/Hs':(p1[2]-p0[2])/Hs,'arm_thickness/Ws':0.024/Ws,'collar_w/Ws':(c1[0]-c0[0])/Ws,
   'plate_top_rel_collar_bottom/Hs':(p1[2]-c0[2])/Hs,'plate_bottom_rel_collar_bottom/Hs':(p0[2]-c0[2])/Hs,
   'arm_exit_rel_collar_bottom/Hs':(a[0][2]-c0[2])/Hs,'arm_exit_from_plate_top/plate_h':(p1[2]-a[0][2])/(p1[2]-p0[2]),
   'arm_bottom_outer_rel_collar_bottom/Hs':(a[ib][2]-0.012-c0[2])/Hs,'arm_bottom_position_along_reach':(a[0,1]-a[ib,1])/reach,
   'drop_exit_to_bottom/Hs':(a[0][2]-a[ib][2])/Hs}}
json.dump(r,open(out,'w'),indent=1,default=float); print(json.dumps(r['ratios'],indent=0,default=float))
