# MANIFEST for cab04: PNG = width/height + sha256 of decoded RGBA; other files = sha256 of bytes. Run from the art06review folder.
import os,hashlib,json
from PIL import Image
def role(p):
    if p.endswith('.png'): return 'self-model part diagram (no reference pixels)'
    if p.startswith('qa/'): return 'analysis record'
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
json.dump({'work':'COORD10-ART06P F19 mat colour source review (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
         'base':{'input':'codex/coord10-art05-input-20261004@03bfdaef576cb4649e9356d20f6f0c4edd5f4964 (Frame_17/18/19_FUR06.fbx, FinishAtlas_FUR06.png, target_mapping.json)','reference':'DU_ep10-4.png sha256 b9a1c3ac... (private, not stored)'},
 'tooling':'pip bpy 4.3.0 import/analysis and one emission diagram render. Blender 5.2.2 / Unity not run.',
 'png_rule':'PNG entries record width, height and sha256 of decoded RGBA bytes; other files record sha256 of file bytes',
 'excluded':'no reference images, crops, screenshots, private settings or credentials','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files),'files')
