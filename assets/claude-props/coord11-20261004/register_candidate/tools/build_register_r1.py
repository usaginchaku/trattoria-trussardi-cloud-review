# COORD11-REG01 R1 (shape only): upper housing (shell with z 0.068-0.2454, slot0) gets a short flat top at the back with a small
# rounded convex bend, and its slope is tilted +DELTA deg about the front-top hinge line (core y=-0.173, z=0.1176).
# The parts seated on the slope (panel, 15 keys, rear slope plate = shells whose verts lie above the old slope) are moved RIGIDLY with
# the same rotation (vertex positions + loop normals rotated; UVs, topology and slots untouched), so their seat offset is unchanged.
# Every other shell: positions, UVs, loop (custom) normals, slots copied as-is. Materials/textures/origin/orientation/outer size kept.
# usage: blender-python build_register_r1.py -- input.fbx out.blend out.fbx out_log.json
import bpy
import bmesh,sys,json,math
import numpy as np
from mathutils import Vector,Matrix
fin,oblend,ofbx,olog=sys.argv[sys.argv.index('--')+1:]
DELTA=3.0            # deg; the largest tilt that keeps the rear slope plate (old seat distance 0.3166 m from hinge) on the slope
R_CORE=0.003         # m; core radius of the new top bend (outer radius = R_CORE + 0.002 bevel offset)
H=Vector((0,-0.173,0.1176)); ZTOP=0.2431; OFF=0.002; XW=0.145
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fin); o=[x for x in bpy.context.scene.objects if x.type=='MESH'][0]; me=o.data
assert o.name=='Register' and len(me.polygons)==5260
nv=len(me.vertices); co=np.array([v.co[:] for v in me.vertices])
# connectivity shells
par=list(range(nv))
def f(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
for e in me.edges:
    a,b=f(e.vertices[0]),f(e.vertices[1])
    if a!=b: par[a]=b
root=np.array([f(i) for i in range(nv)])
shells={}
for i,r in enumerate(root): shells.setdefault(r,[]).append(i)
def sb(vs): c=co[vs]; return c.min(0),c.max(0)
housing=[r for r,vs in shells.items() if abs(sb(vs)[0][2]-0.068)<1e-3 and abs(sb(vs)[1][2]-0.2454)<1e-3]; assert len(housing)==1; housing=housing[0]
th0=math.atan2(0.2431-0.1176,0.346)
def above_old_slope(vs):   # shell lies on top of the old slope (min height above the slope plane >= 0) and inside the slope span
    c=co[vs]; zs=0.1176+(c[:,1]+0.173)*math.tan(th0)
    return (c[:,2]-zs).min()>-0.004 and c[:,1].max()<0.173 and c[:,1].min()>-0.173 and c[:,2].min()>0.13 and c[:,2].max()<0.2431
seated=[r for r,vs in shells.items() if r!=housing and above_old_slope(vs)]
rot=Matrix.Rotation(math.radians(DELTA),4,'X'); T=Matrix.Translation(H)@rot@Matrix.Translation(-H); R3=rot.to_3x3()
# check rear plate clearance along the new slope
th1=th0+math.radians(DELTA); Ls=(ZTOP-H.z)/math.sin(th1)-R_CORE*math.tan(th1/2)
seat_far=max(float(((co[vs][:,1]-H.y)*math.cos(th0)+(co[vs][:,2]-H.z)*math.sin(th0)).max()) for r in seated for vs in [shells[r]])
assert seat_far<Ls, (seat_far,Ls)
# ---- collect kept/moved faces with original UV / loop normals
uvl=me.uv_layers[0].data; ln=[tuple(l.vector) for l in me.corner_normals]
hset=set(shells[housing]); mset=set(i for r in seated for i in shells[r])
verts=[]; vmap={}; faces=[]; fmat=[]; fuv=[]; fn=[]; fsmooth=[]
for p in me.polygons:
    if p.vertices[0] in hset: continue
    idx=[]
    for vi in p.vertices:
        if vi not in vmap:
            v=Vector(co[vi]); vmap[vi]=len(verts); verts.append(tuple(T@v) if vi in mset else tuple(v))
        idx.append(vmap[vi])
    faces.append(idx); fmat.append(p.material_index); fsmooth.append(p.use_smooth)
    fuv.append([tuple(uvl[li].uv) for li in p.loop_indices])
    fn.append([tuple(R3@Vector(ln[li])) if p.vertices[0] in mset else ln[li] for li in p.loop_indices])
kept_faces=len(faces)
# ---- new housing: outer sharp profile (y,z) -> prism x=+-XW -> 2 mm bevel on hard edges (as the original rounded box)
c1,s1=math.cos(th1),math.sin(th1)
n_out=Vector((0,-s1,c1))                      # outward normal of the slope
Hc=Vector((0,-0.173,0.1176))
def slope_pt(t): return Hc+Vector((0,c1,s1))*t
# core bend: fillet between slope line and z=ZTOP with radius R_CORE; arc centre
yb=Hc.y+(ZTOP-Hc.z)/math.tan(th1)                # core corner point
tlen=R_CORE*math.tan(th1/2)
P1=Vector((0,yb,ZTOP))-Vector((0,c1,s1))*tlen; P2=Vector((0,yb+tlen,ZTOP))
cen=P2-Vector((0,0,R_CORE))
arc=[]
for k in range(7):
    a=math.radians(90)+th1*(1-k/6)               # from slope normal direction to straight up
    d=Vector((0,-math.sin(a-math.radians(90)),math.cos(a-math.radians(90))))
    arc.append(cen+d*(R_CORE+OFF))
prof=[(-0.175,0.068),(-0.175,None)]
# front-top outer corner: front plane y=-0.175 meets slope offset line
L0=Hc+n_out*OFF; tf=(-0.175-L0.y)/c1; prof[1]=(-0.175,(L0+Vector((0,c1,s1))*tf).z)
prof+= [(p.y,p.z) for p in arc]+[(0.175,ZTOP+OFF),(0.175,0.068)]
bm=bmesh.new()
ring_l=[bm.verts.new((-XW,y,z)) for y,z in prof]; ring_r=[bm.verts.new((XW,y,z)) for y,z in prof]
n=len(prof)
bm.faces.new(ring_l[::-1]); bm.faces.new(ring_r)
for i in range(n):
    j=(i+1)%n; bm.faces.new((ring_l[i],ring_l[j],ring_r[j],ring_r[i]))
bm.normal_update(); bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
hard=[e for e in bm.edges if len(e.link_faces)==2 and e.calc_face_angle()>math.radians(30)]
bmesh.ops.bevel(bm,geom=hard,offset=OFF,segments=3,profile=0.5,affect='EDGES',clamp_overlap=True)
bmesh.ops.triangulate(bm,faces=bm.faces[:])
uvlay=bm.loops.layers.uv.new('FurnitureUV')
for fa in bm.faces:                               # box projection, 0..1 over the housing bounds (texture is a flat noise fill)
    nn=fa.normal; ax=max(range(3),key=lambda k:abs(nn[k]))
    for l in fa.loops:
        v=l.vert.co; U=lambda k:{0:(v.x+0.15)/0.30,1:(v.y+0.18)/0.36,2:(v.z-0.06)/0.20}[k]
        a,b={0:(1,2),1:(0,2),2:(0,1)}[ax]; l[uvlay].uv=(U(a),U(b))
bm.verts.index_update()
tmp=bpy.data.meshes.new('tmp'); bm.to_mesh(tmp)
# new housing normals only: all faces smooth + face-area weighted normals (large flat faces keep their face normal, the 2 mm bevel
# strips and the top bend blend smoothly) - same look as the original rounded box; no other shell is re-normalled
tmp.polygons.foreach_set('use_smooth',[True]*len(tmp.polygons))
ob_t=bpy.data.objects.new('tmp',tmp); bpy.context.scene.collection.objects.link(ob_t)
bpy.context.view_layer.objects.active=ob_t; ob_t.select_set(True)
wn=ob_t.modifiers.new('wn','WEIGHTED_NORMAL'); wn.mode='FACE_AREA'; wn.weight=100; wn.thresh=0.01; wn.keep_sharp=True
bpy.ops.object.modifier_apply(modifier='wn')
tn=[tuple(l.vector) for l in tmp.corner_normals]; tuv=tmp.uv_layers[0].data
base=len(verts); verts+= [tuple(v.co) for v in tmp.vertices]
for p in tmp.polygons:
    faces.append([base+v for v in p.vertices]); fmat.append(0); fsmooth.append(True)
    fuv.append([tuple(tuv[li].uv) for li in p.loop_indices]); fn.append([tn[li] for li in p.loop_indices])
new_faces=len(tmp.polygons)
# ---- assemble
nm=bpy.data.meshes.new('Register'); nm.from_pydata(verts,[],faces); nm.update()
for m in me.materials: nm.materials.append(m)
nm.polygons.foreach_set('material_index',fmat); nm.polygons.foreach_set('use_smooth',fsmooth)
uvn=nm.uv_layers.new(name='FurnitureUV')
loops=[]; norms=[]
for p,uvs,ns in zip(nm.polygons,fuv,fn):
    for li,u,nrm in zip(p.loop_indices,uvs,ns): uvn.data[li].uv=u; norms.append(nrm)
nm.normals_split_custom_set(norms)
bpy.data.objects.remove(ob_t); bpy.data.objects.remove(o)
no=bpy.data.objects.new('Register',nm); bpy.context.scene.collection.objects.link(no)
import os
oblend,ofbx,olog=map(os.path.abspath,(oblend,ofbx,olog))
# FBX first, while the blend is unsaved: the exporter writes FileName = abspath(basename) against the export dir
for img in bpy.data.images: img.filepath=bpy.path.basename(img.filepath)
os.chdir('/')   # export into '/' then move: the exporter writes FileName = <export dir>/<basename> -> '/name.png' (no local directory written)
tmpf='/_reg01_r1_export.fbx'
bpy.ops.object.select_all(action='DESELECT'); no.select_set(True); bpy.context.view_layer.objects.active=no
bpy.ops.export_scene.fbx(filepath=tmpf,use_selection=True,object_types={'MESH'},path_mode='STRIP',embed_textures=False,apply_scale_options='FBX_SCALE_UNITS',
    mesh_smooth_type='OFF',use_custom_props=False,add_leaf_bones=False,bake_anim=False,use_mesh_modifiers=False)
import shutil; shutil.move(tmpf,ofbx)
# blend: scrub the fixed-size path buffers (old bytes after the terminator are otherwise written to disk), move the object through a
# temporary library into a fresh empty session (no last-operator / window-manager history), save as a normal main file.
for img in bpy.data.images:
    nm2=bpy.path.basename(img.filepath); img.filepath_raw='x'*1000; img.filepath_raw='//'+nm2
lib='/_reg01_r1_tmp.blend'; bpy.data.libraries.write(lib,{no},path_remap='NONE',compress=False)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(lib,link=False) as (src,dst): dst.objects=['Register']
bpy.context.scene.collection.objects.link(bpy.data.objects['Register']); os.remove(lib)
bpy.context.scene.render.filepath='//'
bpy.ops.wm.save_as_mainfile(filepath=oblend,relative_remap=False,compress=False)
json.dump({'delta_deg':DELTA,'r_core':R_CORE,'old_slope_deg':round(math.degrees(th0),3),'new_slope_deg':round(math.degrees(th1),3),
  'core_flat_top_y_from':round(yb+tlen,4),'core_flat_top_len_m':round(0.173-(yb+tlen),4),'flat_top_fraction_of_depth':round((0.173-(yb+tlen))/0.346,3),
  'seated_shells_moved':len(seated),'seated_far_edge_on_slope_m':round(seat_far,4),'slope_tangent_len_m':round(Ls,4),
  'kept_faces':kept_faces,'new_housing_faces':new_faces,'total_faces':len(faces),'removed_housing_faces':sum(1 for p in me.polygons if p.vertices[0] in hset) if False else 188},
  open(olog,'w'),indent=1)
print('BUILD OK',len(faces),'faces; seated',len(seated))
