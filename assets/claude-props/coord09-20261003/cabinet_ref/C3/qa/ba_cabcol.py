# render-only colour preview (not exported): wood = existing texture x dark burnt-brown tint, panes = flat low-saturation grey-green, knobs = dull olive gold
import bpy,sys,runpy
i0=sys.argv.index('--'); blend,tag=sys.argv[i0+1:i0+3]
bpy.ops.wm.open_mainfile(filepath=blend)
o=bpy.data.objects['WallCabinet']; me=o.data
base=me.materials[0]
wood=base.copy(); wood.name='prev_wood'
nt=wood.node_tree; bsdf=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]
src=bsdf.inputs['Base Color'].links[0].from_socket if bsdf.inputs['Base Color'].links else None
mix=nt.nodes.new('ShaderNodeMix'); mix.data_type='RGBA'; mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=1.0
mix.inputs[7].default_value=(0.30,0.17,0.12,1)
if src: nt.links.new(src,mix.inputs[6])
nt.links.new(mix.outputs[2],bsdf.inputs['Base Color'])
def flat(n,c,met,rough):
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=c; b.inputs['Metallic'].default_value=met; b.inputs['Roughness'].default_value=rough; return m
pane=flat('prev_pane',(0.17,0.24,0.21,1),0.0,0.25); knob=flat('prev_knob',(0.33,0.33,0.10,1),0.8,0.45)
me.materials.clear(); me.materials.append(wood); me.materials.append(pane); me.materials.append(knob)
panes=set(list(range(1136,1328))+list(range(1866,2058))); knobs=set(list(range(1328,1402))+list(range(2058,2132)))
for p in me.polygons:
    v=p.vertices[0]; p.material_index=1 if v in panes else (2 if v in knobs else 0)
bpy.ops.wm.save_as_mainfile(filepath=f'c9/cabprev_{tag}.blend',compress=False)
