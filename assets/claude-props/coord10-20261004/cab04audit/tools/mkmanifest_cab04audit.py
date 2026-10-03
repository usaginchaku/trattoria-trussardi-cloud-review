# MANIFEST for cab04: PNG = width/height + sha256 of decoded RGBA; other files = sha256 of bytes. Run from the cab04audit folder.
import os,hashlib,json
from PIL import Image
def role(p):
    if p.startswith('baseline_fbx/'): return 'unchanged bpy4.3 pass-through export of C3m (+ atlas for relative reference)'
    if p.startswith('tools/'): return 'self-written code'
    if p.endswith(('.json','.csv')): return 'audit record'
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
json.dump({'work':'COORD10-CAB04BASE pass-through normal audit (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
  'base':{'C4':'claude/coord09-model-review-20261003@52eac8cfd3197d460a4d27438daaa98dc6033cec','input':'claude/coord09-model-review-20261003@8b12ec3983482e7101fdb175883fe5f1d4ab8adb:assets/claude-props/coord09-20261003/cabinet_ref/C3/C3m/'},
 'tooling':'pip bpy 4.3.0 (Cycles CPU). Blender 5.2.2 not run. Unity not touched.',
 'png_rule':'PNG entries record width, height and sha256 of decoded RGBA bytes; other files record sha256 of file bytes',
 'excluded':'no reference images, crops, screenshots, private settings or credentials','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files),'files')
