# per-ring arm normal comparison (blend, new process): |n_C1 - n_base| and |n_C1 - R(ring) n_base| where R(ring) is the X-axis rotation
# applied to that ring by the build (0 for kept rings). Also ring-centre Y change (reach check).
# usage: blender-python arm_normal_rings.py -- base.blend c1.blend build_log.json out.json
import bpy,sys,json,math,subprocess
import numpy as np
b,c,bl,out=sys.argv[sys.argv.index('--')+1:]
def dump(p):
    import tempfile; tf=tempfile.mktemp(suffix='.npz')
    code=f"""
import bpy,numpy as np
bpy.ops.wm.open_mainfile(filepath={p!r}); me=bpy.data.objects['CurvedLamp'].data
ln=np.empty(len(me.loops)*3); me.corner_normals.foreach_get('vector',ln); lv=np.empty(len(me.loops),np.int64); me.loops.foreach_get('vertex_index',lv)
co=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',co)
np.savez({tf!r},ln=ln.reshape(-1,3),lv=lv,co=co.reshape(-1,3))
"""
    subprocess.run([sys.executable,'-c',code],check=True,capture_output=True); f=tf; d=dict(np.load(f)); import os; os.remove(f); return d
A=dump(b); B=dump(c)
CA=A['co'][96:588].reshape(41,12,3).mean(1); CB=B['co'][96:588].reshape(41,12,3).mean(1)
def ang(C): t=np.gradient(C[:,1:],axis=0); return np.arctan2(t[:,1],t[:,0])
rot=ang(CB)-ang(CA); rows=[]
for i in range(41):
    L=(A['lv']>=96+12*i)&(A['lv']<96+12*(i+1)); na=A['ln'][L]; nb=B['ln'][L]; a=rot[i]
    R=np.array([[1,0,0],[0,math.cos(a),-math.sin(a)],[0,math.sin(a),math.cos(a)]]); nr=na@R.T
    rows.append({'ring':i,'centre_dy':float(CB[i,1]-CA[i,1]),'centre_dz':float(CB[i,2]-CA[i,2]),'rotation_deg':float(math.degrees(a)),
                 'normal_max_abs_vs_base':float(np.abs(nb-na).max()),'normal_max_abs_vs_rotated_base':float(np.abs(nb-nr).max()),'max_angle_vs_rotated_base_deg':float(np.degrees(np.arccos(np.clip((nb*nr).sum(1)/np.linalg.norm(nb,axis=1)/np.linalg.norm(nr,axis=1),-1,1))).max())})
json.dump({'note':'arm = 41 rings x 12 verts; ring 0 at the plate, ring 40 inside the collar; loops counted by vertex ring','rings':rows},open(out,'w'),indent=1)
for r in rows: print(r['ring'],round(r['centre_dy'],7),round(r['centre_dz'],5),round(r['rotation_deg'],2),round(r['normal_max_abs_vs_base'],5),round(r['normal_max_abs_vs_rotated_base'],5),round(r['max_angle_vs_rotated_base_deg'],3))
