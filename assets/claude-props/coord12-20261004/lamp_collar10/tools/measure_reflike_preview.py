# visible collar width in the model-only ref_like_jamb preview of lamp_curved07/revision02 (plate is offset to the side in this view, so the
# dark run directly under the cup is the collar). Ratio = widest dark run per row / cup max width (cream run), rows from the cup bottom down.
# usage: (numpy python, e.g. the bpy venv) measure_reflike_preview.py preview.png out.json
import sys,json
import numpy as np
from PIL import Image
p,out=sys.argv[1:3]
a=np.asarray(Image.open(p).convert('RGB')).astype(int); lum=a.mean(2); dark=lum<110; cream=(a[:,:,1]>150)&(a[:,:,2]<a[:,:,1]-25)
rows=np.where(cream.any(1))[0]; ws=max(np.where(cream[r])[0].ptp()+1 for r in rows); bot=int(rows.max())
res=[]
for r in range(bot-3,bot+30):
    xs=np.where(dark[r])[0]
    if len(xs):
        runs=np.split(xs,np.where(np.diff(xs)>1)[0]+1); run=max(runs,key=len); res.append({'row':r,'dark_run_px':len(run),'ratio':round(len(run)/ws,3)})
json.dump({'preview':p.split('/')[-1],'cup_max_width_px':int(ws),'cup_bottom_row':bot,'rows':res},open(out,'w'),indent=1)
print(ws,[(x['row'],x['ratio']) for x in res])
