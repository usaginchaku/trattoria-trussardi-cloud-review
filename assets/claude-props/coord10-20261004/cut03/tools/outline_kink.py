# outline kink metric (geometry, not shading): per cross-section station (unique y of ring vertices) take the cutting-edge outline
# point (max x) and the spine (min x); turning angle between consecutive outline segments in the XY plane. A1 vs A2.
import bpy,sys,json,numpy as np
out={}
for tag,p in zip(sys.argv[sys.argv.index('--')+1:-1:2],sys.argv[sys.argv.index('--')+2:-1:2]):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p)
    me=[o for o in bpy.data.objects if o.type=='MESH'][0].data; co=np.array([v.co[:] for v in me.vertices])
    ys=np.unique(np.round(co[:,1],6)); E=[];
    for y in ys:
        m=np.abs(co[:,1]-y)<5e-7
        if m.sum()<3: continue
        E.append((y,co[m,0].max(),co[m,0].min()))
    E=np.array(E); r={}
    for name,col in (('edge',1),('spine',2)):
        P=E[:,[col,0]]; seg=np.diff(P,axis=0); seg=seg[np.linalg.norm(seg,axis=1)>1e-9]
        a=np.degrees(np.arctan2(seg[:,1],seg[:,0])); turn=np.abs((np.diff(a)+180)%360-180)
        bl=(E[1:-1,0]>0.0)&(E[1:-1,0]<0.105)            # blade body, excluding the rounded tip arc and handle
        tb=turn[:len(bl)][bl[:len(turn)]] if len(turn) else turn
        ymid=E[1:-1,0]; r[name+'_turn_by_y']=[[round(float(y),4),round(float(t),2)] for y,t in zip(ymid,turn) if 0.0<y<0.105]
        tb2=np.array([t for y,t in zip(ymid,turn) if 0.022<y<0.105])
        r[name+'_blade_body_0.022_0.105_max_turn_deg']=float(tb2.max()) if len(tb2) else None
        r[name]={'stations':int(len(E)),'max_turn_deg_blade':float(tb.max()) if len(tb) else None,'mean_turn_deg_blade':float(tb.mean()) if len(tb) else None,'blade_stations_0_to_0.105':int(bl.sum())}
    out[tag]=r; print('K',tag,json.dumps(r))
json.dump(out,open(sys.argv[-1],'w'),indent=1)
