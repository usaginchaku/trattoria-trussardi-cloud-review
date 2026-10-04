# MANIFEST for coord11 register_paths02: non-PNG = sha256 of bytes (this delivery contains no PNG).
import os,hashlib,json
def role(p):
    if p.endswith('.blend'): return 'R1 blend with the 4 image filepaths fixed to //basename (all other channels identical)'
    if p.startswith('qa/'): return 'verification record'
    if p.startswith('tools/'): return 'self-written code'
    return 'document'
files=[]
for r,_,fs in os.walk('.'):
    for f in sorted(fs):
        p=os.path.relpath(os.path.join(r,f),'.')
        if p=='MANIFEST.json': continue
        b=open(p,'rb').read(); files.append({'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'role':role(p)})
files.sort(key=lambda e:e['path'])
json.dump({'work':'COORD11-REG03 register R1 blend image paths + document correction (Claude cloud)','branch':'claude/coord09-model-review-20261003','created':'2026-10-04 JST',
 'base':{'r1':'21c109ca3ac8a7a13fac6c79f5a207a51e316659:assets/claude-props/coord11-20261004/register_candidate/Register_FUR05_REG01_R1_candidate.blend',
   'r1_blend_sha256':'d3251a0e19d2d1ffec04e048984548f0b1e8c76cb74c7bfaf2855b00df81b7f2',
   'input_pngs':'35e983d4d5bcb676e87256353a1f0c94bc00dce8:assets/codex-source/coord11-register-input-20261004/ (used from scratch for verification only, not copied here)',
   'input_png_sha256':{'keys_FUR05.png':'b5e53bd8625c4e2a9f21e9931cf2b09f87946ac106d216dd7e09a99da438c95a','panel_FUR05.png':'dc093fdbb75cf58a01f8d59d42f997507c48e10d89b9481fa1329c95fe84fcf7',
     'register_FUR05.png':'5ccf95657461f800033e891fda2847956124894922de18279ba4954964493f50','register_shadow_FUR05.png':'f75a2488bc82f3528038e1ce62e65f9377a8b834c00a1937f1aab24fc7efc9dd'}},
 'tooling':'pip bpy 4.3.0. Blender 5.2.2 / Unity not run.','png_rule':'no PNG generated in this delivery',
 'excluded':'no reference images, input PNG copies, Unity data, history or credentials','files':files},open('MANIFEST.json','w'),ensure_ascii=False,indent=1)
print(len(files),'files')
