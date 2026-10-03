# COORD09 W2 (material factor only, candidate-only texture copy):
#  - new image Trussardi_Atlas_BaseColor_C09W.png = v02 BaseColor + checker basket-weave patch in the unused band v 0.75..0.875
#  - new material Trussardi_Atlas_C09W (copy; only BaseColor image differs) assigned to the basket candidate only
#  - UVMap of basket side faces (slat rings, posts, core sides) re-projected into the patch; rim, floor, soil top, foliage, LightmapUV, geometry unchanged
import bpy,bmesh,sys,json,math,numpy as np
from PIL import Image
src,tag,outpng=sys.argv[sys.argv.index('--')+1:]
V0,V1,U0,US=0.75,0.875,0.04,0.90; NCOL=64; NROW=5; PADPX=5
# --- texture
base=Image.open('<home>/dot_v02_src/assets/dot-props/v02/textures/Trussardi_Atlas_BaseColor.png').convert('RGBA'); W,H=base.size
a=np.asarray(base).copy()
tan=np.array([183,161,87]); dark=np.array([92,74,34]); gap=np.array([58,45,20])
y0,y1=int(round(H*(1-V1)))-PADPX,int(round(H*(1-V0)))+PADPX  # pad so bilinear/mip sampling at patch edges never reaches transparent texels
for py in range(y0,y1):
    fv=(H-py-0.5)/H; tv=(fv-V0)/(V1-V0); row=tv*NROW; ri=int(math.floor(row)); fr=row-ri
    for px in range(W):
        tu=((px+0.5)/W-U0)/US; col=tu*NCOL; ci=int(math.floor(col)); fc=col-ci
        horiz=(ri+ci)%2==0
        f=fr if horiz else fc          # across-strand coordinate in cell 0..1
        s=(f*3)%1.0                    # 3 strands per cell
        if min(fr,1-fr)<0.06 or min(fc,1-fc)<0.06: c=gap
        elif s<0.14 or s>0.86: c=dark
        else:
            k=1-0.25*abs(s-0.5)*2; c=tan*k+dark*(1-k)*0.3
        a[py,px,:3]=np.clip(c,0,255); a[py,px,3]=255
Image.fromarray(a.astype(np.uint8)).save(outpng)
# roughness / metallic share UVMap: candidate copies with the same band filled by the basket slat's own value (sampled at v02 slat UV)
TXD='<home>/dot_v02_src/assets/dot-props/v02/textures/'; SL=(0.14795,0.33936); extra={}
for nm in ('Roughness','Metallic'):
    im=Image.open(TXD+f'Trussardi_Atlas_{nm}.png'); mode=im.mode; b=np.asarray(im).copy()
    val=b[int((1-SL[1])*H),int(SL[0]*W)].copy(); b[y0:y1]=val
    p=outpng.replace('BaseColor',nm); Image.fromarray(b,mode).save(p); extra[nm]=(p,val.tolist())
# --- mesh
bpy.ops.wm.open_mainfile(filepath=src)
o=bpy.data.objects['02_Flower_Basket_Mesh']; me=o.data
lm_before=[tuple(l.uv) for l in me.uv_layers['LightmapUV'].data]
uv0_before=[tuple(l.uv) for l in me.uv_layers['UVMap'].data]
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
uvl=bm.loops.layers.uv['UVMap']
seen=set(); isl=[]
for v in bm.verts:
    if v.index in seen: continue
    st=[v]; c=[]
    while st:
        x=st.pop()
        if x.index in seen: continue
        seen.add(x.index); c.append(x.index); st+=[e.other_vert(x) for e in x.link_edges]
    isl.append(c)
RIM=max(bm.verts[i].co.z for c in isl for i in c if min(bm.verts[j].co.z for j in c)<0.0625)
side_isl=[]
for c in isl:
    z=[bm.verts[i].co.z for i in c]
    if min(z)>=0.0625: continue                    # foliage
    if len(c) in (204,) and max(z)<0.008: continue  # floor
    if min(z)>0.050: continue                      # rim lip rings
    side_isl.append(c)
sv=set(i for c in side_isl for i in c)
faces=[f for f in bm.faces if f.verts[0].index in sv and abs(f.normal.z)<0.7]
# outline: superellipse through rim half extents, arc-length parameter
RX=max(abs(bm.verts[i].co.x) for i in sv); RY=max(abs(bm.verts[i].co.y) for i in sv)
th=np.linspace(-math.pi/2,1.5*math.pi,4001)  # start at back (y max -> angle pi/2); seam at back centre
n=6.0
def se(t): c,s=math.cos(t),math.sin(t); return RX*np.sign(c)*abs(c)**(2/n),RY*np.sign(s)*abs(s)**(2/n)
P=np.array([se(t) for t in th]); L=np.concatenate([[0],np.cumsum(np.linalg.norm(np.diff(P,axis=0),axis=1))]); L/=L[-1]
ang=np.arctan2(P[:,1]/RY,P[:,0]/RX)
def tparam(x,y):
    a=math.atan2(y/RY,x/RX); d=np.abs((ang-a+math.pi)%(2*math.pi)-math.pi); return float(L[d.argmin()])
# shift so seam is at back centre (y max): parameter 0 at angle +pi/2
t0=tparam(0,RY)
for f in faces:
    ts=[(tparam(l.vert.co.x,l.vert.co.y)-t0)%1.0 for l in f.loops]
    if max(ts)-min(ts)>0.5: ts=[t+1 if t<0.5 else t for t in ts]
    for l,t in zip(f.loops,ts):
        l[uvl].uv=(U0+US*t, V0+(V1-V0)*min(1,max(0,l.vert.co.z/RIM)))
bm.to_mesh(me); me.update()
# material copy
m0=me.materials[0]; m1=m0.copy(); m1.name='Trussardi_Atlas_C09W'
img=bpy.data.images.load(outpng); img.name='Trussardi_Atlas_BaseColor_C09W.png'
imr={nm:bpy.data.images.load(extra[nm][0]) for nm in extra}
for nm,i2 in imr.items(): i2.name=f'Trussardi_Atlas_{nm}_C09W.png'; i2.colorspace_settings.name='Non-Color'
for nd in m1.node_tree.nodes:
    if nd.type=='TEX_IMAGE' and nd.image:
        if 'BaseColor' in nd.image.name: nd.image=img
        for nm in imr:
            if nm in nd.image.name: nd.image=imr[nm]
me.materials[0]=m1
uv0_after=[tuple(l.uv) for l in me.uv_layers['UVMap'].data]
info={'tag':tag,'patch_v':[V0,V1],'patch_u':[U0,U0+US],'cells_around':NCOL,'rows':NROW,'pad_px':PADPX,'faces_remapped':len(faces),'side_islands':len(side_isl),
 'uv0_loops_changed':sum(1 for a_,b_ in zip(uv0_before,uv0_after) if a_!=b_),'lightmap_unchanged':lm_before==[tuple(l.uv) for l in me.uv_layers['LightmapUV'].data],
 'material':m1.name,'texture':img.name,'roughness_metallic_band_values':{k:v[1] for k,v in extra.items()},'tris':sum(len(p.vertices)-2 for p in me.polygons)}
bpy.ops.wm.save_as_mainfile(filepath=f'c9/basket_{tag}.blend',compress=False)
json.dump(info,open(f'c9/basket_{tag}.json','w'),indent=1); print(json.dumps(info))
