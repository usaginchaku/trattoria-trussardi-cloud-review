# identical plain-silver preview for source and candidate cutlery (same camera / light / exposure / render settings).
# Material (shared, JSON-recorded): Principled, base (0.78,0.79,0.80), metallic 1.0, roughness 0.28. Cloud silver is NOT the RI11 Unity material.
# args: -- tag fork.fbx spoon.fbx knife.fbx
import bpy,sys,math,json
from mathutils import Vector,Matrix
tag,ff,fs,fk=sys.argv[sys.argv.index('--')+1:]
MAT={'base_color':[0.78,0.79,0.80,1],'metallic':1.0,'roughness':0.28}
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=96; s.cycles.use_denoising=True; s.view_settings.view_transform='Standard'; s.view_settings.exposure=0.0
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; nt=w.node_tree; bg=nt.nodes['Background']
# simple two-tone environment so metal shows form: bright sky gradient
grad=nt.nodes.new('ShaderNodeTexGradient'); tc=nt.nodes.new('ShaderNodeTexCoord'); ramp=nt.nodes.new('ShaderNodeValToRGB')
sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'],sep.inputs[0])
nt.links.new(sep.outputs['Z'],ramp.inputs[0]); ramp.color_ramp.elements[0].color=(0.03,0.03,0.03,1); ramp.color_ramp.elements[1].color=(0.55,0.55,0.53,1)
nt.links.new(ramp.outputs[0],bg.inputs[0]); bg.inputs[1].default_value=0.6
L=bpy.data.lights.new('key','AREA'); L.energy=12; L.size=0.4; lo=bpy.data.objects.new('key',L); s.collection.objects.link(lo); lo.location=(0.35,-0.45,0.7); lo.rotation_euler=(math.radians(40),0,math.radians(35))
silver=bpy.data.materials.new('preview_silver'); silver.use_nodes=True; b=silver.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value=MAT['base_color']; b.inputs['Metallic'].default_value=MAT['metallic']; b.inputs['Roughness'].default_value=MAT['roughness']
objs=[]
for path,x in ((ff,-0.05),(fs,0.0),(fk,0.05)):
    bpy.ops.import_scene.fbx(filepath=path); o=bpy.context.selected_objects[0]; o.location.x=x
    o.data.materials.clear(); o.data.materials.append(silver); objs.append(o)
# table + plate context (self-made, same for both)
bpy.ops.mesh.primitive_plane_add(size=3,location=(0,0,-0.0001)); tb=bpy.context.object
tm=bpy.data.materials.new('cloth'); tm.use_nodes=True; tm.node_tree.nodes['Principled BSDF'].inputs[0].default_value=(0.30,0.24,0.20,1); tb.data.materials.append(tm)
bpy.ops.mesh.primitive_cylinder_add(radius=0.13,depth=0.015,location=(-0.22,0,0.0075),vertices=96); pl=bpy.context.object
pm=bpy.data.materials.new('plate'); pm.use_nodes=True; pm.node_tree.nodes['Principled BSDF'].inputs[0].default_value=(0.92,0.92,0.90,1); pl.data.materials.append(pm)
bpy.ops.object.shade_smooth()
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera=cam
def shoot(name,c,d,ortho,size,dist,res,lens=50,up=(0,0,1)):
    s.render.resolution_x,s.render.resolution_y=res
    c=Vector(c); d=Vector(d).normalized(); cam.data.type='ORTHO' if ortho else 'PERSP'; cam.data.ortho_scale=size; cam.data.lens=lens
    loc=c+d*dist; f=(c-loc).normalized(); upv=Vector(up); r=f.cross(upv).normalized(); u=r.cross(f)
    cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
    s.render.filepath=f'cut3/r/{tag}_{name}.png'; bpy.ops.render.render(write_still=True)
shoot('top',(0,0.004,0),(0,0,1),True,0.26,1,(900,1000),up=(0,1,0))
pl.hide_render=True; tb.hide_render=True
for i,o in enumerate(objs):                                              # side elevation, one item at a time (others, plate, table hidden)
    for j,p in enumerate(objs): p.hide_render=(j!=i)
    shoot(f'side{i}',(o.location.x,0.004,0.008),(-1,0,0),True,0.235,2,(1300,190))
for p in objs: p.hide_render=False
pl.hide_render=False; tb.hide_render=False
shoot('oblique',(0,0.02,0.0),(0.45,-0.75,0.55),False,0,0.42,(1100,800),lens=60)
shoot('table',(-0.08,0,0.0),(0.25,-0.85,0.75),False,0,1.1,(1000,700),lens=50)
shoot('blade_top',(0.05,0.072,0),(0,0,1),True,0.07,1,(900,1000),up=(0,1,0))       # knife blade outline close-up (ortho, from above)
json.dump(MAT,open(f'cut3/r/{tag}_material.json','w'))
