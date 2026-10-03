# MANIFEST for art02: PNG = width/height + sha256 of decoded RGBA; other files = sha256 of bytes. Run from the art02 folder.
import os,hashlib,json
from PIL import Image
def role(p):
    if p.startswith('A1/'): return 'A1 painting atlas candidate (tile 3 only)'
    if p.startswith('A2/'): return 'A2 per-frame finish atlas candidate (one cell only)'
    if p.startswith('previews/'): return 'same-camera comparison render (self-made only)'
    if p.startswith('qa/'): return 'verification record'
    if p.startswith('tools/'): return 'self-written code'
    if 'ledger' in p: return 'reference ledger (image IDs and observations only, no images)'
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
json.dump({'work':'COORD10-ART02 upper three frames (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
  'base':{'input':'codex/coord10-art02-input-20261004@8a61591e9f94c253d69fabe16d1d54b99f75c936'},
 'tooling':'pip bpy 4.3.0 (Cycles CPU). Blender 5.2.2 not run. Unity not touched.',
 'png_rule':'PNG entries record width, height and sha256 of decoded RGBA bytes; other files record sha256 of file bytes',
 'excluded':'no reference images, crops, screenshots, private settings or credentials','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files),'files')
