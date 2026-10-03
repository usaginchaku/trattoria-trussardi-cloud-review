# before/after dimensions by exact cross-sections (bisect at y = station): width = x extent, thickness = z extent of the section,
# z_bottom = lowest point of the section. Long axis length / bbox from vertices.
import bpy,bmesh,json,sys,numpy as np
from mathutils import Vector
pairs=json.loads(sys.argv[sys.argv.index('--')+1]); out={}
def section(me,y):
    bm=bmesh.new(); bm.from_mesh(me)
    r=bmesh.ops.bisect_plane(bm,geom=bm.verts[:]+bm.edges[:]+bm.faces[:],plane_co=Vector((0,y,0)),plane_no=Vector((0,1,0)),dist=1e-9)
    P=np.array([e.co[:] for e in r['geom_cut'] if isinstance(e,bmesh.types.BMVert)]); bm.free()
    if len(P)==0: return None
    return {'width_x':round(float(np.ptp(P[:,0])),5),'thickness_z':round(float(np.ptp(P[:,2])),5),'z_bottom':round(float(P[:,2].min()),5),'z_top':round(float(P[:,2].max()),5)}
for name,(src,cand,stations) in pairs.items():
    r={}
    for tag,p in (('source',src),('CUT02_A1',cand)):
        bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=p)
        me=[o for o in bpy.data.objects if o.type=='MESH'][0].data; co=np.array([v.co[:] for v in me.vertices])
        d={'length_y':round(float(np.ptp(co[:,1])),5),'y_range':[round(float(co[:,1].min()),5),round(float(co[:,1].max()),5)],'width_max_x':round(float(np.ptp(co[:,0])),5),'x_range':[round(float(co[:,0].min()),5),round(float(co[:,0].max()),5)],'height_z':round(float(np.ptp(co[:,2])),5),'stations':{}}
        for y in stations: d['stations'][f'{y:+.3f}']=section(me,y)
        r[tag]=d
    out[name]=r
json.dump(out,open(sys.argv[-1],'w'),indent=1)
for n,r in out.items():
    print('D',n,'len',r['source']['length_y'],r['CUT02_A1']['length_y'],'W',r['source']['width_max_x'],r['CUT02_A1']['width_max_x'],'H',r['source']['height_z'],r['CUT02_A1']['height_z'])
    for k in r['source']['stations']: print('  ',k,'src',r['source']['stations'][k],'| new',r['CUT02_A1']['stations'][k])
