import os,hashlib,json
from PIL import Image
def role(p):
    if p.startswith('previews/'): return 'self-made model render (no reference pixels); conditions in qa/render_conditions.json'
    if p.startswith('qa/'): return 'measurement / comparison record'
    if p.startswith('tools/'): return 'self-written code'
    return 'document'
files=[]
for r,_,fs in os.walk('.'):
    for f in sorted(fs):
        p=os.path.relpath(os.path.join(r,f),'.')
        if p=='MANIFEST.json': continue
        b=open(p,'rb').read(); e={'path':p,'bytes':len(b),'role':role(p)}
        if f.endswith('.png'):
            im=Image.open(p); e.update(png_width=im.width,png_height=im.height,png_mode=im.mode,rgba_sha256=hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest())
        else: e['sha256']=hashlib.sha256(b).hexdigest()
        files.append(e)
files.sort(key=lambda e:e['path'])
json.dump({'work':'COORD12-LAMP03 current L1 lamp vs reference comparison (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
 'decision':'C1 = 0 models (main difference is plate+arm vs cup vertical relation, multi-factor; arm-only remainder near reading uncertainty)',
 'inputs_read_only':{'fbx/CurvedLamp_ARCH01.fbx':'12dc1ad187b8930a22f0b48606bc7264c7e718e38fa41e5e4fb8f52c5c1b324a','fbx/StraightLamp_ARCH01.fbx':'60dfa6988538976a2206abce6dd8d865d7d174c5ddc7f535b9513a4338cdb2df',
   'fbx/Shade_ARCH01.png':'ea737420dc224da85986e9f3c3222c75e6a7ed0f9a3dd0e4ec42327f99a0a8e7','models/CurvedLamp_ARCH01.blend':'e7119e11beb4adf6df7ba7d7881a593d5dab3d48edb7e79091f8af0f47f2ad01',
   'models/StraightLamp_ARCH01.blend':'6ed3f6d38009fed805155955e259051c7540f0a066e73e298d460abe73c289e8','base_dir':'assets/claude-props/coord09-20261003/furniture/lamp_shade/L1/'},
 'reference':'DU_ep10-4.png sha256 b9a1c3ac... (private, viewed only, not stored); IMG3594 / IMG3675 not received, not viewed',
 'tooling':'pip bpy 4.3.0 (Cycles CPU). Blender 5.2.2 / Unity not run.','png_rule':'PNG = width, height, mode, sha256 of decoded RGBA; others = sha256 of bytes',
 'excluded':'no reference pixels, crops or side-by-side images with the reference','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files))
