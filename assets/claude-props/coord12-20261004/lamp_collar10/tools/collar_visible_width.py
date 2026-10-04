# F3 check (read-only on the input blend): geometric collar radii, the radius at which the collar surface enters the shade (visible part),
# and the visible dark-collar width measured on model-only renders (input renders from lamp_curved07/revision02/previews and two
# diagnostic renders made here: front ortho as-is and front ortho with the shade hidden). Ws = shade max width.
# usage: blender-python collar_visible_width.py -- input.blend previews_dir out_dir out.json
import bpy,sys,json,os,math
import numpy as np
bl,pdir,odir,out=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=bl); o=bpy.data.objects['CurvedLamp']; me=o.data
co=np.array([v.co[:] for v in me.vertices]); col=co[588:710]; sh=co[710:1416]; cy=(col[:,1].min()+col[:,1].max())/2
rad=lambda p:np.hypot(p[:,0],p[:,1]-cy); Ws=float(2*rad(sh).max())
rings=[(float(z),float(rad(col[np.abs(col[:,2]-z)<1e-5]).max())) for z in sorted(set(col[:,2].round(5)))]
shz=float(sh[:,2].min()); shr=float(rad(sh[np.abs(sh[:,2]-shz)<1e-4]).max())
# collar radius at the shade bottom height (linear between rings)
zs=[r[0] for r in rings]; rs=[r[1] for r in rings]; r_at=float(np.interp(shz,zs,rs))
geo={'Ws_m':Ws,'collar_rings_z_r':rings,'collar_top_diameter_m':2*rings[-1][1],'collar_top_diameter/Ws':2*rings[-1][1]/Ws,
     'shade_bottom_z':shz,'shade_bottom_disk_radius_m':shr,'collar_radius_at_shade_bottom_m':r_at,'visible_collar_max_diameter/Ws':2*r_at/Ws,
     'note':'the collar flares to r 0.053 only above the shade bottom (z > shade_bottom_z), i.e. inside the shade bowl; that part is hidden'}
# diagnostic renders (model only): same camera as lamp_curved07 front view
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=32; s.cycles.use_denoising=True; s.view_settings.view_transform='Standard'
from mathutils import Vector,Matrix
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.85,0.85,0.82,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.6
L=bpy.data.lights.new('key','SUN'); L.energy=2.5; L.angle=0.3; lo=bpy.data.objects.new('key',L); s.collection.objects.link(lo); lo.rotation_euler=(math.radians(55),0,math.radians(-30))
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera=cam
C=Vector((0,-0.19,0.2)); loc=C+Vector((0,-2,0)); f=(C-loc).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
cam.data.type='ORTHO'; cam.data.ortho_scale=0.62; cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
s.render.resolution_x=s.render.resolution_y=700
s.render.filepath=os.path.join(odir,'diag_front_as_is.png'); bpy.ops.render.render(write_still=True)
# hide shade + diffuser: delete their faces in a copy of the mesh
import bmesh
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.verts[i] for i in range(710,1562)],context='VERTS'); m2=bpy.data.meshes.new('noshade'); bm.to_mesh(m2)
for mm in me.materials: m2.materials.append(mm)
o.data=m2; s.render.filepath=os.path.join(odir,'diag_front_shade_hidden.png'); bpy.ops.render.render(write_still=True)
from PIL import Image
def measure(path,ws_px=None):
    a=np.asarray(Image.open(path).convert('RGB')).astype(int); lum=a.mean(2); dark=lum<110
    cream=(a[:,:,1]>150)&(a[:,:,2]<a[:,:,1]-25)
    if ws_px is None:
        rows=np.where(cream.any(1))[0]; ws_px=max(np.where(cream[r])[0].ptp()+1 for r in rows)
    res=[]
    for rr in range(a.shape[0]):
        xs=np.where(dark[rr])[0]
        if len(xs):
            runs=np.split(xs,np.where(np.diff(xs)>1)[0]+1); res.append((rr,max(len(x) for x in runs)))
    return ws_px,res
px_per_m=700/0.62
ws1,r1=measure(os.path.join(odir,'diag_front_as_is.png')); ws2,r2=measure(os.path.join(odir,'diag_front_shade_hidden.png'),ws_px=round(Ws*px_per_m))
z_of_row=lambda rr:0.2+(350-rr)/px_per_m
def summarize(rr,ws):
    sel=[(z_of_row(a),b) for a,b in rr if 0.125<z_of_row(a)<0.18]
    return {'Ws_px':int(ws),'rows':[(round(z,4),b,round(b/ws,3)) for z,b in sel][::3],'max_ratio':round(max(b for z,b in sel)/ws,3) if sel else None}
rend={'front_as_is':summarize(r1,ws1),'front_shade_hidden':summarize(r2,ws2)}
for nm in ('curved_F1C1r2_front.png','curved_F1C1r2_ref_like_jamb.png'):
    ws,rr=measure(os.path.join(pdir,nm)); rend['input_preview:'+nm]={'Ws_px':int(ws),'dark_run_ratios_top_rows':[round(b/ws,3) for a,b in rr if b<0.6*ws][:0] }
json.dump({'geometry':geo,'renders':rend},open(out,'w'),indent=1)
print(json.dumps(geo,indent=0)); print(rend['front_as_is']['max_ratio'],rend['front_shade_hidden']['max_ratio'])
