# same camera / light / material / render for B0 and C1 (self-made plate only; Blender BSDF preview with the input normal map, NOT lilToon).
# views: low_front (eye slightly above the rim), side_section (ortho, half plate y<=0 kept in memory -> profile edge), oblique.
# usage: blender-python render_food24.py -- model.blend tag out_prefix cond.json
import bpy,bmesh,sys,math,json,os
from mathutils import Vector,Matrix
bl,tag,outp,cj=sys.argv[sys.argv.index('--')+1:]
def setup(section):
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(bl)); s=bpy.context.scene; o=[x for x in bpy.data.objects if x.type=='MESH'][0]
    if section:
        bm=bmesh.new(); bm.from_mesh(o.data); bmesh.ops.delete(bm,geom=[f for f in bm.faces if all(v.co.y>1e-4 for v in f.verts)],context='FACES'); bm.to_mesh(o.data); bm.free()
    s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=48; s.cycles.use_denoising=True; s.view_settings.view_transform='Standard'
    w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.8,0.8,0.78,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.7
    L=bpy.data.lights.new('k','SUN'); L.energy=2.5; L.angle=0.2; lo=bpy.data.objects.new('k',L); s.collection.objects.link(lo); lo.rotation_euler=(math.radians(50),0,math.radians(30))
    bpy.ops.mesh.primitive_plane_add(size=1.0,location=(0,0,0.012)); m=bpy.data.materials.new('table'); m.use_nodes=True; m.node_tree.nodes['Principled BSDF'].inputs[0].default_value=(0.35,0.3,0.27,1); bpy.context.object.data.materials.append(m)
    cam=bpy.data.objects.new('c',bpy.data.cameras.new('c')); s.collection.objects.link(cam); s.camera=cam; return s,cam
views={'low_front':((0,-1,0.18),False,0,0.75,85),'side_section':((0,-1,0.0),True,0.2,1.0,50),'oblique':((0.6,-0.8,0.6),False,0,0.6,60)}
cond={}
for name,(dv,ortho,size,dist,lens) in views.items():
    s,cam=setup(name=='side_section'); C=Vector((0,0,0.022)); d=Vector(dv).normalized(); loc=C+d*dist; f=(C-loc).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
    cam.data.type='ORTHO' if ortho else 'PERSP'; cam.data.ortho_scale=size; cam.data.lens=lens; cam.data.clip_start=0.005
    cam.matrix_world=Matrix.Translation(loc)@Matrix((r,u,-f)).transposed().to_4x4(); s.render.resolution_x,s.render.resolution_y=(900,500)
    s.render.filepath='%s_%s_%s.png'%(outp,tag,name); bpy.ops.render.render(write_still=True)
    cond[name]={'dir':list(dv),'ortho':ortho,'ortho_scale':size,'dist':dist,'lens':lens,'target':[0,0,0.022],'res':[900,500],'section':'faces with all verts y>1e-4 removed in memory' if name=='side_section' else None}
json.dump({'engine':'Cycles CPU 48spp denoise (pip bpy 4.3.0)','material':'FBX-imported preview BSDF + input normal map; NOT lilToon, no MatCap emulation','light':'sun 2.5 rot(50,0,30) + world 0.7','table':'plane z 0.012','views':cond},open(cj,'w'),indent=1)
