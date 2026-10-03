# MANIFEST for art04: PNG = width/height + sha256 of decoded RGBA; other files = sha256 of bytes. Run from the art04 folder.
import os,hashlib,json
from PIL import Image
def role(p):
    if p.startswith('A5/') and ('/fbx/' in p or '/models/' in p): return 'A5 Frame_22 wider wooden frame (no grooves) shape candidate'
    if p.startswith('A6/') and ('/fbx/' in p or '/models/' in p): return 'A6 Frame_22 = A5 + few shallow grooves on the front flat bands'
    if p.startswith('previews/'): return 'same-camera comparison render (self-made only)'
    if p.startswith('qa/') or os.path.basename(p).startswith('build_'): return 'verification record'
    if p.startswith('textures/'): return 'texture used by blend (byte copy of ART01 A1/A2 @5994d36)'
    if p.startswith('tools/'): return 'self-written code'
    return 'document'
files=[]
for r,_,fs in os.walk('.'):
    for f in sorted(fs):
        p=os.path.relpath(os.path.join(r,f),'.')
        if p=='MANIFEST.json': continue
        e={'path':p,'bytes':os.path.getsize(p),'role':role(p)}
        if f.lower().endswith('.png'):
            im=Image.open(p).convert('RGBA'); e.update(png_width=im.width,png_height=im.height,rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest())
        else: e['sha256']=hashlib.sha256(open(p,'rb').read()).hexdigest()
        files.append(e)
files.sort(key=lambda e:e['path'])
json.dump({'work':'COORD10-ART04 (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
 'base':{'input':'codex/coord10-art01-input-20261003@2adac80eb5036e698322f61fa48499cbf9681a17','art01':'claude/coord09-model-review-20261003@5994d367ed239cb6409717b7cd31a861e1242a82','art03':'claude/coord09-model-review-20261003@fbb4ead61b90773b32881a79bcbc847200d9b8a4'},
 'tooling':'pip bpy 4.3.0 (Cycles CPU). Blender 5.2.2 not run. Unity not touched.',
 'png_rule':'PNG entries record width, height and sha256 of decoded RGBA bytes; other files record sha256 of file bytes',
 'excluded':'no reference images, crops, screenshots, private settings or credentials','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files),'files')
