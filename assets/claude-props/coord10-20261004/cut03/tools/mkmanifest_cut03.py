# MANIFEST for cab04: PNG = width/height + sha256 of decoded RGBA; other files = sha256 of bytes. Run from the cut03 folder.
import os,hashlib,json
from PIL import Image
def role(p):
    if p.startswith('CUT03_A2/fbx/') and p.endswith('.fbx'): return 'CUT03_A2 knife candidate mesh (FBX)'
    if p.startswith('CUT03_A2/fbx/'): return 'atlas image referenced by the FBX (byte copy, same as CUT02_A1/fbx)'
    if p.startswith('CUT03_A2/models/'): return 'CUT03_A2 knife editable blend'
    if p.startswith('previews/'): return 'same-condition comparison render (self-made only)'
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
json.dump({'work':'COORD10-CUT03 knife edge smoothing A2 (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
    'base':{'input':'claude/coord09-model-review-20261003@91bbcff37e569b6cd630c70bbc9b64949bccb389:assets/claude-props/coord10-20261004/cut02/CUT02_A1/fbx/09_Dinner_Knife.fbx (sha256 30ff436f5bf6705fd85945d3036656f517044717d420146c229391412f02fbf0)'},
 'tooling':'pip bpy 4.3.0 (Cycles CPU). Blender 5.2.2 not run. Unity not touched.',
 'png_rule':'PNG entries record width, height and sha256 of decoded RGBA bytes; other files record sha256 of file bytes',
 'excluded':'no reference images, crops, screenshots, private settings or credentials','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files),'files')
