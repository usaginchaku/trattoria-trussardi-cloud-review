# MANIFEST for cab04: PNG = width/height + sha256 of decoded RGBA; other files = sha256 of bytes. Run from the cut04 folder.
import os,hashlib,json
from PIL import Image
def role(p):
    if p.startswith('uv0_corner_mapping/'): return 'PRIMARY: UV0 corner mapping / stats / targets'
    if p.startswith('CUT04_UV0/fbx/') and p.endswith('.fbx'): return 'CUT04 FBX (only UVMap arrays + Shading type code differ from CUT02)'
    if p.startswith('CUT04_UV0/fbx/'): return 'atlas image (byte copy, unchanged pixels)'
    if p.startswith('CUT04_UV0/models/'): return 'editable blend (via Blender import; use mapping/FBX for adoption)'
    if p.startswith('previews_diagnostic_only/'): return 'DIAGNOSTIC ONLY checker render (not an adopted material/texture)'
    if p.startswith('previews/'): return 'same-condition plain silver comparison render'
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
json.dump({'work':'COORD10-CUT04 fork/spoon UV0-only fix (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
     'base':{'input':'claude/coord09-model-review-20261003@91bbcff37e569b6cd630c70bbc9b64949bccb389:assets/claude-props/coord10-20261004/cut02/CUT02_A1/fbx/{07_Dinner_Fork,08_Dinner_Spoon}.fbx'},
 'tooling':'pip bpy 4.3.0 (Cycles CPU). Blender 5.2.2 not run. Unity not touched.',
 'png_rule':'PNG entries record width, height and sha256 of decoded RGBA bytes; other files record sha256 of file bytes',
 'excluded':'no reference images, crops, screenshots, private settings or credentials','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files),'files')
