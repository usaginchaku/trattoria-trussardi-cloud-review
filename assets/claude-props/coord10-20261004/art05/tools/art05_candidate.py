# COORD10-ART05: replace only the grey placeholder foreground in painting cells 16/17/18 (Left_Frame_17/18/19).
# Composition follows the ART05P review of DU_ep10-4 (private, not stored): F17 = low horizontal band of rounded bumps,
# F18 = wide middle-low mass with a bumpy top (left end a little darker), F19 = 2-3 lobed cluster upper-centre.
# Exact count/outline/subject are HOLD; shapes are self-authored soft blobs (no reference pixels).
# Rules: old foreground pixels are returned to the cell's unchanged background colour; new shapes are composited over it;
# mask = old footprint | new footprint (incl. soft transition); every pixel with mask 0 is byte-identical to the input.
# Shapes are drawn at the painting face's real aspect, then squeezed into the square UV box (as the face displays it).
# usage: python art05_candidate.py <input_dir> <out_dir>
import sys,json,hashlib,numpy as np
from PIL import Image,ImageDraw,ImageFilter
I,O=sys.argv[1],sys.argv[2]
A=np.array(Image.open(f'{I}/PaintingAtlas_FUR06.png').convert('RGB'))
tm=json.load(open(f'{I}/target_mapping.json'))
BG=np.array([232,236,223]); OLDFG=np.array([173,175,165]); BORDER=np.array([211,218,204])
ASPECT={'Frame_17':1.5621,'Frame_18':1.4567,'Frame_19':1.5314}     # painting face width/height from the supplied FBX (slot 1)
G_MAIN=(176,178,168); G_DEEP=(166,168,158)   # F18 left end only slightly darker (observed); no inner cores (they read as holes/eyes)
def E(cx,cy,rx,ry): return (cx,cy,rx,ry)
SHAPES={  # normalised face coords (x right, y down), ellipses; (tone, list)
 'Frame_17':[(G_MAIN,[E(0.50,0.76,0.36,0.075),E(0.20,0.66,0.075,0.10),E(0.34,0.63,0.08,0.125),E(0.49,0.66,0.075,0.10),E(0.63,0.62,0.085,0.13),E(0.78,0.67,0.075,0.095)]),
             ],
 'Frame_18':[(G_MAIN,[E(0.50,0.66,0.37,0.10),E(0.22,0.54,0.09,0.12),E(0.38,0.51,0.085,0.13),E(0.55,0.53,0.09,0.12),E(0.72,0.55,0.085,0.11)]),
             (G_DEEP,[E(0.19,0.61,0.07,0.09)])],
 'Frame_19':[(G_MAIN,[E(0.40,0.36,0.12,0.17),E(0.55,0.31,0.11,0.16),E(0.50,0.48,0.14,0.13)]),
             ]}
SS=4; out=A.copy(); mask=np.zeros(A.shape[:2],np.uint8); log={}
for t in tm['targets']:
    fid=t['id']; x0,y0,x1,y1=t['paintCell']['drawingCellPixelsXYXYExclusive']; bx0,by0,bx1,by1=t['paintCell']['sampledPixelBoundsTopLeft']
    cell=A[y0:y1,x0:x1].astype(float)
    oldfg=(A[y0:y1,x0:x1]==OLDFG).all(2)
    # draw at face aspect, H = box height
    H=int(round((by1-by0)*SS)); W=int(round(H*ASPECT[fid]))
    alpha=np.zeros((H,W)); color=np.ones((H,W,3))*np.array(G_MAIN)   # colour field starts at the main grey (no dark fringe)
    for tone,els in SHAPES[fid]:
        im=Image.new('L',(W,H),0); d=ImageDraw.Draw(im)
        for cx,cy,rx,ry in els: d.ellipse([(cx-rx)*W,(cy-ry)*H,(cx+rx)*W,(cy+ry)*H],fill=255)
        if tone==G_MAIN: im=im.filter(ImageFilter.MaxFilter(4*SS+1)).filter(ImageFilter.MinFilter(4*SS+1))   # close tiny gaps where ellipses meet
        a=np.array(im.filter(ImageFilter.GaussianBlur(SS*(1.4 if tone==G_MAIN else 4.0))),float)/255
        if tone==G_MAIN: alpha=np.maximum(alpha,a)
        else: color=color*(1-a[...,None])+np.array(tone)*a[...,None]
    # squeeze to the UV box (box is square in pixels), then place into the cell
    bw,bh=int(round(bx1-bx0)),int(round(by1-by0))
    a_box=np.array(Image.fromarray((alpha*255).astype(np.uint8)).resize((bw,bh),Image.BILINEAR),float)/255
    c_box=np.stack([np.array(Image.fromarray(np.clip(color[...,k],0,255).astype(np.uint8)).resize((bw,bh),Image.BILINEAR),float) for k in range(3)],-1)
    ox,oy=int(round(bx0))-x0,int(round(by0))-y0
    A2=np.zeros(cell.shape[:2]); C2=np.zeros(cell.shape)
    A2[oy:oy+bh,ox:ox+bw]=a_box; C2[oy:oy+bh,ox:ox+bw]=c_box
    A2[A2<1.5/255]=0
    base=cell.copy(); base[oldfg]=BG                                  # erase old foreground with the unchanged background colour
    border=(A[y0:y1,x0:x1]==BORDER).all(2); assert not (border&(A2>0)).any(), f'{fid}: new shape touches the drawing border'
    newc=base*(1-A2[...,None])+C2*A2[...,None]
    m=oldfg|(A2>0)
    res=np.where(m[...,None],np.clip(np.round(newc),0,255),cell).astype(np.uint8)
    out[y0:y1,x0:x1]=res; mask[y0:y1,x0:x1]=np.where(m,255,0)
    ch=(res!=A[y0:y1,x0:x1]).any(2); ys,xs=np.where(ch); mys,mxs=np.where(m)
    log[fid]={'tile':t['paintCell']['tile'],'cell_xyxy_excl':[x0,y0,x1,y1],'mask_pixels':int(m.sum()),'changed_pixels':int(ch.sum()),
              'old_fg_pixels':int(oldfg.sum()),'new_fg_pixels_alpha_gt0':int((A2>0).sum()),
              'changed_bbox_atlas_xyxy_incl':[int(xs.min()+x0),int(ys.min()+y0),int(xs.max()+x0),int(ys.max()+y0)],'mask_bbox_atlas_xyxy_incl':[int(mxs.min()+x0),int(mys.min()+y0),int(mxs.max()+x0),int(mys.max()+y0)],
              'mask_fraction_of_cell':round(float(m.mean()),4),'border_pixels_unchanged':bool((res[border]==A[y0:y1,x0:x1][border]).all())}
Image.fromarray(out,'RGB').save(f'{O}/PaintingAtlas_FUR06_ART05_candidate.png',optimize=True)
Image.fromarray(mask,'L').save(f'{O}/PaintingAtlas_FUR06_ART05_shape_change_mask.png',optimize=True)
json.dump({'per_cell':log,'aspect':ASPECT,'tones':{'main':G_MAIN,'deep':G_DEEP},'background_colour_used_for_erase':BG.tolist()},open(f'{O}/qa/build_log.json','w'),indent=1)
print(json.dumps(log,indent=0))
