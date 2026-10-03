# ART02 A2: per-frame FinishAtlas copies, only where IMG_3638 shows a hue difference that exposure alone cannot explain.
# Reference colours are white-balance corrected with the wall: factor = observed wall / model cream cell (assumption: the wall is
# the same cream as the model's cream cell). Each target cell is shifted by (target - cell mean), keeping the cell's texture variation.
import json,hashlib,numpy as np
from PIL import Image
R='src2/assets/codex-source/coord10-art02-input-20261004/'
A=np.array(Image.open(R+'FinishAtlas_FUR06.png').convert('RGB')).astype(int)
cell=lambda cx,cy: (slice(cy*256,cy*256+256),slice(cx*256,cx*256+256))
cream=A[cell(0,1)].reshape(-1,3).mean(0)
wall_obs=np.array([208,216,189]); wb=wall_obs/cream
obs={'U1_mat':[211,210,185],'U2_frame':[110,81,76]}
corr={k:(np.array(v)/wb).round().astype(int).tolist() for k,v in obs.items()}
PLAN={1:[('blue_mat_cell(1,1)',(1,1),corr['U1_mat'])],2:[('pink_frame_cell(3,0)',(3,0),corr['U2_frame'])]}
info={'white_balance_factor':wb.round(4).tolist(),'model_cream_mean':cream.round(1).tolist(),'observed':obs,'corrected_targets':corr,'frames':{}}
for n,ops in PLAN.items():
    B=A.copy(); mask=np.ones(A.shape[:2],bool); cells={}
    for name,(cx,cy),tgt in ops:
        sl=cell(cx,cy); m=A[sl].reshape(-1,3).mean(0); B[sl]=np.clip(A[sl]-m+np.array(tgt),0,255); mask[sl]=False
        cells[name]={'from_mean':m.round(1).tolist(),'to':tgt,'rect_xywh':[cx*256,cy*256,256,256]}
    out=f'art2/FinishAtlas_FUR06_ART02_A2_U{n}.png'; Image.fromarray(B.astype(np.uint8)).save(out,optimize=True)
    C=np.array(Image.open(out).convert('RGBA')); S=np.array(Image.open(R+'FinishAtlas_FUR06.png').convert('RGBA'))
    d=(C!=S).any(-1)
    info['frames'][f'LAY03_UpperFrame_{n}']={'texture':out.split('/')[-1],'cells':cells,'pixels_changed_outside_cells':int((d&mask).sum()),'pixels_changed_inside':int((d&~mask).sum()),
       'rgba_sha256_outside_source':hashlib.sha256(S[mask].tobytes()).hexdigest(),'rgba_sha256_outside_candidate':hashlib.sha256(C[mask].tobytes()).hexdigest()}
info['frames']['LAY03_UpperFrame_3']='no A2: frame olive and mat cream match within exposure; lavender inner border cannot be separated (shares the cream cell with the mat)'
json.dump(info,open('art2/A2_check.json','w'),indent=1); print(json.dumps(info,indent=0)[:1500])
