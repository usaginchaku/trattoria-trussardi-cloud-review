# same camera / light / world for baseline and candidates of ONE frame, with ART01 A1 painting + A2 per-frame finish (candidate materials).
# args: -- out_png_prefix fbx frame_no painting_png finish_png light(key|graze)
import bpy,sys,math,os
from mathutils import Vector,Matrix
out,fbx,n,ppng,fpng,light=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=64; s.cycles.use_denoising=True
s.view_settings.view_transform='Standard'; s.render.resolution_x=900; s.render.resolution_y=900
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.75,0.75,0.72,1); bg.inputs[1].default_value=0.7
L=bpy.data.lights.new('key','SUN'); lo=bpy.data.objects.new('key',L); s.collection.objects.link(lo)
if light=='key': L.energy=2.5; L.angle=0.4; lo.rotation_euler=(math.radians(70),0,math.radians(-20))
else: L.energy=3.0; L.angle=0.05; lo.rotation_euler=(math.radians(78),0,math.radians(-62)); bg.inputs[1].default_value=0.35
bpy.ops.import_scene.fbx(filepath=fbx); o=bpy.context.selected_objects[0]
pimg=bpy.data.images.load(os.path.abspath(ppng)); fimg=bpy.data.images.load(os.path.abspath(fpng))
for i,m in enumerate(o.data.materials):
    mc=m.copy(); mc.name=('PaintingAtlas_FUR06_A1' if 'Painting' in m.name else f'FinishAtlas_FUR06_A2_F{n}')
    for nd in mc.node_tree.nodes:
        if nd.type=='TEX_IMAGE': nd.image=pimg if 'Painting' in m.name else fimg
    o.data.materials[i]=mc
bpy.ops.mesh.primitive_plane_add(size=3,location=(0,0.001,1.0),rotation=(math.radians(90),0,0))
wm=bpy.data.materials.new('wall'); wm.use_nodes=True; wm.node_tree.nodes['Principled BSDF'].inputs[0].default_value=(0.85,0.84,0.78,1); bpy.context.object.data.materials.append(wm)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera=cam
H=o.dimensions.z
def shoot(name,d,ortho,size,dist):
    c=Vector((0,0,0.26 if n=='22' else 0.24)); d=Vector(d).normalized()
    cam.data.type='ORTHO' if ortho else 'PERSP'; cam.data.ortho_scale=size; cam.data.lens=50
    loc=c+d*dist; f=(c-loc).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
    cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
    s.render.filepath=f'{out}_{name}.png'; bpy.ops.render.render(write_still=True)
shoot('front',(0,-1,0),True,0.62,3)
shoot('oblique',(0.6,-1,-0.25),False,0,1.35)
