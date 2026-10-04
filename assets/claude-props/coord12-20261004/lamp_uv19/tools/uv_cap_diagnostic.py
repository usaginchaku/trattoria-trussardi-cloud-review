# diagnostic only (no model file is written): (1) UV diagram of the two arm end caps, input vs UVFIX (PIL, self-made);
# (2) close render of the arm alone (collar/shade/diffuser/plate deleted in memory) with a render-only UV checker material, same camera,
# light and render for both files, so degenerate (striped) vs proper cap UVs are visible. Caps are normally hidden inside collar/plate.
# usage: blender-python uv_cap_diagnostic.py -- input.blend fixed.blend out_dir
import bpy,bmesh,sys,os,math
import numpy as np
from mathutils import Vector,Matrix
from PIL import Image,ImageDraw
ib,fb,od=sys.argv[sys.argv.index('--')+1:]
TOP=set(range(1070,1086)); WALL=set(range(1390,1406))
def caps(p):
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p)); me=bpy.data.objects['StraightLamp'].data; uv=me.uv_layers[0].data; out={'top':[],'wall':[]}
    for f in me.polygons:
        vs=set(f.vertices)
        if vs<=TOP or vs<=WALL: out['top' if vs<=TOP else 'wall'].append([tuple(uv[l].uv) for l in f.loop_indices])
    return out
ci,cf=caps(ib),caps(fb)
W,H=900,470; img=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(img)
panels=[('top cap (z const)',ci['top'],cf['top']),('wall cap (y const)',ci['wall'],cf['wall'])]
for k,(name,a,b) in enumerate(panels):
    x0=20+k*450; pts=[p for t in a+b for p in t]; u=[p[0] for p in pts]; v=[p[1] for p in pts]
    cu,cv=(min(u)+max(u))/2,(min(v)+max(v))/2; sc=360/max(max(u)-min(u),max(v)-min(v),1e-6)
    T=lambda p:(x0+205+(p[0]-cu)*sc, 245-(p[1]-cv)*sc)
    d.rectangle([x0,40,x0+410,450],outline=(180,180,180)); d.text((x0+5,10),name+': grey fill = UVFIX triangles, red = input (collapsed to a line)',fill='black')
    for t in b: d.polygon([T(p) for p in t],fill=(200,215,230),outline=(60,90,130))
    for t in a: d.line([T(p) for p in t]+[T(t[0])],fill=(220,30,30),width=3)
    d.text((x0+5,455),'U range %.4f..%.4f  V(input) %.4f  V(fix) %.4f..%.4f'%(min(u),max(u),a[0][0][1],min(p[1] for t in b for p in t),max(p[1] for t in b for p in t)),fill='black')
img.save(os.path.join(od,'uv_caps_input_vs_uvfix.png'))
def render(p,tag):
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p)); o=bpy.data.objects['StraightLamp']; me=o.data
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bmesh.ops.delete(bm,geom=[bm.verts[i] for i in range(0,1070)],context='VERTS'); bm.to_mesh(me); bm.free()
    m=bpy.data.materials.new('checker_diag'); m.use_nodes=True; nt=m.node_tree; ck=nt.nodes.new('ShaderNodeTexChecker'); ck.inputs['Scale'].default_value=300.0
    uvn=nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map='ArchitectureUV'; nt.links.new(uvn.outputs['UV'],ck.inputs['Vector']); nt.links.new(ck.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color'])
    me.materials.clear(); me.materials.append(m)
    s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=32; s.cycles.use_denoising=True; s.view_settings.view_transform='Standard'
    w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[1].default_value=1.0
    L=bpy.data.lights.new('k','SUN'); L.energy=3; lo=bpy.data.objects.new('k',L); s.collection.objects.link(lo); lo.rotation_euler=(math.radians(40),0,math.radians(140))
    cam=bpy.data.objects.new('c',bpy.data.cameras.new('c')); s.collection.objects.link(cam); s.camera=cam
    C=Vector((0,-0.07,0.10)); dv=Vector((0.55,0.6,0.58)).normalized(); loc=C+dv*0.6; f=(C-loc).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
    cam.data.lens=70; cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
    s.render.resolution_x=s.render.resolution_y=600; s.render.filepath=os.path.join(od,'arm_caps_checker_%s.png'%tag); bpy.ops.render.render(write_still=True)
render(ib,'A_input'); render(fb,'A_UVFIX')
print('DIAG OK')
