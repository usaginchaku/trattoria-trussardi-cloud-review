# COORD11-REG03 verification (new processes only; bpy 4.3.0).
# mode 'refs' : open <blend> placed in a different directory next to byte-copies of the 4 input PNGs; report filepath / abspath / exists /
#               pixel load / PNG sha256.   usage: refs blend.blend out.json
# mode 'dump' : dump every saved channel of the scene to a JSON fingerprint.  usage: dump blend.blend out.json
import bpy,sys,json,os,hashlib
import numpy as np
mode,bl,out=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=bl)
if mode=='refs':
    r={'blend':os.path.basename(bl),'blend_dir_is_scratch_copy':True,'images':[]}
    for i in bpy.data.images:
        a=bpy.path.abspath(i.filepath); e=os.path.exists(a)
        d={'name':i.name,'filepath':i.filepath,'relative':i.filepath.startswith('//') and not i.filepath.startswith('//..'),
           'abspath_is_in_blend_dir':os.path.dirname(os.path.abspath(a))==os.path.dirname(os.path.abspath(bl)),'exists':e}
        if e:
            d['png_sha256']=hashlib.sha256(open(a,'rb').read()).hexdigest(); i.reload(); d['loaded_size']=list(i.size); d['has_data']=bool(i.has_data)
            px=np.empty(i.size[0]*i.size[1]*4,np.float32); i.pixels.foreach_get(px); d['pixels_loaded']=int(px.size)
        r['images'].append(d)
    r['all_resolved']=all(x['exists'] and x.get('has_data') for x in r['images'])
else:
    r={'objects':[],'materials':[],'images':sorted(i.name for i in bpy.data.images),
       'scene_units':[bpy.context.scene.unit_settings.system,bpy.context.scene.unit_settings.scale_length,bpy.context.scene.unit_settings.length_unit]}
    H=lambda a:hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
    for o in sorted(bpy.data.objects,key=lambda o:o.name):
        e={'name':o.name,'type':o.type,'matrix_world':[list(map(float,row)) for row in o.matrix_world],'parent':o.parent.name if o.parent else None,
           'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'material_slots':[s.material.name if s.material else None for s in o.material_slots]}
        if o.type=='MESH':
            me=o.data; nv,nl,np_=len(me.vertices),len(me.loops),len(me.polygons)
            co=np.empty(nv*3,np.float32); me.vertices.foreach_get('co',co)
            lv=np.empty(nl,np.int32); me.loops.foreach_get('vertex_index',lv)
            ls=np.empty(np_,np.int32); me.polygons.foreach_get('loop_start',ls)
            mi=np.empty(np_,np.int32); me.polygons.foreach_get('material_index',mi)
            sm=np.empty(np_,bool); me.polygons.foreach_get('use_smooth',sm)
            cn=np.empty(nl*3,np.float32); me.corner_normals.foreach_get('vector',cn)
            ed=np.empty(len(me.edges)*2,np.int32); me.edges.foreach_get('vertices',ed)
            uvs={u.name:H(np.array([d.uv[:] for d in u.data],np.float32)) for u in me.uv_layers}
            tris=sum(len(p.vertices)-2 for p in me.polygons)
            e.update(mesh=me.name,verts=nv,loops=nl,polys=np_,tris=tris,edges=len(me.edges),co=H(co),loop_verts=H(lv),loop_start=H(ls),material_index=H(mi),
                use_smooth=H(sm),corner_normals=H(cn),edge_verts=H(ed),uv_layers=uvs,has_custom_normals=me.has_custom_normals,
                attributes=sorted((a.name,a.domain,a.data_type) for a in me.attributes),
                bbox_min=co.reshape(-1,3).min(0).tolist(),bbox_max=co.reshape(-1,3).max(0).tolist(),mesh_materials=[m.name if m else None for m in me.materials])
            # upper housing top (vertices of the shell whose z spans 0.068..~0.245, x within +-0.145)
            c=co.reshape(-1,3); sel=(np.abs(c[:,0])<=0.1451)&(c[:,2]>0.24)&(c[:,2]<0.2456)&(c[:,1]<0.176)
        r['objects'].append(e)
    for m in sorted(bpy.data.materials,key=lambda m:m.name):
        nd=[]
        if m.use_nodes:
            for n in sorted(m.node_tree.nodes,key=lambda n:n.name):
                ins={}
                for s in n.inputs:
                    v=getattr(s,'default_value',None)
                    ins[s.identifier]=[float(x) for x in v] if hasattr(v,'__len__') and not isinstance(v,str) else (float(v) if isinstance(v,(int,float)) else str(v))
                nd.append({'name':n.name,'type':n.type,'image':n.image.name if getattr(n,'image',None) else None,'inputs':ins,
                           'extra':{k:str(getattr(n,k)) for k in ('interpolation','projection','extension','blend_type') if hasattr(n,k)}})
            links=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links)
        else: links=[]
        r['materials'].append({'name':m.name,'use_nodes':m.use_nodes,'blend_method':str(getattr(m,'blend_method','')),'diffuse':list(m.diffuse_color),
            'metallic':m.metallic,'roughness':m.roughness,'nodes':nd,'links':links})
json.dump(r,open(out,'w'),indent=1); print(mode,'done',r.get('all_resolved',''))
