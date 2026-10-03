import bpy,bmesh,sys,json,numpy as np
paths=sys.argv[sys.argv.index('--')+1:]
out={}
for p in paths:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if p.endswith('.fbx'): bpy.ops.import_scene.fbx(filepath=p)
    else: bpy.ops.wm.open_mainfile(filepath=p)
    for o in [o for o in bpy.data.objects if o.type=='MESH' and ('Basket' in o.name or 'Water' in o.name or p.endswith('.fbx'))]:
        me=o.data
        cn=np.array([c.vector[:] for c in me.corner_normals]); zl=int((np.linalg.norm(cn,axis=1)<1e-6).sum())
        bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        seen=set(); comps=[]
        for f in bm.faces:
            if f.index in seen: continue
            st=[f]; c=[]
            while st:
                x=st.pop()
                if x.index in seen: continue
                seen.add(x.index); c.append(x)
                for e in x.edges:
                    for g in e.link_faces:
                        if g.index not in seen: st.append(g)
            comps.append(c)
        neg=[]; closed=0
        for i,c in enumerate(comps):
            if all(e.is_manifold for f in c for e in f.edges):
                closed+=1
                vol=0.0
                for f in c:
                    vs=[v.co for v in f.verts]
                    for k in range(1,len(vs)-1): vol+=vs[0].dot(vs[k].cross(vs[k+1]))/6
                if vol<0:
                    cc=np.mean([v.co[:] for f in c for v in f.verts],0)
                    neg.append({'comp':i,'faces':len(c),'vol_m3':vol,'center':cc.round(4).tolist()})
        # which corners have zero normals: report face ids/locations
        zfaces=sorted({me.loops[i].vertex_index for i in np.where(np.linalg.norm(cn,axis=1)<1e-6)[0]})
        zpos=np.array([me.vertices[i].co[:] for i in zfaces]) if zfaces else np.zeros((0,3))
        out[f'{p.split("coord09-20261003/")[-1]}::{o.name}']={'zero_len_corner_normals':zl,'zero_normal_verts':len(zfaces),
            'zero_normal_z_range':[float(zpos[:,2].min()),float(zpos[:,2].max())] if len(zpos) else None,'components':len(comps),'closed':closed,'negative_volume':neg,'custom':me.has_custom_normals}
print(json.dumps(out,indent=1))
