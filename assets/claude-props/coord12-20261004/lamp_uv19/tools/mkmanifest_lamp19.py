import os,hashlib,json
from PIL import Image
files=[]
for r,_,fs in os.walk('.'):
    for f in sorted(fs):
        p=os.path.relpath(os.path.join(r,f),'.')
        if p=='MANIFEST.json': continue
        b=open(p,'rb').read(); top=p.split('/')[0]
        role={'A_UVFIX':'A_UVFIX output (input A = lamp_support11/revision02 ARM_C1r2; UV0 end caps only)','B_UVFIX':'B_UVFIX output (input B = lamp_plate15 PLATE_C1; UV0 end caps only)',
              'previews':'self-made diagnostic image (model only)','qa':'diagnosis / verification record','tools':'self-written code'}.get(top,'document')
        e={'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'role':role}
        if f.endswith('.png'):
            im=Image.open(p); e.update(png_width=im.width,png_height=im.height,png_mode=im.mode,rgba_sha256=hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest())
        files.append(e)
files.sort(key=lambda e:e['path'])
json.dump({'work':'COORD12-LAMP19 J-arm end-cap UV0 local repair (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
 'outputs':{'A_UVFIX':['A_UVFIX/models/StraightLamp_ARCH01_ARM_C1r2_UVFIX.blend','A_UVFIX/fbx/StraightLamp_ARCH01_ARM_C1r2_UVFIX.fbx','A_UVFIX/fbx/Shade_ARCH01.png'],
   'B_UVFIX':['B_UVFIX/models/StraightLamp_ARCH01_PLATE_C1_UVFIX.blend','B_UVFIX/fbx/StraightLamp_ARCH01_PLATE_C1_UVFIX.fbx','B_UVFIX/fbx/Shade_ARCH01.png']},
 'inputs_read_only':'see qa/input_sha_at_start.txt and qa/input_sha_at_delivery.txt (identical)','runtime':'pip bpy 4.3.0. Blender 5.2.2 / native UV2 / Unity not run.',
 'png_rule':'PNG = width, height, mode, decoded RGBA sha256, file sha256; others = file sha256','reference_pixels_included':False,'files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files))
