# COORD11-REG03: rewrite only the 4 image filepaths of the R1 candidate blend to '//<basename>' and save as a new blend.
# Cause of the R1 defect: build_register_r1.py appended the object from a temporary library saved in '/', so '//name.png' was resolved
# against '/' and stored as '/name.png'. bpy 4.3.0 save_as_mainfile(relative_remap=True) also rewrites '//' paths relative to the OLD
# blend directory when saving elsewhere ('//../name.png', probed), so relative_remap=False is used here.
# usage: blender-python fix_image_paths.py -- src.blend out.blend out_log.json
import bpy,sys,json,os
src,out,logp=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=src)
before=[(i.name,i.filepath,bpy.path.abspath(i.filepath)) for i in bpy.data.images]
for i in bpy.data.images:
    b=bpy.path.basename(i.filepath)
    i.filepath_raw='x'*1000          # overwrite the fixed-size path buffer so no old bytes remain after the terminator
    i.filepath_raw='//'+b
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(out),relative_remap=False,compress=False)
after=[(i.name,i.filepath) for i in bpy.data.images]
json.dump({'before':before,'after_in_session':after,'save':'save_as_mainfile(relative_remap=False, compress=False)'},open(logp,'w'),indent=1)
print('FIX',after)
