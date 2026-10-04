# independent input audit (read-only): channel hashes (Float32 LE row-major / UInt32 LE indices), edit scope consistency,
# exact-duplicate added triangles (sorted UV2 corner Float32 bit triples), added-triangle connectivity (charts).
# usage: python audit_input.py native_mesh.json edit_scope.json out.json
import sys,json,hashlib
import numpy as np
mj,ej,out=sys.argv[1:4]; m=json.load(open(mj)); e=json.load(open(ej)); A=m['attributes']
def h(a,dt): return hashlib.sha256(np.ascontiguousarray(np.array(a,dtype=dt)).tobytes()).hexdigest()
tri=np.array(m['submeshes'][0]['triangles'],dtype=np.uint32)
res={'channel_sha_check':{}}
for k in ('positions','normals','tangents','uv0','uv2'): res['channel_sha_check'][k]=h(A[k],'<f4')==m['channelSha256'][k]
res['channel_sha_check']['indices']=h(tri,'<u4')==m['channelSha256']['indices']
uv2=np.array(A['uv2'],dtype=np.float32); E=e['editableVertexIds']; Es=set(E)
res['counts']={'verts':len(A['positions']),'tris':len(tri),'editable':len(E),'editable_range_ok':E==list(range(9039,9441))}
added=tri[4220:4408]; fixed=tri[:4220]
res['added_tris_use_only_editable_verts']=bool(np.isin(added,E).all()); res['fixed_tris_use_no_editable_verts']=bool(~np.isin(fixed,E).any())
key=lambda t:tuple(sorted(tuple(uv2[v].view(np.uint32).tolist()) for v in t))
fk={}
for i,t in enumerate(fixed): fk.setdefault(key(t),[]).append(i)
dup=[(4220+i,fk.get(key(t),[])) for i,t in enumerate(added)]
res['added_exact_duplicates']=sum(1 for _,f in dup if f); res['duplicate_matches_scope']=all(sorted(f)==sorted(x['equalUv2ExistingTriangleIds']) for (_,f),x in zip(dup,e['exactDuplicateTriangles']))
# charts among added triangles (shared vertex ids)
par=list(range(9441))
def f(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
for t in added:
    for v in t[1:]: par[f(v)]=f(t[0])
ch={}
for i,t in enumerate(added): ch.setdefault(f(t[0]),[]).append(4220+i)
res['added_charts']={'count':len(ch),'sizes':sorted(len(v) for v in ch.values())}
json.dump(res,open(out,'w'),indent=1); print(json.dumps(res))
