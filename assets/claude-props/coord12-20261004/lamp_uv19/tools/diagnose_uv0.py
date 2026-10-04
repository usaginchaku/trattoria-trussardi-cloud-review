# independent UV0 diagnosis (read-only): per triangle UV area / 3D area in the blend (and FBX re-import), arm faces (verts >= 1070),
# end caps = faces whose 3 verts all lie in the first arm ring (1070-1085) or the last arm ring (1390-1405).
# usage: blender-python diagnose_uv0.py -- blend|fbx file out.json
import bpy,sys,json,os
import numpy as np
mode,p,out=sys.argv[sys.argv.index('--')+1:]
if mode=='blend': bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p))
else: bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=os.path.abspath(p))
o=[x for x in bpy.data.objects if x.type=='MESH'][0]; me=o.data
co=np.array([v.co[:] for v in me.vertices]); uv=np.array([d.uv[:] for d in me.uv_layers[0].data])
top=set(range(1070,1086)); wall=set(range(1390,1406)); res={'mode':mode,'file':os.path.basename(p),'uv_layer':me.uv_layers[0].name,'tris':len(me.polygons),'loops':len(me.loops),'verts':len(co),'faces':{}}
def area3(a,b,c): return 0.5*np.linalg.norm(np.cross(b-a,c-a))
def area2(a,b,c): return 0.5*abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))
groups={'top_cap':[],'wall_cap':[],'arm_side':[],'non_arm':[]}
for f in me.polygons:
    vs=set(f.vertices); L=list(f.loop_indices)
    g='top_cap' if vs<=top else 'wall_cap' if vs<=wall else 'arm_side' if min(vs)>=1070 else 'non_arm'
    groups[g].append((f.index,L,area3(*co[list(f.vertices)]),area2(*uv[L])))
for g,fs in groups.items():
    res['faces'][g]={'count':len(fs),'corners':sum(len(x[1]) for x in fs),'uv_area_zero_count':sum(1 for x in fs if x[3]<1e-14),'area3d_sum':float(sum(x[2] for x in fs)),
      'face_indices':[x[0] for x in fs] if g in ('top_cap','wall_cap') else None,'corner_indices':[l for x in fs for l in x[1]] if g in ('top_cap','wall_cap') else None,
      'const_coord':None}
for g,vs in (('top_cap',top),('wall_cap',wall)):
    c=co[sorted(vs)] if mode=='blend' else None
    if c is not None: res['faces'][g]['vertex_coord_range']=[c.min(0).tolist(),c.max(0).tolist()]
    L=res['faces'][g]['corner_indices']; res['faces'][g]['uv_range']=[uv[L].min(0).tolist(),uv[L].max(0).tolist()]
json.dump(res,open(out,'w'),indent=1)
for g,v in res['faces'].items(): print(g,v['count'],v['corners'],'uv0area=0:',v['uv_area_zero_count'],'3Darea',round(v['area3d_sum'],7),v.get('vertex_coord_range'),v.get('uv_range'))
print('cap faces',res['faces']['top_cap']['face_indices'],res['faces']['wall_cap']['face_indices'])
