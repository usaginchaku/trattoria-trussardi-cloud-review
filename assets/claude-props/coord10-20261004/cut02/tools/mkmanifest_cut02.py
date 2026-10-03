# MANIFEST for cab04: PNG = width/height + sha256 of decoded RGBA; other files = sha256 of bytes. Run from the cut02 folder.
import os,hashlib,json
from PIL import Image
def role(p):
    if p.startswith('CUT02_A1/fbx/') and p.endswith('.fbx'): return 'CUT02_A1 candidate mesh (FBX)'
    if p.startswith('CUT02_A1/fbx/'): return 'atlas image referenced by the FBX (byte copy of the v02 .fbm image @7bacd4c)'
    if p.startswith('CUT02_A1/models/'): return 'CUT02_A1 editable blend'
    if p.startswith('previews/'): return 'same-condition comparison render (self-made only)'
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
json.dump({'work':'COORD10-CUT02 cutlery remake A1 (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
   'base':{'input':'dot/props-v02-20261002@7bacd4cc8d7b86b9559f9851e2ecd31dfa818571:assets/dot-props/v02/fbx/{07_Dinner_Fork,08_Dinner_Spoon,09_Dinner_Knife}.fbx'},
 'tooling':'pip bpy 4.3.0 (Cycles CPU). Blender 5.2.2 not run. Unity not touched.',
 'png_rule':'PNG entries record width, height and sha256 of decoded RGBA bytes; other files record sha256 of file bytes',
 'excluded':'no reference images, crops, screenshots, private settings or credentials','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files),'files')
