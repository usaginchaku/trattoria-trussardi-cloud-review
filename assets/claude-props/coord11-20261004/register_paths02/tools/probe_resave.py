# hazard probe (scratch only): open the fixed blend, save copies elsewhere with relative_remap True / False, report stored image paths
import bpy,sys,os,json,subprocess
bl,work,out=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=bl); r={}
for flag in (True,False):
    d=os.path.join(work,f'resave_remap_{flag}'); os.makedirs(d,exist_ok=True); p=os.path.join(d,'x.blend')
    bpy.ops.wm.save_as_mainfile(filepath=p,relative_remap=flag,copy=True)
    q=subprocess.run([sys.executable,'-c',f"import bpy;bpy.ops.wm.open_mainfile(filepath={p!r});print('PATHS',[i.filepath for i in bpy.data.images])"],capture_output=True,text=True).stdout
    r[f'relative_remap={flag}']=[l for l in q.splitlines() if l.startswith('PATHS')][0][6:]
json.dump({'note':'saved from a blend in directory A into directory B (one level deeper); bpy 4.3.0','result':r},open(out,'w'),indent=1); print(r)
