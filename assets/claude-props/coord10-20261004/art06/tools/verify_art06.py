# independent check of the ART06 candidate against the input FinishAtlas (decoded pixels)
# usage: python verify_art06.py input.png candidate.png mask.png out.json
import sys,json,hashlib,numpy as np
from PIL import Image
I,C,M,O=sys.argv[1:5]
def info(p):
    im=Image.open(p); return im,{'mode':im.mode,'size':list(im.size),'file_sha256':hashlib.sha256(open(p,'rb').read()).hexdigest(),
      'decoded_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'rgba_sha256':hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()}
ii,ri=info(I); ci,rc=info(C); mi,rm=info(M)
a=np.asarray(ii).astype(int); b=np.asarray(ci).astype(int); m=np.asarray(mi)
diff=np.any(a!=b,axis=2)
t5=np.zeros(diff.shape,bool); t5[256:512,256:512]=True
cells={}
for t in range(16):
    r,c=divmod(t,4); cells[t]=int(diff[r*256:(r+1)*256,c*256:(c+1)*256].sum())
res={'input':ri,'candidate':rc,'mask':rm,
 'same_mode_and_size':ri['mode']==rc['mode'] and ri['size']==rc['size'],
 'mask_values':sorted(int(v) for v in np.unique(m)),
 'mask_nonzero_outside_tile5':int(((m>0)&~t5).sum()),
 'mask_equals_changed_pixels':bool(((m>0)==diff).all()),
 'changed_pixels_total':int(diff.sum()),'changed_pixels_outside_mask':int((diff&(m==0)).sum()),'changed_pixels_outside_tile5':int((diff&~t5).sum()),
 'changed_pixels_per_cell':cells,
 'unchanged_cells_identical':{f'tile{t}':cells[t]==0 for t in range(16) if t!=5},
 'named_regions_identical':{'tile1_back_board':cells[1]==0,'tile3_outer_frame':cells[3]==0,'tile4_inner_rim':cells[4]==0}}
res['PASS']=bool(res['same_mode_and_size'] and res['mask_values']==[0,255] and res['mask_nonzero_outside_tile5']==0 and res['mask_equals_changed_pixels']
  and res['changed_pixels_outside_tile5']==0 and all(res['unchanged_cells_identical'].values()))
json.dump(res,open(O,'w'),indent=1); print(json.dumps({k:res[k] for k in ('same_mode_and_size','mask_values','mask_nonzero_outside_tile5','changed_pixels_total','changed_pixels_outside_tile5','named_regions_identical','PASS')}))
