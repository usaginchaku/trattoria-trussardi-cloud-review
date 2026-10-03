# F19 self-made model only, front orthographic view; same camera / light / render for baseline and candidate.
# Only the FinishAtlas image of F19's own (imported) materials is swapped; PaintingAtlas fixed to the original input (read-only).
# usage: blender-python render_art06.py -- tag input_dir finish_png out_png
import bpy,sys,math,os
from mathutils import Vector,Matrix
tag,I,fin,outp=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=48; s.cycles.use_denoising=True; s.view_settings.view_transform='Standard'
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.8,0.8,0.78,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.8
L=bpy.data.lights.new('key','SUN'); L.energy=2.2; L.angle=0.4; lo=bpy.data.objects.new('key',L); s.collection.objects.link(lo); lo.rotation_euler=(math.radians(60),0,math.radians(-25))
bpy.ops.import_scene.fbx(filepath=f'{I}/Frame_19_FUR06.fbx')
img=bpy.data.images.load(os.path.abspath(fin)); n=0
for m in bpy.data.materials:
    if m.use_nodes:
        for nd in m.node_tree.nodes:
            if nd.type=='TEX_IMAGE' and nd.image and 'Finish' in nd.image.name: nd.image=img; n+=1
print('finish nodes swapped',n)
bpy.ops.mesh.primitive_plane_add(size=3,location=(0,0.001,0.3),rotation=(math.radians(90),0,0))
wm=bpy.data.materials.new('wall'); wm.use_nodes=True; wm.node_tree.nodes['Principled BSDF'].inputs[0].default_value=(0.9,0.9,0.85,1); bpy.context.object.data.materials.append(wm)
o=[x for x in s.objects if x.type=='MESH' and x.name!='Plane'][0]
bb=[o.matrix_world@Vector(c) for c in o.bound_box]; c=sum(bb,Vector())/8; size=max(max(v.x for v in bb)-min(v.x for v in bb),max(v.z for v in bb)-min(v.z for v in bb))*1.15
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera=cam
cam.data.type='ORTHO'; cam.data.ortho_scale=size; loc=c+Vector((0,-3,0)); f=(c-loc).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
s.render.resolution_x=s.render.resolution_y=900; s.render.filepath=outp; bpy.ops.render.render(write_still=True)
