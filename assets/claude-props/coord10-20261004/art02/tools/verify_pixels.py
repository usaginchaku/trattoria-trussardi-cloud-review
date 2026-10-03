# Independent check (separate from the generators): decoded RGBA of every candidate PNG equals the input outside the allowed area.
# usage: python verify_pixels.py <input_dir> <art02_dir>
import sys,json,hashlib,numpy as np
from PIL import Image
inp,art=sys.argv[1],sys.argv[2]
scope=json.load(open(f'{inp}/frame_scope.json'))
rgba=lambda p: np.array(Image.open(p).convert('RGBA'))
res={}
P0=rgba(f'{inp}/PaintingAtlas_FUR06.png'); P1=rgba(f'{art}/A1/PaintingAtlas_FUR06_ART02_A1.png')
allowed=np.zeros(P0.shape[:2],bool); x0,y0,x1,y1=[f for f in scope['frames'] if f['name']=='LAY03_UpperFrame_1'][0]['editablePixelRectExclusive']; allowed[y0:y1,x0:x1]=True
d=(P0!=P1).any(-1)
res['A1']={'size':[P1.shape[1],P1.shape[0]],'allowed_rect_UpperFrame_1':[x0,y0,x1,y1],'changed_outside_allowed':int((d&~allowed).sum()),'changed_inside':int((d&allowed).sum()),
  'outside_rgba_sha256_input':hashlib.sha256(P0[~allowed].tobytes()).hexdigest(),'outside_rgba_sha256_candidate':hashlib.sha256(P1[~allowed].tobytes()).hexdigest()}
for f in scope['frames']:
    if f['name']=='LAY03_UpperFrame_1': continue
    a,b,c,e=f['editablePixelRectExclusive']; res['A1'][f'{f["name"]}_tile_identical']=bool((P0[b:e,a:c]==P1[b:e,a:c]).all())
F0=rgba(f'{inp}/FinishAtlas_FUR06.png')
for n,(cx,cy) in ((1,(1,1)),(2,(3,0))):
    F1=rgba(f'{art}/A2/FinishAtlas_FUR06_ART02_A2_U{n}.png'); al=np.zeros(F0.shape[:2],bool); al[cy*256:cy*256+256,cx*256:cx*256+256]=True; d=(F0!=F1).any(-1)
    res[f'A2_U{n}']={'size':[F1.shape[1],F1.shape[0]],'allowed_cell_xywh':[cx*256,cy*256,256,256],'changed_outside_allowed':int((d&~al).sum()),'changed_inside':int((d&al).sum()),
      'outside_rgba_sha256_input':hashlib.sha256(F0[~al].tobytes()).hexdigest(),'outside_rgba_sha256_candidate':hashlib.sha256(F1[~al].tobytes()).hexdigest()}
json.dump(res,open(f'{art}/qa/verify_pixels.json','w'),indent=1); print(json.dumps(res,indent=0))
