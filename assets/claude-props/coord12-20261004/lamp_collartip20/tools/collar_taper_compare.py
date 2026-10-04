# compare the visible collar taper (front view) between the reference (LAMP18 numeric row profile, read from
# ../lamp_plateheight18/qa/vertical_profile.json - numbers only) and the model (front-ortho union silhouette of collar + plate computed
# from geometry). Collar visible span: reference = collar top row -> first row of the tip band (tip band = rows within 1 px of the
# minimum, EXCLUDED as collar/rod-ambiguous); model = shade bottom z 0.18 -> collar bottom z 0.145. Compared at fractions f of that span.
# usage: blender-python collar_taper_compare.py -- profile.json model.blend out.json
import bpy,sys,json
import numpy as np
pj,bl,out=sys.argv[sys.argv.index('--')+1:]
P=json.load(open(pj)); CUP={'IMG_3594_left':62,'IMG_3594_right':64,'IMG_3675':63}
TOP={'IMG_3594_left':368,'IMG_3594_right':371,'IMG_3675':422}
ref={}
for k,v in P['lamps'].items():
    rows={r['y']:r['w'] for r in v['rows']}; ys=[y for y in sorted(rows) if TOP[k]<=y<=TOP[k]+16]
    wmin=min(rows[y] for y in ys if y<=TOP[k]+14); tip0=min(y for y in ys if rows[y]<=wmin+1)
    span=[y for y in ys if TOP[k]<=y<tip0]; n=len(span)
    ref[k]={'collar_top_row':TOP[k],'tip_band_first_row':tip0,'rows':[{'f':round(i/(n-1),3) if n>1 else 0,'y':y,'w_px':rows[y],'w_Ws':round(rows[y]/CUP[k],3)} for i,y in enumerate(span)]}
bpy.ops.wm.open_mainfile(filepath=bl); co=np.array([v.co[:] for v in bpy.data.objects['StraightLamp'].data.vertices])
pl=co[0:96]; col=co[96:218]; cy=(col[:,1].min()+col[:,1].max())/2; Ws=0.222
rings=sorted({round(z,5) for z in col[:,2]}); rr={z:float(np.hypot(col[np.abs(col[:,2]-z)<1e-5,0],col[np.abs(col[:,2]-z)<1e-5,1]-cy).max()) for z in rings}
zt,zb=0.18,0.145; ptop=float(pl[:,2].max()); pw=float(pl[:,0].max()-pl[:,0].min())
def model_w(z):
    r=np.interp(z,[zb,0.18,0.19],[rr[zb],rr[0.18],rr[0.19]]); w=2*r
    return max(w,pw) if z<=ptop else w, 2*r
fs=[0,0.25,0.5,0.6,0.7,0.8,0.9,1.0]
mod=[{'f':f,'z':round(zt-f*(zt-zb),4),'union_w_Ws':round(model_w(zt-f*(zt-zb))[0]/Ws,3),'collar_only_w_Ws':round(model_w(zt-f*(zt-zb))[1]/Ws,3)} for f in fs]
def ref_at(k,f):
    xs=[r['f'] for r in ref[k]['rows']]; ws=[r['w_Ws'] for r in ref[k]['rows']]; return float(np.interp(f,xs,ws))
cmp=[{'f':f,'model_union':m['union_w_Ws'],'ref':{k:round(ref_at(k,f),3) for k in ref},'diff_px':{k:round((m['union_w_Ws']-ref_at(k,f))*CUP[k],1) for k in ref}} for f,m in zip(fs,mod)]
res={'reference':ref,'model':{'collar_rings_z_r':rr,'plate_top_z':ptop,'plate_width_Ws':round(pw/Ws,3),'profile':mod},'comparison':cmp,
 'error_px':'+-1 px per edge (+-2 px width), +-1 row in the f position; moire does not move dark edges by more than ~1 px'}
json.dump(res,open(out,'w'),indent=1)
for c in cmp: print(c)
print('rings',rr,'plate top',ptop)
