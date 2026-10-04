# same camera / light / materials / render for input vs candidate: FBX imported with default settings, the 4 input PNGs bound by basename
# from the input folder for both, counter-top plane + wall, sun + world light. Views: side (ortho, +X), oblique (persp), table distance (persp).
# usage: blender-python render_register_r1.py -- tag model.fbx tex_dir out_prefix
import bpy,sys,math,os
from mathutils import Vector,Matrix
tag,fbx,tex,outp=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=48; s.cycles.use_denoising=True; s.view_settings.view_transform='Standard'
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.85,0.85,0.82,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.7
L=bpy.data.lights.new('key','SUN'); L.energy=2.5; L.angle=0.3; lo=bpy.data.objects.new('key',L); s.collection.objects.link(lo); lo.rotation_euler=(math.radians(50),0,math.radians(35))
bpy.ops.import_scene.fbx(filepath=fbx)
for img in bpy.data.images: img.filepath=os.path.join(tex,bpy.path.basename(img.filepath)); img.reload()
def plane(size,loc,rot,col):
    bpy.ops.mesh.primitive_plane_add(size=size,location=loc,rotation=rot); m=bpy.data.materials.new('m'); m.use_nodes=True
    m.node_tree.nodes['Principled BSDF'].inputs[0].default_value=col; bpy.context.object.data.materials.append(m)
plane(3,(0,0,0),(0,0,0),(0.25,0.13,0.08,1))                      # counter top (neutral brown, not a reference colour)
plane(3,(0,0.6,1.0),(math.radians(90),0,0),(0.88,0.86,0.80,1))   # wall behind
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera=cam
def shoot(name,c,d,ortho,size,dist,res,lens=50):
    s.render.resolution_x,s.render.resolution_y=res; c=Vector(c); d=Vector(d).normalized()
    cam.data.type='ORTHO' if ortho else 'PERSP'; cam.data.ortho_scale=size; cam.data.lens=lens; cam.data.clip_start=0.01
    loc=c+d*dist; f=(c-loc).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
    cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
    s.render.filepath=f'{outp}_{tag}_{name}.png'; bpy.ops.render.render(write_still=True)
shoot('side',(0,0,0.125),(1,0,0),True,0.5,2,(800,640))
shoot('oblique',(0,0,0.12),(0.8,-0.9,0.45),False,0,1.0,(800,640),lens=50)
shoot('table_distance',(0,0,0.12),(0.55,-1.0,0.35),False,0,2.6,(800,640),lens=50)
