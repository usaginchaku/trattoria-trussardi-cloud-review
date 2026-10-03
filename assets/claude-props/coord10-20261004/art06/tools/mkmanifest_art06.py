# MANIFEST for art06: PNG = width/height + sha256 of decoded RGBA; other files = sha256 of bytes. Run from the art06 folder.
import os,hashlib,json
from PIL import Image
def role(p):
    if p.endswith('_candidate.png'): return 'ART06 candidate F19-only FinishAtlas copy (tile5 recoloured only)'
    if p.endswith('_change_mask.png'): return 'binary change mask (0/255), nonzero only inside tile5'
    if p.startswith('previews/'): return 'F19 front baseline vs candidate render (same camera/light/render, painting = original input)'
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
json.dump({'work':'COORD10-ART06 F19 tile5 mat colour candidate (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
        'base':{'input':'codex/coord10-art05-input-20261004@03bfdaef576cb4649e9356d20f6f0c4edd5f4964','input_FinishAtlas_FUR06.png':{'sha256':'ff49ac35494a3f92011d5f2bc01137e18c270c39c6f3af4f3d49809ff6c0a715','png_width':1024,'png_height':1024,'mode':'RGB'},'input_Frame_19_FUR06.fbx_sha256':'17d2de842784ff9241f90ec6a11bbd407e8824b9e879ad1f02cd2f49b05ebd4e','record':'ART06P 779ee005 (art06review/qa/cell_stats_and_hue.txt)','reference':'DU_ep10-4.png sha256 b9a1c3ac... (private, viewed only, not stored)'},
 'tooling':'numpy/PIL for the atlas copy; pip bpy 4.3.0 (Cycles CPU) for previews only. Blender 5.2.2 / Unity not run.',
 'png_rule':'PNG entries record width, height and sha256 of decoded RGBA bytes; other files record sha256 of file bytes',
 'excluded':'no reference images, crops, screenshots, private settings or credentials','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files),'files')
