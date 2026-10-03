# same camera/light/render for baseline/A1/A2: 4 frames in a 2x2 wall layout (F22 UL, F23 UR, F24 LL, F25 LR), viewed from front (-Y) and an oblique.
# args: tag painting_png [finish_png_for_frames_or_-] [frame_fbx_dir_or_-]
import bpy,sys,math,os
from mathutils import Vector,Matrix
a=sys.argv[sys.argv.index('--')+1:]; tag,ppng=a[0],a[1]; fpng=a[2] if len(a)>2 and a[2]!='-' else None; fdir=a[3] if len(a)>3 and a[3]!='-' else 'src9/assets/codex-source/coord10-art01-20261003'
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=64; s.cycles.use_denoising=True
s.view_settings.view_transform='Standard'; s.render.resolution_x=1200; s.render.resolution_y=1200
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.75,0.75,0.72,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.7
L=bpy.data.lights.new('key','SUN'); L.energy=2.5; L.angle=0.4; lo=bpy.data.objects.new('key',L); s.collection.objects.link(lo); lo.rotation_euler=(math.radians(70),0,math.radians(-20))
pos={'22':(-0.24,0,0.62),'23':(0.25,0,0.62),'24':(-0.24,0,0.05),'25':(0.25,0,0.07)}
for n,p in pos.items():
    bpy.ops.import_scene.fbx(filepath=f'{fdir}/Frame_{n}_FUR06.fbx')
    o=bpy.context.selected_objects[0]; o.location=Vector(p)-Vector((0,0,0))
    if fpng and '{n}' in fpng:
        for i,m in enumerate(o.data.materials):
            if 'Finish' in m.name:
                mc=m.copy(); mc.name=f'FinishAtlas_FUR06_A2_F{n}'
                for nd in mc.node_tree.nodes:
                    if nd.type=='TEX_IMAGE': nd.image=bpy.data.images.load(os.path.abspath(fpng.replace('{n}',n)))
                o.data.materials[i]=mc
pimg=bpy.data.images.load(os.path.abspath(ppng)); pimg.colorspace_settings.name='sRGB'
fimg=bpy.data.images.load(os.path.abspath(fpng)) if fpng and '{n}' not in fpng else None
for m in bpy.data.materials:
    if not m.use_nodes: continue
    for nd in m.node_tree.nodes:
        if nd.type=='TEX_IMAGE':
            if 'Painting' in m.name: nd.image=pimg
            elif fimg is not None and 'Finish' in m.name and '_A2_' not in m.name: nd.image=fimg
# wall plane behind
bpy.ops.mesh.primitive_plane_add(size=3,location=(0,0.001,1.0),rotation=(math.radians(90),0,0))
wm=bpy.data.materials.new('wall'); wm.use_nodes=True; wm.node_tree.nodes['Principled BSDF'].inputs[0].default_value=(0.85,0.84,0.78,1); bpy.context.object.data.materials.append(wm)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera=cam
def shoot(name,d,ortho,size):
    c=Vector((0,0,0.585)); d=Vector(d).normalized()
    cam.data.type='ORTHO' if ortho else 'PERSP'; cam.data.ortho_scale=size; cam.data.lens=50
    loc=c+d*(4 if ortho else 2.6); f=(c-loc).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
    cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
    s.render.filepath=f'art/{tag}_{name}.png'; bpy.ops.render.render(write_still=True)
shoot('front',(0,-1,0),True,1.25)
shoot('oblique',(0.55,-1,-0.25),False,0)
