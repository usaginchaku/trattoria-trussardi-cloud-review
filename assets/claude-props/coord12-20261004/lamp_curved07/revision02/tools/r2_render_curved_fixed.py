# LAMP07: copy of lamp_standoff05/revision02/tools/render_lamp_wall_r2.py; fixed target (no re-centering) for baseline and C1, plus one
# view approximating the right arch-jamb lamp of DU_ep10-4 (seen from the room, from the side and slightly below; long lens). Model only.
# revision02 (LAMP05): copy of lamp_compare03/tools/render_lamp.py with the wall as a 6 cm slab whose room face is at Y=0 (+0.0002) so the
# side view shows what is behind the wall face. Otherwise unchanged.
# same camera / light / material / render for every lamp model: open the given blend (its own materials and Shade texture),
# wall plane at Y=+0.0005 (plate back is Y=0), sun + world. Views: front (ortho, from -Y), side (ortho, from +X),
# eye_oblique (perspective from below and to the side, roughly a standing viewer 1.6 m away). Models are framed with ONE shared box so
# Curved / Straight / C1 render at the same scale.
# usage: blender-python render_lamp.py -- model.blend tag out_prefix out_json
import bpy,sys,math,json,os
from mathutils import Vector,Matrix
bl,tag,outp,oj=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(bl))
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=48; s.cycles.use_denoising=True; s.view_settings.view_transform='Standard'
for o in list(bpy.data.objects):
    if o.type in ('CAMERA','LIGHT'): bpy.data.objects.remove(o)
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.85,0.85,0.82,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.6
L=bpy.data.lights.new('key','SUN'); L.energy=2.5; L.angle=0.3; lo=bpy.data.objects.new('key',L); s.collection.objects.link(lo); lo.rotation_euler=(math.radians(55),0,math.radians(-30))
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0.0002+0.03,0.2)); bpy.context.object.scale=(1.6,0.06,1.6)   # wall slab: room face at Y=+0.0002 (Y=0 wall), 6 cm thick
wm=bpy.data.materials.new('wall'); wm.use_nodes=True; wm.node_tree.nodes['Principled BSDF'].inputs[0].default_value=(0.88,0.87,0.82,1); bpy.context.object.data.materials.append(wm)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera=cam
C=Vector((0,-0.19,0.2)); views={}
def shoot(name,d,ortho,size,dist,lens=50):
    s.render.resolution_x,s.render.resolution_y=(700,700); d=Vector(d).normalized()
    cam.data.type='ORTHO' if ortho else 'PERSP'; cam.data.ortho_scale=size; cam.data.lens=lens; cam.data.clip_start=0.01
    loc=C+d*dist; f=(C-loc).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
    cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
    p=f'{outp}_{tag}_{name}.png'; s.render.filepath=p; bpy.ops.render.render(write_still=True)
    views[name]={'target':list(C),'dir':list(d),'ortho':ortho,'ortho_scale':size,'dist':dist,'lens_mm':lens,'res':[700,700],'cam_loc':list(loc)}
shoot('front',(0,-1,0),True,0.62,2)
shoot('side',(1,0,0),True,0.62,2)
shoot('eye_oblique',(0.55,-0.75,-0.55),False,0,1.6,lens=50)
shoot('ref_like_jamb',(math.sin(math.radians(65))*math.cos(math.radians(-10)),-math.cos(math.radians(65))*math.cos(math.radians(-10)),math.sin(math.radians(-10))),False,0,3.0,lens=135)
json.dump({'engine':'CYCLES CPU 48spp denoise, Standard view transform','world':[0.85,0.85,0.82,0.6],'sun':{'energy':2.5,'angle':0.3,'rot_deg':[55,0,-30]},
  'wall':'slab Y=+0.0002..+0.0602 (room face = Y=0 wall), color (0.88,0.87,0.82)','materials':'model blend materials unchanged (Metal_ARCH01, Shade_ARCH01 + Shade_ARCH01.png)','views':views},open(oj,'w'),indent=1)
