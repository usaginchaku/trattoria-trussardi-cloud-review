# MANIFEST for cab04: PNG = width/height + sha256 of decoded RGBA; other files = sha256 of bytes. Run from the art05review folder.
import os,hashlib,json
from PIL import Image
def role(p):
    if p.startswith('tools/'): return 'self-written code'
    if p.startswith('observations'): return 'review observations (numbers/text only, no reference pixels)'
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
json.dump({'work':'COORD10-ART05P reference review (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
       'base':{'reference':'DU_ep10-4.png sha256 b9a1c3aca00965d0a360c89da9ac20027c0471940cb1baee33d093d8930544bb (private archive, not stored)'},
 'tooling':'image viewing and PIL sampling only; no Blender/Unity',
 'png_rule':'PNG entries record width, height and sha256 of decoded RGBA bytes; other files record sha256 of file bytes',
 'excluded':'no reference images, crops, screenshots, private settings or credentials','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files),'files')
