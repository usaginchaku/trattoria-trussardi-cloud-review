import os,hashlib,json
from PIL import Image
def role(p):
    if p.startswith('revision02/C1r2/'): return ('FINAL CANDIDATE C1r2','final')
    if p.startswith('revision02/'): return ('revision02 record / code / preview','final')
    if p.startswith('C1/'): return ('first candidate C1 (radial streaks from triangle-fan-dependent normals) - rejected, kept','rejected-kept')
    if p.startswith('previews/'): return ('first previews (side_section kept the near half: no cut visible) - superseded, kept','superseded-kept')
    if p.startswith('B0/'): return ('rebuilt baseline B0 (same pipeline; equals input FBX on re-import)','baseline')
    if p.startswith(('qa/','tools/')): return ('first-build record / code','kept')
    return ('document','final')
files=[]
for r,_,fs in os.walk('.'):
    for f in sorted(fs):
        p=os.path.relpath(os.path.join(r,f),'.')
        if p=='MANIFEST.json': continue
        b=open(p,'rb').read(); ro,st=role(p); e={'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'role':ro,'status':st}
        if f.endswith('.png'):
            im=Image.open(p); e.update(png_width=im.width,png_height=im.height,png_mode=im.mode,rgba_sha256=hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest())
        files.append(e)
files.sort(key=lambda e:e['path'])
json.dump({'work':'COORD12-FOOD24 pink plate upper rim candidate (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-05 JST',
 'final_candidate':['revision02/C1r2/PinkPlate_FOOD24_C1r2.blend','revision02/C1r2/PinkPlate_FOOD24_C1r2.fbx','revision02/C1r2/textures/MatCap_Ceramic_MAT01.png','revision02/C1r2/textures/Normal_CeramicMicro_MAT01.png'],
 'input':{'repo':'usaginchaku/trattoria-trussardi-cloud-review','branch':'codex/coord12-food24-input-20261005','commit':'069eb4de14c09263adbe59799576f66e96eefb80','path':'assets/codex-inputs/coord12-food24/','sha':'qa/input_sha_at_start.txt == qa/input_sha_at_delivery.txt'},
 'runtime':'pip bpy 4.3.0 (cannot open the 5.2.2 input .blend; rebuilt from native JSON + FBX). Blender 5.2.2 / native / lilToon / Unity / Bake not run.',
 'reference_pixels_included':False,'png_rule':'PNG = width, height, mode, decoded RGBA sha256, file sha256; others = file sha256','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files))
