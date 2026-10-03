# same-camera renders of menu stand candidates; adds a render-only outline of the lowest tread (0.32 m along world X) centred on the post, rotated by -parent yaw into local space
import bpy,math,sys
from mathutils import Vector,Matrix
blend,tag=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=blend)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=48; s.cycles.use_denoising=True
s.view_settings.view_transform='Standard'; s.render.resolution_x=800; s.render.resolution_y=800
for o in list(bpy.data.objects):
    if o.type in('LIGHT','CAMERA'): bpy.data.objects.remove(o)
if not s.world: s.world=bpy.data.worlds.new('w')
w=s.world; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.6,0.62,0.65,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.9
def light(n,rot,e):
    L=bpy.data.lights.new(n,'SUN'); L.energy=e; L.angle=0.3; o=bpy.data.objects.new(n,L); s.collection.objects.link(o); o.rotation_euler=rot
light('key',(math.radians(40),0,math.radians(-35)),3.0); light('fill',(math.radians(60),0,math.radians(140)),1.0)
yaw=math.radians(8.0)
# render-only display colours: timber texture is not part of the received set (shows magenta) -> plain colour; Menu material kept
for mat in bpy.data.materials:
    if mat.use_nodes and mat.name.startswith(('Timber','Groove')):
        bsdf=[n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0]
        for l in list(bsdf.inputs['Base Color'].links): mat.node_tree.links.remove(l)
        bsdf.inputs['Base Color'].default_value=(0.32,0.2,0.12,1) if mat.name.startswith('Timber') else (0.1,0.08,0.06,1)
    if mat.use_nodes and mat.name.startswith('Menu'):
        for n in mat.node_tree.nodes:
            if n.type=='TEX_IMAGE': n.image=bpy.data.images.load('<scratch>/src9/assets/codex-source/coord09-menu-foot-20261003/Menu_FOLLOWUP04.png')
# tread: world X width 0.32 (design), depth along world Z 1.49 -> local: rotate by -yaw about up
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-0.0035-0.01))
t=bpy.context.object; t.scale=(0.32,0.9,0.02); t.rotation_euler=(0,0,yaw)
m=bpy.data.materials.new('tread'); m.use_nodes=True; m.node_tree.nodes['Principled BSDF'].inputs[0].default_value=(0.75,0.55,0.45,1); t.data.materials.append(m)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera=cam
def shoot(name,d,cz,size,ortho=True):
    c=Vector((0,0,cz)); d=Vector(d).normalized()
    cam.data.type='ORTHO' if ortho else 'PERSP'; cam.data.ortho_scale=size; cam.data.lens=50
    loc=c+d*4 if ortho else c+d*size*2.2
    f=(c-loc).normalized(); up=Vector((0,0,1)) if abs(f.z)<0.99 else Vector((-math.sin(yaw),math.cos(yaw),0))
    r=f.cross(up).normalized(); u=r.cross(f)
    cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
    s.render.filepath=f'r9/menu{tag}_{name}.png'; bpy.ops.render.render(write_still=True)
shoot('front',(0,-1,0),0.74,1.7)
shoot('side',(1,0,0),0.74,1.7)
shoot('top',(0,-0.0001,1),0.0,0.8)
shoot('feet_q34',(0.7,-0.9,0.5),0.12,0.8,False)
