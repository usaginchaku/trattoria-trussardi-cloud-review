# loop-normal / UV difference detail (blend files, new process each open):
#  noise   : baseline blend opened twice (reload-only difference)
#  r2      : baseline vs revision02 C1 blend
#  first   : baseline vs ../models/StraightLamp_ARCH01_C1.blend1 (Blender's automatic backup of the FIRST in-folder build, which re-set
#            custom normals with normals_split_custom_set; read-only evidence)
# per pair: max |diff| per shell, count of loops above thresholds, material slot and component (x/y/z) of the max.
# usage: blender-python normal_diff_detail_r2.py -- baseline.blend r2.blend first.blend1 out.json
import bpy,subprocess,sys,json
import numpy as np
base,r2,first,out=sys.argv[sys.argv.index('--')+1:]
def dump(p):
    code=f"""
import bpy,numpy as np,sys
bpy.ops.wm.open_mainfile(filepath={p!r}); me=[o for o in bpy.data.objects if o.type=='MESH'][0].data
ln=np.empty(len(me.loops)*3,np.float32); me.corner_normals.foreach_get('vector',ln)
uv=np.empty(len(me.loops)*2,np.float32); me.uv_layers[0].data.foreach_get('uv',uv)
lv=np.empty(len(me.loops),np.int32); me.loops.foreach_get('vertex_index',lv)
mi=np.array([p.material_index for p in me.polygons for _ in p.loop_indices],np.int32)
np.savez('/dev/stdout' if False else {p!r}+'.npz_tmp',ln=ln,uv=uv,lv=lv,mi=mi)
"""
    import tempfile,os
    t=tempfile.mktemp(suffix='.npz'); code=code.replace(repr(p)+"+'.npz_tmp'",repr(t))
    subprocess.run([sys.executable,'-c',code],check=True,capture_output=True)
    d=dict(np.load(t)); os.remove(t); return d
SH=[('plate',0,96),('arm',96,192),('collar',192,314),('shade',314,1020),('diffuser',1020,1166)]
def cmp(A,B):
    dn=np.abs(A['ln']-B['ln']).reshape(-1,3); du=np.abs(A['uv']-B['uv']).reshape(-1,2); r={}
    for nm,a,b in SH:
        m=(A['lv']>=a)&(A['lv']<b); d=dn[m]; i=int(np.argmax(d.max(1))) if m.any() else 0
        r[nm]={'loops':int(m.sum()),'material_slot':sorted(set(A['mi'][m].tolist())),'normal_max_abs':float(d.max()),'max_component':'xyz'[int(np.argmax(d[i]))],
               'loops_gt_1e-6':int((d.max(1)>1e-6).sum()),'loops_gt_1e-5':int((d.max(1)>1e-5).sum()),'loops_gt_1e-4':int((d.max(1)>1e-4).sum()),'uv_max_abs':float(du[m].max())}
    return r
Bs=dump(base); Bs2=dump(base); R2=dump(r2); F=dump(first)
res={'note':'absolute differences of corner (loop) normals and UV0 between saved blends; plate/arm/collar/shade/diffuser by vertex index range',
 'reload_noise_baseline_vs_baseline':cmp(Bs,Bs2),'baseline_vs_revision02':cmp(Bs,R2),'baseline_vs_first_build_with_normal_reset(.blend1)':cmp(Bs,F)}
json.dump(res,open(out,'w'),indent=1)
for k in list(res)[1:]: print(k,{n:(v['normal_max_abs'],v['loops_gt_1e-5'],v['uv_max_abs']) for n,v in res[k].items()})
