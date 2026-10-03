# same camera / light / world for baseline, A1, A1+A2 of the three upper frames (1 entry side left, 2 middle, 3 rear right).
# Frames are placed side by side on a wall plane at their local scale (instance scale .85/.85/.8 not applied: shape comparison only).
# args: -- tag painting_png finish_pattern ('-' = original; '{n}' replaced by 1..3, missing file -> original)
import bpy,sys,math,os
from mathutils import Vector,Matrix
tag,ppng,fpat=sys.argv[sys.argv.index('--')+1:]
R='src2/assets/codex-source/coord10-art02-input-20261004'
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=64; s.cycles.use_denoising=True
s.view_settings.view_transform='Standard'
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.75,0.75,0.72,1); bg.inputs[1].default_value=0.7
L=bpy.data.lights.new('key','SUN'); L.energy=2.5; L.angle=0.4; lo=bpy.data.objects.new('key',L); s.collection.objects.link(lo); lo.rotation_euler=(math.radians(70),0,math.radians(-20))
pimg=bpy.data.images.load(os.path.abspath(ppng)) if ppng!='-' else None
for n,x in ((1,-0.62),(2,0.0),(3,0.62)):
    bpy.ops.import_scene.fbx(filepath=f'{R}/LAY03_UpperFrame_{n}.fbx'); o=bpy.context.selected_objects[0]; o.location=(x,0,0)
    for i,m in enumerate(o.data.materials):
        mc=m.copy(); o.data.materials[i]=mc
        for nd in mc.node_tree.nodes:
            if nd.type!='TEX_IMAGE': continue
            if 'Painting' in m.name and pimg: nd.image=pimg; mc.name=f'LAY03_UpperFrame_{n}_Painting_ART02_A1'
            if 'Finish' in m.name and fpat!='-' and os.path.exists(fpat.replace('{n}',str(n))):
                nd.image=bpy.data.images.load(os.path.abspath(fpat.replace('{n}',str(n)))); mc.name=f'LAY03_UpperFrame_{n}_Finish_ART02_A2'
bpy.ops.mesh.primitive_plane_add(size=4,location=(0,0.001,0.5),rotation=(math.radians(90),0,0))
wm=bpy.data.materials.new('wall'); wm.use_nodes=True; wm.node_tree.nodes['Principled BSDF'].inputs[0].default_value=(0.85,0.84,0.78,1); bpy.context.object.data.materials.append(wm)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera=cam
def shoot(name,d,ortho,size,dist,res):
    s.render.resolution_x,s.render.resolution_y=res
    c=Vector((0,0,0.2)); d=Vector(d).normalized()
    cam.data.type='ORTHO' if ortho else 'PERSP'; cam.data.ortho_scale=size; cam.data.lens=50
    loc=c+d*dist; f=(c-loc).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
    cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
    s.render.filepath=f'art2/r/{tag}_{name}.png'; bpy.ops.render.render(write_still=True)
shoot('front',(0,-1,0),True,1.9,3,(1500,600))
shoot('oblique',(0.6,-1,-0.25),False,0,2.6,(1500,800))
shoot('far',(0,-1,0),True,1.9,3,(190,76))     # far-distance proxy: ~1/8 resolution, checks colour bleeding at the picture edges
