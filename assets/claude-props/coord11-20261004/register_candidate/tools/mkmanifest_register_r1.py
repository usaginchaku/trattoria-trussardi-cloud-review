# MANIFEST for coord11 register_candidate: PNG = width/height + sha256 of decoded RGBA (+ file sha256); other files = sha256 of bytes.
import os,hashlib,json
from PIL import Image
def role(p):
    if p.endswith('.fbx'): return 'R1 candidate FBX (shape only; textures by basename, not embedded)'
    if p.endswith('.blend'): return 'R1 candidate blend (bpy 4.3.0; images //basename, not packed)'
    if p.startswith('previews/'): return 'input vs R1 render, same camera/light/material/render (side / oblique / table distance)'
    if p.startswith('qa/'): return 'verification record'
    if p.startswith('tools/'): return 'self-written code'
    return 'document'
files=[]
for r,_,fs in os.walk('.'):
    for f in sorted(fs):
        p=os.path.relpath(os.path.join(r,f),'.')
        if p=='MANIFEST.json': continue
        b=open(p,'rb').read(); e={'path':p,'bytes':len(b),'role':role(p),'sha256':hashlib.sha256(b).hexdigest()}
        if f.lower().endswith('.png'):
            im=Image.open(p); e.update(png_width=im.width,png_height=im.height,png_mode=im.mode,rgba_sha256=hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest())
        files.append(e)
files.sort(key=lambda e:e['path'])
json.dump({'work':'COORD11-REG01 register shape candidate R1 (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
 'base':{'input':'codex/coord11-register-input-20261004@35e983d4d5bcb676e87256353a1f0c94bc00dce8',
   'Register_FUR05.fbx_sha256':'5a430c207b5f552083399c1123fae854d54394c2bb90c62a37cddff97b953c76',
   'textures_used_unchanged':{'register_FUR05.png':'f00d89ea9ae3860e4661c5bd9117ed5ca1ebb62d94670831b68250721f727ac9','register_shadow_FUR05.png':'be3fcb596ffa71323301d8aef1f6dca612382b46a48acffbbe99c9b887206170',
     'panel_FUR05.png':'8227f597ed9f28a3db28ac841992020204f3c82a8ce14c43eff1880548b9d38f','keys_FUR05.png':'ff118202d1a70cab829132b185738379ab91494f1669f783b8383e60a7ad119e'},
   'texture_hash_kind':'decoded RGBA sha256 (512x512 RGB)','reference':'DU_ep10-4.png sha256 b9a1c3ac... (private, viewed only, not stored)'},
 'scale_note':'common scale 0.7825509309768677 kept outside the model (not baked); old contract worldScale 0.7825509458780289 not used',
 'tooling':'pip bpy 4.3.0 (Cycles CPU). Blender 5.2.2 / Unity not run.',
 'reencoding_vs_content':'input text files differ from the input MANIFEST only by git CRLF->LF; see qa/input_receipt_check.json. Output PNG previews are new renders, not re-encodes.',
 'png_rule':'PNG entries record width, height, mode, sha256 of decoded RGBA bytes and file sha256; other files record sha256 of file bytes',
 'excluded':'no reference images, crops, screenshots, input textures, private settings or credentials','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files),'files')
