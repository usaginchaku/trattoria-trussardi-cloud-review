import os,hashlib,json
from PIL import Image
files=[]
for r,_,fs in os.walk('.'):
    for f in sorted(fs):
        p=os.path.relpath(os.path.join(r,f),'.')
        if p=='MANIFEST.json': continue
        b=open(p,'rb').read(); e={'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),
          'role':{'models':'CANDIDATE PLATE_C1 blend','fbx':'CANDIDATE PLATE_C1 FBX / required image (byte copy of input)','previews':'model-only render, same camera/light/render, Y=0 wall slab','qa':'measurement / verification record','tools':'self-written code'}.get(p.split('/')[0],'document')}
        if f.endswith('.png'):
            im=Image.open(p); e.update(png_width=im.width,png_height=im.height,png_mode=im.mode,rgba_sha256=hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest())
        files.append(e)
files.sort(key=lambda e:e['path'])
json.dump({'work':'COORD12-LAMP15 Short lamp mounting-plate front size candidate (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
 'candidate':['models/StraightLamp_ARCH01_PLATE_C1.blend','fbx/StraightLamp_ARCH01_PLATE_C1.fbx','fbx/Shade_ARCH01.png'],
 'inputs_read_only':'assets/claude-props/coord12-20261004/lamp_support11/revision02/ (blend a5e6bc89..., fbx d785213f..., png ea737420...), checked at start and delivery',
 'reference':'private attachments IMG_3594 / IMG_3675 (provenance: LAMP13 revision02), read in scratch only; no pixels stored','runtime':'pip bpy 4.3.0. Blender 5.2.2 / native UV2 / Unity not run.',
 'png_rule':'PNG = width, height, mode, decoded RGBA sha256, file sha256; others = file sha256','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files))
