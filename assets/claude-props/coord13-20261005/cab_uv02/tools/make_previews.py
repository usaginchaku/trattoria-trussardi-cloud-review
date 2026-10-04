# self-made UV2 diagrams from native_mesh.json coordinates only (no textures / original pixels).
# 1) uv2_before_added.png : fixed UV2 (gray) + added 188 triangles (red) as delivered -> coincident duplicates
# 2) uv2_free_vs_bigchart.png : free space of fixed UV2 at margin 0.00390625 (white=free) + to-scale footprints of the
#    largest added chart at scale 1.0 (red) and 0.70 (orange), drawn in a strip below the unit square (not a placement)
# usage: python make_previews.py native_mesh.json out_dir
import sys,json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
mj,od=sys.argv[1:3]; m=json.load(open(mj))
uv=np.array(m['attributes']['uv2'],dtype=np.float32).astype(np.float64); T=np.array(m['submeshes'][0]['triangles'],dtype=np.int64).reshape(-1,3)
N=1024; pad=16
def xy(p,H): return [(pad+x*N, pad+(1-y)*N) for x,y in p]   # v up
im=Image.new('RGB',(N+2*pad,N+2*pad),(20,20,24)); d=ImageDraw.Draw(im,'RGBA')
d.rectangle([pad,pad,pad+N,pad+N],outline=(90,90,100))
for t in T[:4220]: d.polygon(xy(uv[t],N),fill=(150,150,150,255))
for t in T[4220:]: d.polygon(xy(uv[t],N),fill=(230,40,40,160),outline=(255,60,60,255))
im.save(od+'/uv2_before_added.png')
G=2048; occ=Image.new('L',(G,G),0); g=ImageDraw.Draw(occ)
for t in T[:4220]: g.polygon([(x*G,(1-y)*G) for x,y in uv[t]],fill=1,outline=1)
o=np.array(occ,bool); blocked=distance_transform_edt(~o)<=0.00390625*G
free=(~blocked).astype(np.uint8)*255
fim=Image.fromarray(free).resize((N,N),Image.NEAREST).convert('RGB')
strip=140; im2=Image.new('RGB',(N+2*pad,N+2*pad+strip),(20,20,24)); im2.paste(fim,(pad,pad)); d2=ImageDraw.Draw(im2)
d2.rectangle([pad,pad,pad+N,pad+N],outline=(90,90,100))
w,h=0.21456995,0.06794
y0=pad+N+20
d2.rectangle([pad,y0,pad+w*N,y0+h*N],outline=(255,60,60),width=2)
d2.rectangle([pad+w*N+40,y0,pad+w*N+40+0.7*w*N,y0+0.7*h*N],outline=(255,160,40),width=2)
im2.save(od+'/uv2_free_vs_bigchart.png')
