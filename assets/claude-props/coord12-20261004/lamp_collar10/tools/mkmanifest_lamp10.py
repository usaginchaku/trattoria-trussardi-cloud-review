# MANIFEST for lamp_collar10: PNG = width/height/mode + decoded RGBA sha256 + file sha256; others = file sha256. Run from lamp_collar10/.
import os,hashlib,json
from PIL import Image
files=[]
for r,_,fs in os.walk('.'):
    for f in sorted(fs):
        p=os.path.relpath(os.path.join(r,f),'.')
        if p=='MANIFEST.json': continue
        b=open(p,'rb').read(); e={'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),
          'role':{'previews':'model-only diagnostic render (input blend, unchanged; shade faces removed in memory only for the second)','qa':'measurement / SHA record','tools':'self-written code'}.get(p.split('/')[0],'document')}
        if f.endswith('.png'):
            im=Image.open(p); e.update(png_width=im.width,png_height=im.height,png_mode=im.mode,rgba_sha256=hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest())
        files.append(e)
files.sort(key=lambda e:e['path'])
json.dump({'work':'COORD12-LAMP10 Curved collar width (F3) check (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
 'decision':'0 models: visible collar width already ~0.35-0.37 Ws, within the reference apparent range; LAMP03 0.477 was the hidden top diameter',
 'inputs_read_only':'a61a7a959d8c5636ac38a742b15995ffefe990a5:assets/claude-props/coord12-20261004/lamp_curved07/revision02/ (blend 04e3ed97..., fbx 8779f6e4..., png ea737420...)',
 'reference':'DU_ep10-4.png (private, viewed in scratch only; pixel values read, no pixels stored)','runtime':'pip bpy 4.3.0 / numpy / PIL. Blender 5.2.2 / Unity / native UV2 not run.',
 'png_rule':'PNG = width, height, mode, decoded RGBA sha256, file sha256; others = file sha256','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files))
