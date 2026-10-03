# fixed-camera renderer for furniture candidates (camera from given centre/size, identical for all variants)
import bpy,math,sys
from mathutils import Vector,Matrix
blend,tag,views,cx,cy,cz,size=sys.argv[sys.argv.index('--')+1:]
c=Vector((float(cx),float(cy),float(cz))); size=float(size)
bpy.ops.wm.open_mainfile(filepath=blend)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=48; s.cycles.use_denoising=True
s.view_settings.view_transform='Standard'; s.render.resolution_x=900; s.render.resolution_y=700
for o in list(bpy.data.objects):
    if o.type in('LIGHT','CAMERA'): bpy.data.objects.remove(o)
if not s.world: s.world=bpy.data.worlds.new('w')
w=s.world; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.6,0.62,0.65,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.9
def light(n,rot,e):
    L=bpy.data.lights.new(n,'SUN'); L.energy=e; L.angle=0.3; o=bpy.data.objects.new(n,L); s.collection.objects.link(o); o.rotation_euler=rot
light('key',(math.radians(40),0,math.radians(-35)),3.0); light('fill',(math.radians(60),0,math.radians(140)),1.0)
bpy.ops.mesh.primitive_plane_add(size=20,location=(0,0,-0.0005))
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera=cam
V={'front':(Vector((0,-1,0)),'O'),'side':(Vector((1,0,0)),'O'),'back':(Vector((0,1,0)),'O'),'q34':(Vector((0.6,-0.8,0.45)),'P'),'low':(Vector((0.35,-1,0.18)),'P'),'top':(Vector((0,-0.001,1)),'O'),'seat':(Vector((-0.5,-1,0.6)),'P')}
for v in views.split(','):
    d,t=V[v]; d=d.normalized()
    if t=='O': cam.data.type='ORTHO'; cam.data.ortho_scale=size*1.2; loc=c+d*size*4
    else: cam.data.type='PERSP'; cam.data.lens=50; loc=c+d*size*2.2
    f=(c-loc).normalized(); up=Vector((0,0,1)) if abs(f.z)<0.99 else Vector((0,1,0))
    r=f.cross(up).normalized(); u=r.cross(f)
    cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
    s.render.filepath=f'r9/{tag}_{v}.png'; bpy.ops.render.render(write_still=True)
