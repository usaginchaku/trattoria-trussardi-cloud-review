# independent check: re-import the input FBX and the candidate FBX (bpy FBX importer, default settings) and compare shell by shell.
# usage: blender-python verify_register_r1.py -- input.fbx candidate.fbx out.json
import bpy
import sys,json,math
import numpy as np
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
fin,fc,out=sys.argv[sys.argv.index('--')+1:]
def load(p):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p)
    obs=[o for o in bpy.context.scene.objects]; o=[x for x in obs if x.type=='MESH'][0]; me=o.data
    co=np.array([v.co[:] for v in me.vertices]); par=list(range(len(co)))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for e in me.edges:
        a,b=f(e.vertices[0]),f(e.vertices[1])
        if a!=b: par[a]=b
    root=[f(i) for i in range(len(co))]; sh={}
    for i,r in enumerate(root): sh.setdefault(r,[]).append(i)
    uv=me.uv_layers[0].data; ln=[l.vector[:] for l in me.corner_normals]
    shells=[]
    for vs in sh.values():
        s=set(vs); fs=[p for p in me.polygons if p.vertices[0] in s]
        shells.append({'v':np.array(sorted(vs)),'co':co[sorted(vs)],'faces':[(p.material_index,[tuple(np.round(co[v],5)) for v in p.vertices],[tuple(uv[l].uv) for l in p.loop_indices],[ln[l] for l in p.loop_indices]) for p in fs]})
    info={'objects':[(x.name,x.type) for x in obs],'name':o.name,'loc':tuple(o.location),'rot':tuple(o.rotation_euler),'scale':tuple(o.scale),
      'verts':len(co),'tris':sum(len(p.vertices)-2 for p in me.polygons),'polys':len(me.polygons),'uv_layers':[u.name for u in me.uv_layers],
      'materials':[m.name for m in me.materials],'faces_per_slot':{i:sum(1 for p in me.polygons if p.material_index==i) for i in range(len(me.materials))},
      'bbox_min':co.min(0).round(5).tolist(),'bbox_max':co.max(0).round(5).tolist(),
      'images':sorted((i.name,bpy.path.basename(i.filepath)) for i in bpy.data.images),'non_unit_normals':int(sum(abs(Vector(n).length-1)>1e-3 for n in ln)),
      'degenerate_tris':int(sum(p.area<1e-10 for p in me.polygons)),'uv_out_of_0_1':int(sum(1 for d in uv if not(-1e-4<=d.uv.x<=1.0001 and -1e-4<=d.uv.y<=1.0001)))}
    return info,shells,o,me
A,sa,_,_=load(fin); B,sb,ob,meb=load(fc)
H=Vector((0,-0.173,0.1176)); rot=Matrix.Rotation(math.radians(3.0),4,'X'); T=Matrix.Translation(H)@rot@Matrix.Translation(-H); R3=rot.to_3x3()
def key(s): return (len(s['co']),len(s['faces']),tuple(s['co'].mean(0).round(4)))
def cmp(s,t,M=None):
    # face matching by nearest centroid (KD tree), then per-corner matching by nearest position; tolerances reported, not rounded keys
    from mathutils.kdtree import KDTree
    if len(s['faces'])!=len(t['faces']): return {'match':False,'why':'face count'}
    tf=lambda c:Vector(tuple(M@Vector(c))) if M else Vector(c)
    src=[(m,[tf(c) for c in vs],uvs,[R3@Vector(n) if M else Vector(n) for n in ns]) for m,vs,uvs,ns in s['faces']]
    kd=KDTree(len(src))
    for i,(m,P,_,_) in enumerate(src): kd.insert(sum(P,Vector())/len(P),i)
    kd.balance(); used=set(); dp=du=dn=0.0; miss=0
    for m,vs,uvs,ns in t['faces']:
        P=[Vector(c) for c in vs]; c=sum(P,Vector())/len(P)
        cand=[x for x in kd.find_n(c,4) if x[1] not in used and src[x[1]][0]==m]
        if not cand: miss+=1; continue
        i=cand[0][1]; used.add(i); m0,P0,u0,n0=src[i]
        for j,p in enumerate(P):
            o=min(range(len(P0)),key=lambda k:(P0[k]-p).length)
            dp=max(dp,(P0[o]-p).length); du=max(du,abs(u0[o][0]-uvs[j][0]),abs(u0[o][1]-uvs[j][1])); dn=max(dn,(n0[o]-Vector(ns[j])).length)
    return {'match':miss==0 and dp<2e-5,'unmatched_faces':miss,'max_pos_diff_m':dp,'max_uv_diff':du,'max_loop_normal_diff':dn}
# classify input shells
th0=math.atan2(0.2431-0.1176,0.346)
def housing(s): return abs(s['co'][:,2].min()-0.068)<1e-3 and abs(s['co'][:,2].max()-0.2454)<1e-3
def seated(s):
    c=s['co']; zs=0.1176+(c[:,1]+0.173)*math.tan(th0)
    return not housing(s) and (c[:,2]-zs).min()>-0.004 and c[:,1].max()<0.173 and c[:,1].min()>-0.173 and c[:,2].min()>0.13 and c[:,2].max()<0.2431
res={'input':A,'candidate':B,'shells':[]}
used=set(); kept_ok=moved_ok=0
for i,s in enumerate(sa):
    if housing(s): res['housing_input']={'faces':len(s['faces']),'verts':len(s['co'])}; continue
    M=T if seated(s) else None
    target=np.array(tuple(M@Vector(c)) for c in s['co']) if False else None
    cen=(np.array([tuple(M@Vector(c)) for c in s['co']]) if M else s['co']).mean(0)
    j=min((j for j in range(len(sb)) if j not in used and len(sb[j]['faces'])==len(s['faces'])),key=lambda j:np.abs(sb[j]['co'].mean(0)-cen).sum())
    used.add(j); r=cmp(s,sb[j],M); r.update(shell_in=i,kind='seated_rigid_rot3deg' if M else 'kept',faces=len(s['faces']))
    res['shells'].append(r); kept_ok+=bool(r['match'] and not M); moved_ok+=bool(r['match'] and M)
nh=[j for j in range(len(sb)) if j not in used]; assert len(nh)==1; h=sb[nh[0]]
# housing checks
hc=h['co']; res['housing_candidate']={'faces':len(h['faces']),'verts':len(hc),'bbox_min':hc.min(0).round(5).tolist(),'bbox_max':hc.max(0).round(5).tolist()}
# seated parts must lie above the new housing surface: cast rays down from each seated vertex onto the housing
bm_v=[tuple(c) for c in hc]; vid={v:k for k,v in enumerate(h['v'])}
tris=[[vid[v] for v in p.vertices] for p in meb.polygons if p.vertices[0] in set(h['v'].tolist())]
bvh=BVHTree.FromPolygons([tuple(meb.vertices[v].co) for v in h['v']],tris)
mins=[]
for r in res['shells']:
    if r['kind']!='kept' or True:
        pass
seat_gap=[];inside=0
for j in used:
    s=sb[j]
    if s['co'][:,2].min()<0.13 or s['co'][:,1].max()>0.173: continue
    for c in s['co']:
        hit=bvh.ray_cast(Vector(c)+Vector((0,0,0.0005)),Vector((0,0,-1)),0.2)
        if hit[0] is None: continue
        seat_gap.append(c[2]-hit[0].z)
    up=[bvh.ray_cast(Vector(c),Vector((0,0,1)),0.05)[0] for c in s['co']]
    inside+=sum(1 for u in up if u is not None)
res['seated_parts_min_height_above_housing_m']=round(float(min(seat_gap)),5) if seat_gap else None
res['seated_part_vertices_with_housing_above_them']=inside
res['summary']={'kept_shells_identical':kept_ok,'seated_shells_rigidly_moved_identical_uv_normals':moved_ok,'shells_compared':len(res['shells']),
 'same_object_name_transform':(A['name'],A['loc'],A['rot'],A['scale'])==(B['name'],B['loc'],B['rot'],B['scale']),
 'same_outer_bbox':A['bbox_min']==B['bbox_min'] and A['bbox_max']==B['bbox_max'],'same_materials':A['materials']==B['materials'],
 'same_uv_layers':A['uv_layers']==B['uv_layers'],'ground_z_min':B['bbox_min'][2]}
json.dump(res,open(out,'w'),indent=1,default=lambda x:x.tolist() if hasattr(x,'tolist') else str(x)); print(json.dumps(res['summary']),res['seated_parts_min_height_above_housing_m'],inside)
print('xform',A['name'],A['loc'],A['rot'],A['scale'],'|',B['name'],B['loc'],B['rot'],B['scale']); print('A',{k:A[k] for k in ('tris','faces_per_slot','bbox_min','bbox_max','non_unit_normals','degenerate_tris','uv_out_of_0_1')}); print('B',{k:B[k] for k in ('tris','faces_per_slot','bbox_min','bbox_max','non_unit_normals','degenerate_tris','uv_out_of_0_1','images')})
bad=[r for r in res['shells'] if not r['match'] or r['max_pos_diff_m']>2e-5 or r['max_uv_diff']>1e-5 or r['max_loop_normal_diff']>2e-3]; print('bad shells',bad)
