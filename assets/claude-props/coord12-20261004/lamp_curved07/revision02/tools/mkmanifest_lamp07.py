# MANIFEST for lamp_curved07 (whole folder): PNG = width/height/mode + decoded RGBA sha256 + file sha256; others = file sha256. Run from lamp_curved07/.
import os,hashlib,json
from PIL import Image
def role(p):
    if p.startswith('revision02/'):
        q=p[11:]
        if q.startswith('models/') or q.endswith('F1C1r2.fbx'): return ('FINAL CANDIDATE F1C1r2','final')
        if q=='fbx/Shade_ARCH01.png': return ('required image, byte copy of input','final')
        if q.startswith('previews/'): return ('model-only render, fixed camera/light/render, Y=0 wall slab','final')
        if q.startswith('qa/'): return ('revision02 record','final')
        if q.startswith('tools/'): return ('revision02 self-written code','final')
        return ('revision02 document','final')
    if p.startswith(('models/','fbx/','previews/')): return ('first build C1 (S=26): S-shaped step on the rising arm branch -> not a candidate; kept with creation SHA','superseded-kept')
    if p.startswith('qa/'): return ('first build C1 record (incl. input SHA at start)','superseded-kept')
    if p.startswith('tools/'): return ('self-written code used for C1 (and copied to revision02)','kept')
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
json.dump({'work':'COORD12-LAMP07 Curved L1 F1 (plate vs cup height) candidate (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
 'final_candidate':['revision02/models/CurvedLamp_ARCH01_F1C1r2.blend','revision02/fbx/CurvedLamp_ARCH01_F1C1r2.fbx','revision02/fbx/Shade_ARCH01.png'],
 'inputs_read_only':{'base_dir':'assets/claude-props/coord09-20261003/furniture/lamp_shade/L1/','models/CurvedLamp_ARCH01.blend':'e7119e11beb4adf6df7ba7d7881a593d5dab3d48edb7e79091f8af0f47f2ad01',
   'fbx/CurvedLamp_ARCH01.fbx':'12dc1ad187b8930a22f0b48606bc7264c7e718e38fa41e5e4fb8f52c5c1b324a','fbx/Shade_ARCH01.png':'ea737420dc224da85986e9f3c3222c75e6a7ed0f9a3dd0e4ec42327f99a0a8e7','checked':'at start and at delivery'},
 'reference':'DU_ep10-4.png (private, viewed only, not stored)','tooling':'pip bpy 4.3.0. Blender 5.2.2 / native UV2 / Unity not run.',
 'png_rule':'PNG = width, height, mode, decoded RGBA sha256, file sha256; others = file sha256','files':files},open('revision02/MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files))
