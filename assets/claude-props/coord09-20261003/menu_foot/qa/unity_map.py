# Map split vertices of the current Unity mesh (MenuStand_RI03_CurrentUV2.asset) to source FBX vertex indices by position,
# then emit foot-only deltas (position delta + normal rotation) expressed in Unity mesh space. UV0/UV2 of the Unity mesh are never touched.
import bpy,re,json,sys,itertools,numpy as np
from mathutils import Vector,Matrix
from scipy.spatial import cKDTree
A='src9/assets/codex-source/coord09-menu-foot-20261003/MenuStand_RI03_CurrentUV2.asset'
t=open(A).read()
n=int(re.search(r'm_VertexCount: (\d+)',t).group(1))
hexd=re.search(r'_typelessdata: ([0-9a-f]+)',t).group(1)
raw=bytes.fromhex(hexd); stride=len(raw)//n
arr=np.frombuffer(raw,dtype='<f4').reshape(n,stride//4)
U_pos=arr[:,0:3].astype(np.float64); U_nrm=arr[:,3:6].astype(np.float64)
# source + candidate (bpy import of source FBX and candidate blend share vertex order)
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath='src9/assets/codex-source/coord09-menu-foot-20261003/MenuStand_EX01.fbx')
me=bpy.data.objects['MenuStand'].data; S=np.array([v.co[:] for v in me.vertices])
D=np.load('c9/menu_M1_delta.npy')  # candidate - source, Blender local
best=None
for perm in itertools.permutations(range(3)):
    for sg in itertools.product((1,-1),repeat=3):
        M=np.zeros((3,3))
        for i,(p,s) in enumerate(zip(perm,sg)): M[i,p]=s
        Q=S@M.T; d,_=cKDTree(Q).query(U_pos)
        if best is None or d.max()<best[0]: best=(d.max(),M)
err,M=best
Q=S@M.T; d,idx=cKDTree(Q).query(U_pos)
foot=(idx>=338)&(idx<=1453)
# normal rotation per source vertex: derive from candidate blend ring rotations -> recompute here from positions (rigid per ring): use the stored per-vertex normals
bpy.ops.wm.open_mainfile(filepath='c9/menu_M0.blend'); m0=bpy.data.objects['MenuStand'].data
bpy.ops.wm.open_mainfile(filepath='c9/menu_M1.blend'); m1=bpy.data.objects['MenuStand'].data
# per-ring rotation: fit rotation between ring vertex offsets (Kabsch) in Blender space
R_of={}
for leg0 in (338,710,1082):
    for r in range(31):
        ids=list(range(leg0+12*r,leg0+12*r+12))
        P0=S[ids]; P1=S[ids]+D[ids]
        a=P0-P0.mean(0); b=P1-P1.mean(0)
        H=a.T@b; Uu,_,Vt=np.linalg.svd(H); dd=np.sign(np.linalg.det(Vt.T@Uu.T))
        R=Vt.T@np.diag([1,1,dd])@Uu.T
        for i in ids: R_of[i]=R
rows=[]
for ui in np.where(foot)[0]:
    si=int(idx[ui]); Rb=R_of[si]; Ru=M@Rb@M.T
    dpos=M@D[si]; nn=Ru@U_nrm[ui]
    rows.append({'unity_vertex':int(ui),'source_vertex':si,'delta_pos_unity_mesh':[float(x) for x in dpos],'new_normal_unity_mesh':[float(x) for x in nn/np.linalg.norm(nn)],'normal_rotation_unity_mesh':Ru.round(9).tolist()})
info={'unity_vertex_count':n,'stride_bytes':stride,'axis_map_blender_to_unity_mesh':M.tolist(),'max_position_match_error_m':float(err),
 'unity_vertices_mapped':int(n),'unity_foot_vertices':int(foot.sum()),'source_foot_vertices_covered':int(len(set(idx[foot].tolist()))),
 'nonfoot_unity_vertices_unchanged':int((~foot).sum()),
 'note':'apply delta_pos to vertex position and normal_rotation to normal (and tangent xyz) of listed Unity vertices only; UV0/UV2/indices untouched; positions in Unity mesh local space (before Geometry child rotation / parent / worldScale)'}
json.dump({'info':info,'vertices':rows},open('c9/menu_M1_unity_foot_delta.json','w'))
print(json.dumps(info))
# --- sanity checks
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath='src9/assets/codex-source/coord09-menu-foot-20261003/MenuStand_EX01.fbx')
me=bpy.data.objects['MenuStand'].data
vn=np.zeros((len(S),3))
for l,c in zip(me.loops,me.corner_normals): vn[l.vertex_index]+=c.vector
vn/=np.linalg.norm(vn,axis=1)[:,None]
dots=np.einsum('ij,ij->i',(vn@M.T)[idx],U_nrm)
newU=U_pos.copy()
for r in rows: newU[r['unity_vertex']]+=r['delta_pos_unity_mesh']
# Unity mesh -> design world: Geometry child rot (x=90deg) then parent yaw 8deg; footprint along world X of lowest 2mm (in world up)
import math
qx=Matrix.Rotation(math.radians(90),3,'X'); 
Rg=np.array(qx); yaw=math.radians(8.0); Ry=np.array([[math.cos(yaw),0,math.sin(yaw)],[0,1,0],[-math.sin(yaw),0,math.cos(yaw)]])
def world(P): return (Ry@(Rg@P.T)).T
for nm,P in (('before',U_pos),('after',newU)):
    W=world(P); fi=np.where(foot)[0]; y=W[fi,1]; low=fi[y<=y.min()+0.002]
    print('SANITY',nm,'up-axis min',round(float(W[:,1].min()),5),'worldX footprint lowest2mm',round(float(np.ptp(W[low,0])),5))
print('SANITY normal agreement (vertex-avg source normals vs Unity normals) min dot',round(float(dots.min()),4),'median',round(float(np.median(dots)),4))
