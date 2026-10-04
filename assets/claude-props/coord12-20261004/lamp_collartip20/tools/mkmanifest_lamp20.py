import os,hashlib,json
from PIL import Image
files=[]
for r,_,fs in os.walk('.'):
    for f in sorted(fs):
        p=os.path.relpath(os.path.join(r,f),'.')
        if p=='MANIFEST.json': continue
        b=open(p,'rb').read(); e={'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),
          'role':{'models':'CANDIDATE COLLARTIP_C1 blend','fbx':'CANDIDATE COLLARTIP_C1 FBX / required image (byte copy of input)','previews':'model-only render, same camera/light/render, Y=0 wall slab','qa':'selection / measurement / verification record','tools':'self-written code'}.get(p.split('/')[0],'document')}
        if f.endswith('.png'):
            im=Image.open(p); e.update(png_width=im.width,png_height=im.height,png_mode=im.mode,rgba_sha256=hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest())
        files.append(e)
files.sort(key=lambda e:e['path'])
json.dump({'work':'COORD12-LAMP20 Short lamp lower collar taper candidate (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
 'candidate':['models/StraightLamp_ARCH01_COLLARTIP_C1.blend','fbx/StraightLamp_ARCH01_COLLARTIP_C1.fbx','fbx/Shade_ARCH01.png'],
 'input':{'commit':'0753acfbb7d628e8c6f8647f094a9f828d097933','dir':'assets/claude-props/coord12-20261004/lamp_uv19/B_UVFIX/',
   'blend':'42b0a0dd51516170c67f54afb2fc2133b7cebe67a21fdf0b969a2cf2e133f063','fbx':'e4ec1f6c6836dd7740495b4d43665a33d8b3ed3f7b2f934893d9a226baed1a71','png':'ea737420dc224da85986e9f3c3222c75e6a7ed0f9a3dd0e4ec42327f99a0a8e7'},
 'reference':'LAMP18 numeric row profiles of private IMG_3594 / IMG_3675 (no pixels stored)','runtime':'pip bpy 4.3.0. Blender 5.2.2 / native UV2 / Unity not run.',
 'png_rule':'PNG = width, height, mode, decoded RGBA sha256, file sha256; others = file sha256','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files))
