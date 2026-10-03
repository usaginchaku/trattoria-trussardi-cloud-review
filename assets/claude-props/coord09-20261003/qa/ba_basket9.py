import bpy,math,sys
from mathutils import Vector,Matrix
blend,tag=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=blend)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=48; s.cycles.use_denoising=True
s.view_settings.view_transform='Standard'; s.render.resolution_x=800; s.render.resolution_y=700
for o in list(bpy.data.objects):
    if o.type in('LIGHT','CAMERA'): bpy.data.objects.remove(o)
w=s.world; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.55,0.57,0.6,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.8
def light(n,rot,e):
    L=bpy.data.lights.new(n,'SUN'); L.energy=e; L.angle=0.3; o=bpy.data.objects.new(n,L); s.collection.objects.link(o); o.rotation_euler=rot
light('key',(math.radians(40),0,math.radians(-35)),3.0); light('fill',(math.radians(60),0,math.radians(140)),1.0)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera=cam
names=[n for n in ('02_Flower_Basket_Mesh','02_Flower_Basket_LOD1_Mesh') if n in bpy.data.objects]; B=bpy.data.objects[names[0]]
for o in bpy.data.objects:
    if o.type=='MESH': o.hide_render=o.name not in (B.name,'Render surface')
c=B.matrix_world.translation+Vector((0,0,0.115))  # fixed target height (same for all variants)
def shoot(name,off,lens,ortho=False):
    cam.data.type='ORTHO' if ortho else 'PERSP'; cam.data.ortho_scale=0.36; cam.data.lens=lens
    loc=c+off; f=(c-loc).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
    cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
    s.render.filepath=f'c9/{tag}_{name}.png'; bpy.ops.render.render(write_still=True)
shoot('front_ortho',Vector((0,-1.5,0)),50,True)
shoot('refview',Vector((0.0,-1.1,0.32)),85)   # slightly downward side view similar to IMG_3827 framing
shoot('q34',Vector((0.6,-0.75,0.55)),60)
