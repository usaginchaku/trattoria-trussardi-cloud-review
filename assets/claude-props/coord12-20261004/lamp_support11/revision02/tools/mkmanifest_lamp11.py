# MANIFEST for lamp_support11 (whole folder). PNG = width/height/mode + decoded RGBA sha256 + file sha256; others = file sha256. Run from lamp_support11/.
import os,hashlib,json
from PIL import Image
def role(p):
    if p.startswith('revision02/'):
        q=p[11:]
        if q.startswith('models/') or q.endswith('ARM_C1r2.fbx'): return ('FINAL CANDIDATE ARM_C1r2','final')
        if q=='fbx/Shade_ARCH01.png': return ('required image, byte copy of input','final')
        if q.startswith('previews/'): return ('model-only render, same camera/light/render, Y=0 wall slab','final')
        return ('revision02 record/code/document','final')
    if p.startswith(('models/','fbx/')): return ('first build ARM_C1 (lamp body custom normals cleared by shade_smooth_by_angle on the selected body) - rejected, kept with creation SHA','rejected-kept')
    if p.startswith('qa/'): return ('first build record (incl. input SHA at start, failing verify)','rejected-kept')
    if p.startswith('tools/'): return ('first build code','rejected-kept')
    return ('other','unknown')
files=[]
for r,_,fs in os.walk('.'):
    for f in sorted(fs):
        p=os.path.relpath(os.path.join(r,f),'.')
        if p=='revision02/MANIFEST.json': continue
        b=open(p,'rb').read(); ro,st=role(p); e={'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'role':ro,'status':st}
        if f.endswith('.png'):
            im=Image.open(p); e.update(png_width=im.width,png_height=im.height,png_mode=im.mode,rgba_sha256=hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest())
        files.append(e)
files.sort(key=lambda e:e['path'])
json.dump({'work':'COORD12-LAMP11 Straight support arm side outline candidate (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
 'final_candidate':['revision02/models/StraightLamp_ARCH01_ARM_C1r2.blend','revision02/fbx/StraightLamp_ARCH01_ARM_C1r2.fbx','revision02/fbx/Shade_ARCH01.png'],
 'inputs_read_only':{'base_dir':'assets/claude-props/coord12-20261004/lamp_standoff05/revision02/','models/StraightLamp_ARCH01_C1.blend':'36ee6c3556a435ca58a338707082471cb3621916cac875069d69b4df3f4cf950',
   'fbx/StraightLamp_ARCH01_C1.fbx':'9c4904bdcd8c661d014068308f7bb8cf29494d02c2fc60c0d828c341dfd752d1','fbx/Shade_ARCH01.png':'ea737420dc224da85986e9f3c3222c75e6a7ed0f9a3dd0e4ec42327f99a0a8e7','checked':'at start and at delivery'},
 'reference':'IMG_3594.JPG / IMG_3675.JPG private attachments, viewed in scratch only; no photo, crop or pixel stored','runtime':'pip bpy 4.3.0. Blender 5.2.2 / native UV2 / Unity not run.',
 'png_rule':'PNG = width, height, mode, decoded RGBA sha256, file sha256; others = file sha256','files':files},open('revision02/MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files))
