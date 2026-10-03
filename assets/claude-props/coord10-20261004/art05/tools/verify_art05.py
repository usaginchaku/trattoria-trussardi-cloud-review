# Independent check: candidate vs input atlas with the binary mask.
import sys,json,hashlib,numpy as np
from PIL import Image
I,O=sys.argv[1],sys.argv[2]
A=Image.open(f'{I}/PaintingAtlas_FUR06.png'); C=Image.open(f'{O}/PaintingAtlas_FUR06_ART05_candidate.png'); M=Image.open(f'{O}/PaintingAtlas_FUR06_ART05_shape_change_mask.png')
a=np.array(A.convert('RGB')); c=np.array(C.convert('RGB')); m=np.array(M)
cells={16:(1364,682,1705,1023),17:(1705,682,2046,1023),18:(0,1023,341,1364)}
inc=np.zeros(m.shape,bool)
for x0,y0,x1,y1 in cells.values(): inc[y0:y1,x0:x1]=True
diff=(a!=c).any(2)
r={'input_png':{'size':A.size,'mode':A.mode,'sha256':hashlib.sha256(open(f'{I}/PaintingAtlas_FUR06.png','rb').read()).hexdigest(),'rgb_sha256':hashlib.sha256(a.tobytes()).hexdigest()},
   'candidate_png':{'size':C.size,'mode':C.mode,'sha256':hashlib.sha256(open(f'{O}/PaintingAtlas_FUR06_ART05_candidate.png','rb').read()).hexdigest(),'rgb_sha256':hashlib.sha256(c.tobytes()).hexdigest()},
   'mask_png':{'size':M.size,'mode':M.mode,'values':sorted(np.unique(m).tolist()),'sha256':hashlib.sha256(open(f'{O}/PaintingAtlas_FUR06_ART05_shape_change_mask.png','rb').read()).hexdigest()},
   'mask_nonzero_outside_cells':int(((m>0)&~inc).sum()),'changed_pixels_outside_cells':int((diff&~inc).sum()),'changed_pixels_where_mask_0':int((diff&(m==0)).sum()),
   'rgb_sha256_outside_cells_equal':hashlib.sha256(a[~inc].tobytes()).hexdigest()==hashlib.sha256(c[~inc].tobytes()).hexdigest(),
   'rgb_sha256_mask0_equal':hashlib.sha256(a[m==0].tobytes()).hexdigest()==hashlib.sha256(c[m==0].tobytes()).hexdigest(),'per_cell':{}}
for k,(x0,y0,x1,y1) in cells.items():
    d=diff[y0:y1,x0:x1]; mm=m[y0:y1,x0:x1]>0; ys,xs=np.where(d)
    r['per_cell'][k]={'changed':int(d.sum()),'mask_255':int(mm.sum()),'cell_pixels':(x1-x0)*(y1-y0),'mask_fraction':round(float(mm.mean()),4),
       'changed_bbox_atlas_xyxy_incl':[int(xs.min()+x0),int(ys.min()+y0),int(xs.max()+x0),int(ys.max()+y0)],
       'border_ring_6px_unchanged':bool(not d[:12,:].any() and not d[-12:,:].any() and not d[:,:12].any() and not d[:,-12:].any())}
json.dump(r,open(f'{O}/qa/verify_pixels.json','w'),indent=1); print(json.dumps({k:v for k,v in r.items() if k!='per_cell'}),json.dumps(r['per_cell']))
