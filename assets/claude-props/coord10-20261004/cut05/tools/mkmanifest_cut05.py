# MANIFEST for cab04: PNG = width/height + sha256 of decoded RGBA; other files = sha256 of bytes. Run from the cut05 folder.
import os,hashlib,json
from PIL import Image
def role(p):
    if p.endswith('.fbx'): return "type-code repaired copy (only Model/Shading B->C)"
    if p.endswith('.png') and p.startswith('fbx_'): return 'atlas image (byte copy of the source commit file)'
    if p.startswith('previews/'): return 'old vs repaired plain-silver render (one pair)'
    if p.startswith('qa/'): return 'verification record'
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
json.dump({'work':'COORD10-CUT05 FBX bool type-code repaired copies (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
      'base':{'CUT02':'claude/coord09-model-review-20261003@91bbcff37e569b6cd630c70bbc9b64949bccb389','CUT03':'claude/coord09-model-review-20261003@0dce019df77f5a228e5f307984b11b78665f4458'},
 'tooling':'pip bpy 4.3.0 (Cycles CPU). Blender 5.2.2 not run. Unity not touched.',
 'png_rule':'PNG entries record width, height and sha256 of decoded RGBA bytes; other files record sha256 of file bytes',
 'excluded':'no reference images, crops, screenshots, private settings or credentials','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files),'files')
