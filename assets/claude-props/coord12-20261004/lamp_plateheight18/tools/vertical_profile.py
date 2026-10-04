# vertical profile (numbers only) of the dark metal silhouette under each short-arm lamp cup in the private attachments (scratch only):
# per row: widest dark run (mean RGB < 95) width, start, end, centre; plus cup outer extents (mean RGB < 150) and the last row containing
# cream shade pixels. Also the model's front-ortho silhouette widths per z from geometry (LAMP15 PLATE_C1), in Ws units.
# usage: blender-python vertical_profile.py -- att1.jpg att2.jpg model.blend out.json
import sys,json
import numpy as np
from PIL import Image
a1,a2,bl,out=sys.argv[sys.argv.index('--')+1:]
A=np.asarray(Image.open(a1).convert('RGB')).astype(int); B=np.asarray(Image.open(a2).convert('RGB')).astype(int)
def runw(row,thr):
    xs=np.where(row<thr)[0]
    if not len(xs): return None
    g=np.split(xs,np.where(np.diff(xs)>1)[0]+1); w=max(g,key=len); return [int(w[0]),int(w[-1]),len(w)]
res={'lamps':{}}
for name,im,(x0,x1,y0,y1) in [('IMG_3594_left',A,(708,790,305,425)),('IMG_3594_right',A,(1270,1365,305,425)),('IMG_3675',B,(365,465,355,480))]:
    reg=im[y0:y1,x0:x1]; lum=reg.mean(2)
    cream=(reg[:,:,0]>150)&(reg[:,:,1]>150)&(reg[:,:,2]<reg[:,:,0]-5)
    cup=[runw(lum[r],150) for r in range(y1-y0)]; cw=max((c[2] for c in cup if c),default=0); ci=[c for c in cup if c and c[2]==cw][0]
    rows=[]
    for r in range(y1-y0):
        d=runw(lum[r],95)
        if d: rows.append({'y':r+y0,'x0':d[0]+x0,'x1':d[1]+x0,'w':d[2],'cx':(d[0]+d[1])/2+x0,'cream_px':int(cream[r].sum())})
    res['lamps'][name]={'cup_outer_w_px':cw,'cup_centre_x':(ci[0]+ci[1])/2+x0,'rows':rows}
# model front silhouette (geometry)
import bpy
bpy.ops.wm.open_mainfile(filepath=bl); co=np.array([v.co[:] for v in bpy.data.objects['StraightLamp'].data.vertices])
pl=co[0:96]; col=co[96:218]; Ws=0.222; prof=[]
for z in np.arange(0.20,0.0,-0.005):
    ws=[]
    for nm,p in (('plate',pl),('collar',col),('arm',co[1070:1406])):
        m=np.abs(p[:,2]-z)<0.003
        if m.any(): ws.append((nm,float(p[m,0].max()-p[m,0].min())))
    if ws: prof.append({'z':round(float(z),3),'parts':ws,'union_w_over_Ws':round(max(w for _,w in ws)/Ws,3)})
res['model_front_silhouette']={'collar_z':[float(col[:,2].min()),float(col[:,2].max())],'plate_z':[float(pl[:,2].min()),float(pl[:,2].max())],'profile':prof}
json.dump(res,open(out,'w'),indent=1)
for k,v in res['lamps'].items():
    print(k,'cup',v['cup_outer_w_px'],'cx',v['cup_centre_x']); print('  ',[(r['y'],r['w'],round(r['cx'],1),r['cream_px']) for r in v['rows'] if r['w']>2][:40])
