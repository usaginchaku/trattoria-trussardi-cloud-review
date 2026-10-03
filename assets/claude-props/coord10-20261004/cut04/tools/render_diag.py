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
silver=bpy.data.materials.new('diag_checker_UV0'); silver.use_nodes=True; b=silver.node_tree.nodes['Principled BSDF']
# DIAGNOSTIC ONLY: procedural checker driven by UVMap (UV0); not an adopted material or texture
_nt=silver.node_tree; _uv=_nt.nodes.new('ShaderNodeUVMap'); _uv.uv_map='UVMap'; _ck=_nt.nodes.new('ShaderNodeTexChecker'); _ck.inputs['Scale'].default_value=900
_ck.inputs['Color1'].default_value=(0.9,0.15,0.1,1); _ck.inputs['Color2'].default_value=(0.95,0.95,0.95,1); _nt.links.new(_uv.outputs[0],_ck.inputs['Vector']); _nt.links.new(_ck.outputs['Color'],b.inputs['Base Color'])
b.inputs['Base Color'].default_value=MAT['base_color']; b.inputs['Metallic'].default_value=0.0; b.inputs['Roughness'].default_value=0.6
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
    s.render.filepath=f'cut4/r/{tag}_{name}.png'; bpy.ops.render.render(write_still=True)

shoot('diag_oblique',(-0.03,0.06,0.0),(0.6,-0.6,0.45),False,0,0.22,(1100,800),lens=60)
json.dump(MAT,open(f'cut4/r/{tag}_material.json','w'))
