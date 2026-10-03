# COORD10-CUT03 A2 (knife only; derived from CUT02 A1 build_cut02.py — outline, tip, widths, thickness, axes unchanged):
# blade/bolster stations are redistributed by the curvature of the cutting-edge curve (more where it bends), tip arc 6 -> 8 stations.
# UV0 for the new knife adds z to the u projection so the thin side walls / caps get non-zero UV area (still inside the uniform silver patch).
# CUT02 A1: new fork / spoon / knife meshes (self-authored parametric geometry, no reference pixels).
# Axes/units as the v02 sources: metres, long axis +Y (head/bowl/blade at +Y), up +Z, lying on z=0, object at origin,
# total length (Y extent) and Y end positions kept per item. Material slot = the source material (Trussardi_Atlas, same images).
# UVMap: planar top projection squeezed into the uniform silver patch the sources already use; LightmapUV: new non-overlapping unwrap.
# args: -- src_dir outdir
import bpy,bmesh,os,sys,json,math,numpy as np
from mathutils import Vector
SRC,OUT,NBLADE,NTIP=sys.argv[sys.argv.index('--')+1:]; NBLADE=int(NBLADE); NTIP=int(NTIP)
def smooth(t): t=min(1,max(0,t)); return t*t*(3-2*t)
def interp(y,pts):
    ys=[p[0] for p in pts]; zs=[p[1] for p in pts]; return float(np.interp(y,ys,zs))
# ---------------- generic loft (closed rings) ----------------
def loft(bm,rings,cap_start=True,cap_end=True,y0=None,y1=None):
    vs=[[bm.verts.new(p) for p in ring] for ring in rings]; n=len(rings[0])
    for a,b in zip(vs[:-1],vs[1:]):
        for i in range(n): bm.faces.new((a[i],a[(i+1)%n],b[(i+1)%n],b[i]))
    for ring,flip in ((vs[0],True),(vs[-1],False)):
        if (flip and not cap_start) or (not flip and not cap_end): continue
        c=bm.verts.new(sum((v.co for v in ring),Vector())/n)
        if flip and y0 is not None: c.co.y=y0
        if (not flip) and y1 is not None: c.co.y=y1
        for i in range(n):
            f=(ring[(i+1)%n],ring[i],c) if flip else (ring[i],ring[(i+1)%n],c); bm.faces.new(f)
    return vs
def ring(y,x0,w,ztop,zbot,K):
    # ztop(s), zbot(s) for s in [-1,1]; top left->right, bottom right->left
    S=np.linspace(-1,1,K); top=[(x0+s*w/2,y,ztop(s)) for s in S]; bot=[(x0+s*w/2,y,zbot(s)) for s in S[::-1]]
    return top+bot
# ---------------- SPOON ----------------
def spoon():
    Y0,Y1=-0.102,0.110; yc,a,b=0.0745,0.019,0.0355; depth,Tb=0.0062,0.0013
    def neck_w(y): return 2*interp(y,[(Y0,0.0058),(Y0+0.012,0.0062),(-0.06,0.0060),(0.0,0.0047),(0.028,0.0034),(0.045,0.0034)])
    def endcap(y):  # rounded handle end (semicircle radius r)
        r=0.0062; d=y-Y0; return 1.0 if d>=r else math.sqrt(max(0,1-((r-d)/r)**2))
    def ell(y): return math.sqrt(max(0,1-((y-yc)/b)**2))
    def width(y):
        we=2*a*ell(y); wn=neck_w(y)*endcap(y) if y<0.06 else 0
        return (we**4+wn**4)**0.25
    def c_handle(y): return interp(y,[(Y0,0.00125),(-0.06,0.0028),(-0.01,0.0058),(0.025,0.0086),(0.040,0.0084)])
    Tn=lambda y: interp(y,[(Y0,0.0025),(0.0,0.0027),(0.03,0.0030),(0.042,0.0022),(0.05,Tb)])
    ys=list(np.linspace(Y0+0.0004,Y0+0.0062,4))+list(np.linspace(Y0+0.009,0.020,14))+list(np.linspace(0.024,0.044,7))+list(np.linspace(0.047,0.100,16))+list(np.linspace(0.102,Y1-0.0004,5))
    rings=[]
    for y in ys:
        e=ell(y); D=depth*e**2; w=max(width(y),0.0008)
        bowlw=smooth((y-0.036)/0.012)               # 0 handle -> 1 bowl
        Hb=depth+Tb                                   # bowl rim height (bowl back touches z=0 at yc)
        top_c=(1-bowlw)*(c_handle(y)+Tn(y)/2)+bowlw*Hb
        T=(1-bowlw)*Tn(y)+bowlw*Tb
        crown=0.00045*(1-bowlw)
        zt=lambda s,top_c=top_c,D=D,crown=crown: top_c-D*(1-s*s)+crown*(1-s*s)
        zb=lambda s,zt=zt,T=T: zt(s)-T
        rings.append(ring(y,0.0,w,zt,zb,9))
    return rings,'08_Dinner_Spoon',Y0,Y1
# ---------------- KNIFE ----------------
def knife():
    Y0,Y1=-0.1125,0.12376
    # outline: spine (x min side) and edge (x max side) as functions of y
    def spine(y): return interp(y,[(Y0,-0.0058),(-0.03,-0.0063),(0.000,-0.0045),(0.008,-0.0040),(0.016,-0.0062),(Y1,-0.0062)])
    from scipy.interpolate import PchipInterpolator
    _blade=PchipInterpolator([0.008,0.018,0.040,0.075,0.098,0.110,Y1],[0.0040,0.0100,0.0138,0.0140,0.0124,0.0098,0.0080])   # smooth cutting-edge curve
    def edge(y):  return float(_blade(y)) if y>=0.008 else interp(y,[(Y0,0.0058),(-0.03,0.0063),(0.000,0.0045),(0.008,0.0040)])
    R=(edge(Y1)-spine(Y1))/2; yr=Y1-R                                     # rounded tip: semicircle of the tip width
    def endcap(y): r=0.006; d=y-Y0; return 1.0 if d>=r else math.sqrt(max(0,1-((r-d)/r)**2))
    def tipcap(y): return 1.0 if y<=yr else math.sqrt(max(0,1-((y-yr)/R)**2))
    # curvature-weighted stations on [0, yr]: density ~ 1 + K*|x''(y)| of the cutting edge (A1 had 6 + 12 uniform stations there)
    gy=np.linspace(0.0,yr,2000); ge=np.array([edge(y) for y in gy]); curv=np.abs(np.gradient(np.gradient(ge,gy),gy))
    dens=1+np.minimum(curv/np.percentile(curv,90),2.0)   # capped so the intended neck/blade corner at y=0.008 does not attract clustered rings
    cdf=np.concatenate([[0],np.cumsum((dens[1:]+dens[:-1])/2*np.diff(gy))]); cdf/=cdf[-1]
    blade_ys=list(np.interp(np.linspace(0,1,NBLADE),cdf,gy))
    ys=list(np.linspace(Y0+0.0004,Y0+0.006,4))+list(np.linspace(Y0+0.010,-0.004,10))+blade_ys+list(yr+R*np.sin(np.linspace(0.18,1.50,NTIP)))
    rings=[]
    for y in ys:
        sp,ed=spine(y),edge(y); k=endcap(y)*tipcap(y); mid=(sp+ed)/2; w=max((ed-sp)*k,0.0008)
        blade=smooth((y-0.004)/0.012)
        Th=interp(y,[(Y0,0.0040),(-0.05,0.0044),(0.0,0.0042),(0.006,0.0034)])   # handle thickness
        Tsp=0.0019; Ted=0.0005
        def zt(s,Th=Th,blade=blade):
            hand=Th*(0.5+0.5*(1-s*s)**0.5)                                      # rounded handle top
            bl=Tsp*(1-s)/2+Ted*(1+s)/2                                        # wedge: thick spine (s=-1) -> thin edge (s=+1)
            return (1-blade)*hand+blade*bl
        zb=lambda s: 0.0
        rings.append(ring(y,mid,w,zt,zb,6))
    return rings,'09_Dinner_Knife',Y0,Y1
# ---------------- FORK (grid top surface + extrude; tines with V slot bottoms) ----------------
def fork(bm):
    Y0,Y1=-0.1025,0.10306; yroot=0.067; HW=0.0125; tw0,tw1,gap=0.0040,0.0026,0.003
    centers=[-0.0105,-0.0035,0.0035,0.0105]
    def hw(y):
        if y>=0.060: return HW
        if y>=0.036: return 0.0036+(HW-0.0036)*smooth((y-0.036)/0.024)
        return interp(y,[(Y0,0.0056),(Y0+0.0056,0.0058),(-0.07,0.0057),(-0.02,0.0047),(0.036,0.0036)])
    def endcap(y): r=0.0056; d=y-Y0; return 1.0 if d>=r else math.sqrt(max(0,1-((r-d)/r)**2))
    cols=[]
    for c in centers: cols+= [c-tw0/2,c+tw0/2]
    cols=sorted(cols); gaps=[(cols[1]+cols[2])/2,(cols[3]+cols[4])/2,(cols[5]+cols[6])/2]
    allcols=sorted(cols+gaps); frac=[x/HW for x in allcols]               # 11 columns
    ys=list(np.linspace(Y0+0.0005,Y0+0.0056,4))+list(np.linspace(Y0+0.010,0.030,10))+list(np.linspace(0.034,0.064,9))+[yroot]
    rows=[]
    for y in ys:
        h=hw(y)*endcap(y); h=max(h,0.0006); rows.append([bm.verts.new((f*h,y,0.0)) for f in frac])
    # V slot bottoms: gap-mid points on the root row lowered
    for gi,gx in enumerate(gaps):
        j=allcols.index(gx); rows[-1][j].co.y=yroot-0.0013
    faces=[]
    for a,b in zip(rows[:-1],rows[1:]):
        for i in range(len(frac)-1): faces.append(bm.faces.new((a[i],a[i+1],b[i+1],b[i])))
    # end cap fan (handle end)
    c0=bm.verts.new((0,Y0,0.0)); r0=rows[0]
    for i in range(len(frac)-1): faces.append(bm.faces.new((r0[i+1],r0[i],c0)))
    # tines
    root=rows[-1]
    tys=list(np.linspace(yroot,Y1-0.0013,7))[1:]
    for ti,c in enumerate(centers):
        L=root[allcols.index(c-tw0/2)]; R=root[allcols.index(c+tw0/2)]; prev=(L,R)
        for y in tys:
            t=(y-yroot)/(Y1-yroot); w=tw0+(tw1-tw0)*t; cx=c*(1-0.06*t)      # slight inward convergence
            nl=bm.verts.new((cx-w/2,y,0)); nr=bm.verts.new((cx+w/2,y,0)); faces.append(bm.faces.new((prev[0],prev[1],nr,nl))); prev=(nl,nr)
        tipc=bm.verts.new(((prev[0].co.x+prev[1].co.x)/2,Y1,0)); faces.append(bm.faces.new((prev[0],prev[1],tipc)))
    return faces
def fork_z(y,x):
    c=interp(y,[(-0.1025,0.0),(-0.06,0.0011),(-0.01,0.0042),(0.03,0.0080),(0.055,0.0090),(0.08,0.0072),(0.10306,0.0040)])
    t=interp(y,[(-0.1025,0.0023),(-0.03,0.0024),(0.02,0.0026),(0.04,0.0024),(0.055,0.0018),(0.067,0.0016),(0.10306,0.0014)])
    cup=0.0011*(x/0.0125)**2*smooth((y-0.045)/0.02)                      # head slightly spoon-like across its width
    return c+cup,t
# ---------------- build ----------------
def finish(name,bm,src_fbx):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=src_fbx)
    so=[o for o in bpy.data.objects if o.type=='MESH'][0]; mat=so.data.materials[0]; sname=so.name; smesh=so.data.name
    sco=np.array([v.co[:] for v in so.data.vertices]); sinfo={'object':sname,'mesh':smesh,'material':mat.name,'uv_layers':[u.name for u in so.data.uv_layers],'bbox':[sco.min(0).tolist(),sco.max(0).tolist()],'tris':len(so.data.polygons)}
    me=bpy.data.meshes.new(smesh+'_CUT02'); bm.to_mesh(me); bm.free()
    # ground exactly at z=0
    co=np.array([v.co[:] for v in me.vertices]); dz=co[:,2].min()
    for v in me.vertices: v.co.z-=dz
    o=bpy.data.objects.new(sname,me); bpy.context.collection.objects.link(o)
    bpy.data.objects.remove(so); me.materials.append(mat)
    for p in me.polygons: p.use_smooth=True
    me.set_sharp_from_angle(angle=math.radians(48))
    # UVMap: planar top projection into the silver patch (u 0.140-0.185, v 0.140-0.235; inside the sources' range)
    co=np.array([v.co[:] for v in me.vertices]); mn,mx=co.min(0),co.max(0)
    uv=me.uv_layers.new(name='UVMap')
    for l in me.loops:
        x,y,_=me.vertices[l.vertex_index].co
        z=me.vertices[l.vertex_index].co.z
        uv.data[l.index].uv=(0.140+0.045*((x-mn[0])+(z-mn[2]))/((mx[0]-mn[0])+(mx[2]-mn[2])),0.140+0.095*(y-mn[1])/(mx[1]-mn[1]))
    lm=me.uv_layers.new(name='LightmapUV'); me.uv_layers.active=lm
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(50),island_margin=0.02,area_weight=0.0,scale_to_bounds=False)
    bpy.ops.uv.pack_islands(margin=0.01,rotate=True)
    bpy.ops.object.mode_set(mode='OBJECT'); me.uv_layers.active=me.uv_layers['UVMap']; me.uv_layers['UVMap'].active_render=True
    return o,me,sinfo
def run():
    os.makedirs(f'{OUT}/fbx',exist_ok=True); os.makedirs(f'{OUT}/models',exist_ok=True); report={}
    for kind in ('knife',):
        bm=bmesh.new()
        if kind=='fork':
            fork(bm); name='07_Dinner_Fork'
            ext=bmesh.ops.extrude_face_region(bm,geom=list(bm.faces)); newv=[e for e in ext['geom'] if isinstance(e,bmesh.types.BMVert)]
            topset=set(newv)
            for v in bm.verts:
                c,t=fork_z(v.co.y,v.co.x); v.co.z=c+(t if v in topset else 0.0)
            bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        else:
            rings,name,ya,yb=spoon() if kind=='spoon' else knife()
            loft(bm,rings,y0=ya,y1=yb); bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>3],quad_method='BEAUTY',ngon_method='BEAUTY')
        o,me,sinfo=finish(name,bm,f'{SRC}/{name}.fbx')
        co=np.array([v.co[:] for v in me.vertices])
        report[name]={'source':sinfo,'candidate':{'verts':len(me.vertices),'tris':len(me.polygons),'bbox':[co.min(0).round(5).tolist(),co.max(0).round(5).tolist()],'uv_layers':[u.name for u in me.uv_layers],'material':me.materials[0].name}}
        o.select_set(True); bpy.context.view_layer.objects.active=o
        bpy.ops.export_scene.fbx(filepath=f'{OUT}/fbx/{name}.fbx',use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',bake_space_transform=False,mesh_smooth_type='FACE',add_leaf_bones=False,path_mode='STRIP')
        for im in bpy.data.images:
            if im.filepath: b=os.path.basename(im.filepath.replace('\\','/')); im.filepath_raw='x'*1000; im.filepath_raw='//../fbx/'+b
        for sc in bpy.data.scenes: sc.render.filepath='x'*1000; sc.render.filepath='//render/'
        bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/models/{name}.blend',compress=True,relative_remap=False)
        print('R',name,json.dumps(report[name]))
    json.dump(report,open(f'{OUT}/build_report.json','w'),indent=1)
run()
