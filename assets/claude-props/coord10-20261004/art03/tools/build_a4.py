# COORD10-ART03 A4: shallow V grooves across the Frame_22 frame bars (olive frame faces only).
# Each groove = 3 bisect cuts (t-w/2, t, t+w/2) through the bar's front-facing olive faces; centre-line vertices are pushed back (+y) by depth d.
# Vertices touching a non-olive face (mat/rim/painting) or a face whose plane would bend are not moved, so mat/painting faces stay unchanged.
# Outer size, mount face (y=0), origin/axes unchanged. Normals: flat (custom normal = face normal), same as the source convention.
# args: -- tag outdir texdir width_m depth_m n_side n_tb (env A4_CUT=all|flat|flat2|ring)
import bpy,bmesh,os,sys,json,numpy as np
from mathutils import Vector
tag,outdir,texdir,W,D,NS,NT=sys.argv[sys.argv.index('--')+1:]; W=float(W); D=float(D); NS=int(NS); NT=int(NT)
CUT=os.environ.get('A4_CUT','all'); NY=-0.15 if CUT=='all' else -0.95
R=os.environ.get('ART_SRC','src9/assets/codex-source/coord10-art01-20261003')
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=f'{R}/Frame_22_FUR06.fbx')
o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
fin=[i for i,m in enumerate(me.materials) if 'Finish' in m.name][0]
src_tris=len(me.polygons); src_verts=len(me.vertices)
bm=bmesh.new(); bm.from_mesh(me); uvl=bm.loops.layers.uv[0]
def is_olive(f):
    if f.material_index!=fin: return False
    u=sum((l[uvl].uv for l in f.loops),Vector((0,0)))/len(f.loops); return int(u.x*4)==2 and int((1-u.y)*4)==0
def in_groove(f):
    # faces that form the groove surface: flat front bands (n.y<=-0.95) + the bevel row touching them
    if not is_olive(f): return False
    if f.normal.y<=-0.95: return True
    return f.normal.y<=-0.15 and any(g.normal.y<=-0.95 and is_olive(g) for e in f.edges for g in e.link_faces if g is not f)
def in_cut(f):
    if not is_olive(f): return False
    if CUT=='ring': return True      # whole bar cross-section ring is cut, so no neighbour face receives collinear edge vertices
    if CUT!='flat2': return f.normal.y<=NY
    if f.normal.y<=-0.95: return True
    return f.normal.y<=-0.15 and any(g.normal.y<=-0.95 and is_olive(g) for e in f.edges for g in e.link_faces if g is not f)
def bar_faces(kind):
    out=[]
    for f in bm.faces:
        if not in_cut(f): continue
        c=f.calc_center_median()
        if kind=='L' and c.x<-0.148: out.append(f)
        elif kind=='R' and c.x>0.148: out.append(f)
        elif kind=='B' and c.z<0.03 and abs(c.x)<0.16: out.append(f)
        elif kind=='T' and c.z>0.49 and abs(c.x)<0.16: out.append(f)
    return out
zs=np.linspace(0.045,0.475,NS); xs=np.linspace(-0.12,0.12,NT)
grooves=[('L',2,z) for z in zs]+[('R',2,z) for z in zs]+[('B',0,x) for x in xs]+[('T',0,x) for x in xs]
centre=[]
for kind,ax,t in grooves:
    for off in (-W/2,W/2,0.0):
        fs=bar_faces(kind); geom=list(set(fs)|{e for f in fs for e in f.edges}|{v for f in fs for v in f.verts})
        n=Vector((0,0,0)); n[ax]=1; co=Vector((0,0,0)); co[ax]=t+off
        bmesh.ops.bisect_plane(bm,geom=geom,plane_co=co,plane_no=n,dist=1e-7)
    bm.verts.ensure_lookup_table()
    fs=set(bar_faces(kind))
    if CUT=='ring': fs={f for f in fs if in_groove(f)}
    for v in bm.verts:
        if abs(v.co[ax]-t)>1e-6 or not any(f in fs for f in v.link_faces): continue
        ok=(all(f in fs or (is_olive(f) and abs(f.normal.y)<0.05) for f in v.link_faces) if CUT=='all' else all(is_olive(f) for f in v.link_faces) if CUT=='flat' else all(f in fs for f in v.link_faces))  # flat2/ring: only verts surrounded by groove faces
        if ok: centre.append(v)
centre=list(set(centre))
for v in centre: v.co.y+=D
# neighbour faces outside the groove set only received collinear edge vertices: fan them from an added centre vertex (poke) to avoid zero-area triangles
if CUT in ('flat2','ring'):
    ng=[f for f in bm.faces if len(f.verts)>4 and not in_groove(f)]
    poked=len(ng); bmesh.ops.poke(bm,faces=ng,center_mode='MEAN')
else: poked=0
bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>3],quad_method='BEAUTY',ngon_method='BEAUTY')
# n-gons with collinear inserted vertices can yield zero-area triangles: flip the longest edge of each such triangle
flips=0
for it in range(20):
    bad=[f for f in bm.faces if f.calc_area()<1e-10]
    if not bad: break
    es=set()
    for f in bad:
        e=max(f.edges,key=lambda e:e.calc_length())
        if len(e.link_faces)==2: es.add(e)
    r=bmesh.ops.rotate_edges(bm,edges=list(es),use_ccw=False); flips+=len(r['edges'])
zero_left=sum(1 for f in bm.faces if f.calc_area()<1e-10)
bm.normal_update()
bm.to_mesh(me); me.update()
lf=[0]*len(me.loops)
for p in me.polygons:
    for li in p.loop_indices: lf[li]=p.index
me.normals_split_custom_set([me.polygons[lf[i]].normal.copy() for i in range(len(me.loops))]); me.update()
info={'tag':tag,'cut_faces':CUT,'groove_width_m':W,'groove_depth_m':D,'side_grooves_each':NS,'top_bottom_grooves_each':NT,'side_z':[round(z,4) for z in zs],'tb_x':[round(x,4) for x in xs],
      'pushed_vertices':len(centre),'degenerate_edge_flips':flips,'poked_neighbour_ngons':poked,'zero_area_left':zero_left,'verts':[src_verts,len(me.vertices)],'tris':[src_tris,len(me.polygons)]}
os.makedirs(f'{outdir}/fbx',exist_ok=True); os.makedirs(f'{outdir}/models',exist_ok=True)
o.select_set(True); bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=f'{outdir}/fbx/Frame_22_FUR06_{tag}.fbx',use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=False,mesh_smooth_type='FACE',add_leaf_bones=False,path_mode='STRIP')
for m in me.materials:
    if 'Painting' in m.name: m.name='PaintingAtlas_FUR06_A1'; img='PaintingAtlas_FUR06_A1.png'
    else: m.name='FinishAtlas_FUR06_A2_F22'; img='FinishAtlas_FUR06_A2_F22.png'
    for nd in m.node_tree.nodes:
        if nd.type=='TEX_IMAGE': nd.image=bpy.data.images.load(os.path.abspath(f'{texdir}/{img}'))
for im in list(bpy.data.images):
    if im.users==0: bpy.data.images.remove(im)
for im in bpy.data.images:
    b=os.path.basename(im.filepath); im.filepath_raw='x'*1000; im.filepath_raw='//../../../textures/'+b
for sc in bpy.data.scenes: sc.render.filepath='x'*1000; sc.render.filepath='//render/'
bpy.ops.wm.save_as_mainfile(filepath=f'{outdir}/models/Frame_22_FUR06_{tag}.blend',compress=True,relative_remap=False)
json.dump(info,open(f'{outdir}/build_{tag}.json','w'),indent=1); print('INFO',json.dumps(info))
