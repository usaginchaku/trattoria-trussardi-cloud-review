# revision02 MANIFEST (supersedes ../MANIFEST.json, which is kept unchanged). Paths are relative to lamp_standoff05/.
# MANIFEST for lamp_standoff05 (whole folder incl. old top-level outputs): PNG = width/height/mode + decoded RGBA sha256 (+ file sha256);
# other files = sha256 of bytes. Run from lamp_standoff05/.
import os,hashlib,json
from PIL import Image
def role(p):
    if p.startswith('revision02/'):
        q=p[len('revision02/'):]
        if q.startswith('models/') or q.endswith('_C1.fbx'): return ('FINAL CANDIDATE C1 (revision02)','final')
        if q=='fbx/Shade_ARCH01.png': return ('required image, byte copy of input Shade_ARCH01.png (blend //../fbx/ target)','final')
        if q.startswith('previews/'): return ('baseline L1 vs C1 model-only render, same conditions, Y=0 wall slab','final')
        if q.startswith('qa/'): return ('revision02 verification record','final')
        return ('revision02 self-written code','final')
    if p.endswith('.blend1'): return ('Blender auto backup made when the second build saved over models/; presumed to be the first-build blend by Blender save behaviour, but byte identity with the first output is NOT provable (no hash was recorded). Used read-only to measure the normal re-set problem.','existing-backup-unverified')
    if p in ('README_JA.txt','REVIEW_STATUS.txt','MANIFEST.json'): return ('top-level document from commit f0b8778, superseded by revision02/ documents; kept unchanged','superseded-doc')
    if p.startswith(('fbx/','models/','qa/','tools/')): return ('existing output of the SECOND in-place build (no normal re-set). The first-build FBX, blend, qa and build script were overwritten and are LOST (never committed). Not a candidate.','superseded-existing')
    return ('other','unknown')
files=[]
for r,_,fs in os.walk('.'):
    if r.startswith('./revision02') and False: pass
    for f in sorted(fs):
        p=os.path.relpath(os.path.join(r,f),'.')
        if p=='revision02/MANIFEST.json': continue
        b=open(p,'rb').read(); ro,st=role(p); e={'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'role':ro,'status':st}
        if f.endswith('.png'):
            im=Image.open(p); e.update(png_width=im.width,png_height=im.height,png_mode=im.mode,rgba_sha256=hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest())
        files.append(e)
files.sort(key=lambda e:e['path'])
json.dump({'work':'COORD12-LAMP05 Straight L1 wall-penetration fix candidate C1 (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
 'lost_files_not_listed':['first-build fbx/StraightLamp_ARCH01_C1.fbx','first-build models/StraightLamp_ARCH01_C1.blend (a .blend1 backup exists, identity unproven)','first-build qa/build_log.json, qa/verify_blend.json, qa/verify_fbx.json','first-build tools/build_standoff_c1.py'],
 'git_scope':'56eaa0f..f0b8778: only additions (37) under coord12-20261004/lamp_standoff05/; 0 changes elsewhere',
 'final_candidate':['revision02/models/StraightLamp_ARCH01_C1.blend','revision02/fbx/StraightLamp_ARCH01_C1.fbx','revision02/fbx/Shade_ARCH01.png'],
 'inputs_read_only':{'base_dir':'assets/claude-props/coord09-20261003/furniture/lamp_shade/L1/','models/StraightLamp_ARCH01.blend':'6ed3f6d38009fed805155955e259051c7540f0a066e73e298d460abe73c289e8',
   'fbx/StraightLamp_ARCH01.fbx':'60dfa6988538976a2206abce6dd8d865d7d174c5ddc7f535b9513a4338cdb2df','fbx/Shade_ARCH01.png':'ea737420dc224da85986e9f3c3222c75e6a7ed0f9a3dd0e4ec42327f99a0a8e7'},
 'tooling':'pip bpy 4.3.0 (Cycles CPU). Blender 5.2.2 / Unity / native UV2 not run.','png_rule':'PNG = width, height, mode, decoded RGBA sha256 and file sha256; others = file sha256',
 'excluded':'no reference pixels, Unity data, history or credentials','files':files},open('revision02/MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files))
