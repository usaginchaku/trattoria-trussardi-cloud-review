# same camera / light / materials for baseline and candidate: the three supplied FBX at their design positions along the wall
# (x = design z 0.53 / 1.29 / 2.10, common base height), only the PaintingAtlas image is swapped. Finish atlas, geometry, UVs fixed.
# usage: blender-python render_art05.py -- tag input_dir painting_png out_prefix
import bpy,sys,math,os
from mathutils import Vector,Matrix
tag,I,png,outp=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=48; s.cycles.use_denoising=True; s.view_settings.view_transform='Standard'
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.8,0.8,0.78,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.8
L=bpy.data.lights.new('key','SUN'); L.energy=2.2; L.angle=0.4; lo=bpy.data.objects.new('key',L); s.collection.objects.link(lo); lo.rotation_euler=(math.radians(60),0,math.radians(-25))
img=bpy.data.images.load(os.path.abspath(png))
for n,x in ((17,0.53),(18,1.29),(19,2.10)):
    bpy.ops.import_scene.fbx(filepath=f'{I}/Frame_{n}_FUR06.fbx'); o=bpy.context.selected_objects[0]; o.location=(x,0,0)
for m in bpy.data.materials:
    if m.use_nodes and 'Painting' in m.name:
        for nd in m.node_tree.nodes:
            if nd.type=='TEX_IMAGE': nd.image=img
bpy.ops.mesh.primitive_plane_add(size=6,location=(1.3,0.001,0.3),rotation=(math.radians(90),0,0))
wm=bpy.data.materials.new('wall'); wm.use_nodes=True; wm.node_tree.nodes['Principled BSDF'].inputs[0].default_value=(0.9,0.9,0.85,1); bpy.context.object.data.materials.append(wm)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera=cam
def shoot(name,c,d,ortho,size,dist,res,lens=50):
    s.render.resolution_x,s.render.resolution_y=res; c=Vector(c); d=Vector(d).normalized()
    cam.data.type='ORTHO' if ortho else 'PERSP'; cam.data.ortho_scale=size; cam.data.lens=lens
    loc=c+d*dist; f=(c-loc).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
    cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
    s.render.filepath=f'{outp}_{tag}_{name}.png'; bpy.ops.render.render(write_still=True)
shoot('front_close',(1.31,0,0.16),(0,-1,0),True,2.2,3,(1600,360))
shoot('oblique_context',(1.2,0,0.16),(0.75,-1,-0.35),False,0,2.6,(1200,700),lens=40)     # from the near (F19) side, wall receding toward F17 as in the reference view
