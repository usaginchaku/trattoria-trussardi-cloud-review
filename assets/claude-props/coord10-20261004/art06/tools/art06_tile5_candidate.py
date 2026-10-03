# COORD10-ART06: F19-only FinishAtlas copy, recolour tile5 (col1,row1 = px x256-511, y256-511) from light blue toward low-saturation lavender.
# Basis = RELATIVE hue/saturation difference only (numbers recorded in ART06P qa/cell_stats_and_hue.txt); no reference pixels are read here.
#   target hue = model tile4 hue (F17/F18 mat colour)  + (ref F19 mat hue - mean ref F17/F18 mat hue)
#   target sat = model tile4 sat * (ref F19 mat sat / mean ref F17/F18 mat sat)
#   V (max channel) of the tile5 mean is kept; every pixel keeps its own offset from the old mean (fine variation preserved exactly up to clipping).
# usage: python art06_tile5_candidate.py input_FinishAtlas.png out_candidate.png out_mask.png out_log.json
import sys,json,colorsys,numpy as np
from PIL import Image
src,out,mout,logp=sys.argv[1:5]
im=Image.open(src); mode=im.mode; a=np.asarray(im).astype(np.int32)
assert mode=='RGB' and a.shape==(1024,1024,3), (mode,a.shape)
Y0,Y1,X0,X1=256,512,256,512
REF_F19=(249.2,0.057); REF_F17=(57.9,0.124); REF_F18=(54.0,0.132)   # ART06P recorded HSV numbers (hue deg, sat)
t4=a[256:512,0:256].reshape(-1,3).mean(0); h4,s4,v4=colorsys.rgb_to_hsv(*(t4/255))
dh=REF_F19[0]-(REF_F17[0]+REF_F18[0])/2; sr=REF_F19[1]/((REF_F17[1]+REF_F18[1])/2)
th=(h4*360+dh)%360; ts=s4*sr
cell=a[Y0:Y1,X0:X1]; m0=cell.reshape(-1,3).mean(0); h5,s5,v5=colorsys.rgb_to_hsv(*(m0/255))
m1=np.array(colorsys.hsv_to_rgb(th/360,ts,v5))*255
new=np.clip(np.rint(cell-m0+m1),0,255).astype(np.int32)
b=a.copy(); b[Y0:Y1,X0:X1]=new
Image.fromarray(b.astype(np.uint8),'RGB').save(out,optimize=False)
mask=(np.any(b!=a,axis=2)*255).astype(np.uint8); Image.fromarray(mask,'L').save(mout)
lum=lambda c:float(0.2126*c[0]+0.7152*c[1]+0.0722*c[2])
nm=new.reshape(-1,3).mean(0)
log={'method':'mean shift in RGB: new = old - old_mean + target_mean (rounded, clipped); target_mean = HSV(target_hue, target_sat, V of old mean)',
 'relative_basis':{'ref_hue_delta_F19_minus_F17F18_deg':round(dh,2),'ref_sat_ratio_F19_over_F17F18':round(sr,4),
   'model_tile4_hsv':[round(h4*360,2),round(s4,4),round(v4,4)],'target_hue_deg':round(th,2),'target_sat':round(ts,4)},
 'tile5_before':{'mean_rgb':[round(x,2) for x in m0],'hsv':[round(h5*360,2),round(s5,4),round(v5,4)],'std':[round(x,3) for x in cell.reshape(-1,3).std(0)],
   'min':cell.reshape(-1,3).min(0).tolist(),'max':cell.reshape(-1,3).max(0).tolist(),'rec709_luma':round(lum(m0),2)},
 'tile5_after':{'target_mean_rgb':[round(x,2) for x in m1],'mean_rgb':[round(x,2) for x in nm],
   'hsv':[round(x,4) for x in (lambda h,s,v:(h*360,s,v))(*colorsys.rgb_to_hsv(*(nm/255)))],'std':[round(x,3) for x in new.reshape(-1,3).std(0)],
   'min':new.reshape(-1,3).min(0).tolist(),'max':new.reshape(-1,3).max(0).tolist(),'rec709_luma':round(lum(nm),2)},
 'rec709_luma_delta':round(lum(nm)-lum(m0),2),'clipped_values':int(((cell-m0+m1)<0).sum()+((cell-m0+m1)>255).sum()),
 'changed_pixels':int((mask>0).sum())}
json.dump(log,open(logp,'w'),indent=1); print(json.dumps(log,indent=1))
