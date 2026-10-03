# same camera / light / preview materials for C3m baseline and C4. Preview colouring is the existing CAB03 render-only
# preview (qa/ba_cabcol.py): wood = existing FinishAtlas texture x burnt brown (0.30,0.17,0.12), panes flat grey-green,
# knobs dull olive gold; assigned by the same vertex index ranges. New crown verts (>=2132) are wood. Nothing is exported.
import bpy,sys,math,os
from mathutils import Vector,Matrix
fbx,tag=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=64; s.cycles.use_denoising=True; s.view_settings.view_transform='Standard'
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.75,0.75,0.72,1); bg.inputs[1].default_value=0.6
L=bpy.data.lights.new('key','SUN'); L.energy=3.0; L.angle=0.3; lo=bpy.data.objects.new('key',L); s.collection.objects.link(lo); lo.rotation_euler=(math.radians(35),0,math.radians(-25))
bpy.ops.import_scene.fbx(filepath=fbx); o=bpy.context.selected_objects[0]; me=o.data
base=me.materials[0]; wood=base.copy(); wood.name='prev_wood'; nt=wood.node_tree; bsdf=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]
srcs=bsdf.inputs['Base Color'].links[0].from_socket if bsdf.inputs['Base Color'].links else None
mix=nt.nodes.new('ShaderNodeMix'); mix.data_type='RGBA'; mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=1.0; mix.inputs[7].default_value=(0.30,0.17,0.12,1)
if srcs: nt.links.new(srcs,mix.inputs[6])
nt.links.new(mix.outputs[2],bsdf.inputs['Base Color'])
def flat(n,c,met,rough):
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=c; b.inputs['Metallic'].default_value=met; b.inputs['Roughness'].default_value=rough; return m
pane=flat('prev_pane',(0.17,0.24,0.21,1),0.0,0.25); knob=flat('prev_knob',(0.33,0.33,0.10,1),0.8,0.45)
me.materials.clear(); me.materials.append(wood); me.materials.append(pane); me.materials.append(knob)
panes=set(list(range(1136,1328))+list(range(1866,2058))); knobs=set(list(range(1328,1402))+list(range(2058,2132)))
for p in me.polygons:
    v=p.vertices[0]; p.material_index=1 if v in panes else (2 if v in knobs else 0)
bpy.ops.mesh.primitive_plane_add(size=6,location=(0,0.0005,0.4),rotation=(math.radians(90),0,0))
wm=bpy.data.materials.new('wall'); wm.use_nodes=True; wm.node_tree.nodes['Principled BSDF'].inputs[0].default_value=(0.85,0.84,0.78,1); bpy.context.object.data.materials.append(wm)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera=cam
def shoot(name,c,d,ortho,size,dist,res,lens=50):
    s.render.resolution_x,s.render.resolution_y=res
    c=Vector(c); d=Vector(d).normalized(); cam.data.type='ORTHO' if ortho else 'PERSP'; cam.data.ortho_scale=size; cam.data.lens=lens
    loc=c+d*dist; f=(c-loc).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
    cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
    s.render.filepath=f'cab4/r/{tag}_{name}.png'; bpy.ops.render.render(write_still=True)
shoot('front_close',(0,-0.15,0.72),(0,-1,0),True,0.75,3,(1200,500))
shoot('oblique_low_left',(0,-0.15,0.70),(-0.55,-1,-0.45),False,0,1.3,(1200,800))   # from lower-left like IMG_3591
shoot('side_close',(-0.42,-0.15,0.74),(-1,-0.08,0),True,0.42,3,(900,600))
shoot('room_distance',(0,-0.15,0.45),(-0.45,-1,-0.55),False,0,4.2,(800,600))      # about 4 m away, looking up
