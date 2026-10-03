# self-model only (emission flat colours, Cycles): Frame_19 front view with each slot-0 part flat-coloured by the FinishAtlas tile it uses, labelled. No reference pixels.
import bpy,sys,math
from mathutils import Vector,Matrix
I,out=sys.argv[-2],sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=f'{I}/Frame_19_FUR06.fbx')
o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data; uvl=me.uv_layers[0].data
cols={1:(0.25,0.15,0.10,1),3:(0.85,0.25,0.35,1),4:(0.95,0.85,0.45,1),5:(0.25,0.55,0.95,1)}
mats={}
for t,c in cols.items():
    m=bpy.data.materials.new(f'tile{t}'); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); e=nt.nodes.new('ShaderNodeEmission'); e.inputs[0].default_value=c; o_=nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(e.outputs[0],o_.inputs[0]); mats[t]=m
pm=bpy.data.materials.new('painting'); pm.use_nodes=True; nt=pm.node_tree; nt.nodes.clear(); e=nt.nodes.new('ShaderNodeEmission'); e.inputs[0].default_value=(0.9,0.9,0.9,1); o_=nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(e.outputs[0],o_.inputs[0])
me.materials.clear()
for t in (1,3,4,5): me.materials.append(mats[t])
me.materials.append(pm)
order={1:0,3:1,4:2,5:3}
for p in me.polygons:
    U=[uvl[l].uv for l in p.loop_indices]; cu=sum(u[0] for u in U)/len(U); cv=sum(u[1] for u in U)/len(U)
    if cu>0.0 and cv<0.5 and cu<0.17: p.material_index=4; continue      # painting slot UV range (0.004-0.162, 0.3375-0.496)
    t=int((1-cv)*4)*4+int(cu*4); p.material_index=order.get(t,4)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=4; s.view_settings.view_transform='Standard'
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1)
s.render.resolution_x,s.render.resolution_y=900,680
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera=cam; cam.data.type='ORTHO'; cam.data.ortho_scale=0.5
c=Vector((0,0,0.165)); loc=c+Vector((0,-3,0)); f=(c-loc).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4()
s.render.filepath=out; bpy.ops.render.render(write_still=True)
