# label-free contact sheet: rows = views, columns = variants (order given), simple text labels drawn with PIL default font
import sys
from PIL import Image,ImageDraw
out=sys.argv[1]; cols=sys.argv[2].split(','); rows=sys.argv[3].split(','); pat=sys.argv[4]; sc=float(sys.argv[5]) if len(sys.argv)>5 else 0.5
ims=[[Image.open(pat.format(c=c,r=r)).convert('RGB') for c in cols] for r in rows]
w,h=ims[0][0].size; w2,h2=int(w*sc),int(h*sc)
S=Image.new('RGB',(w2*len(cols),(h2+22)*len(rows)),'white'); d=ImageDraw.Draw(S)
for j,r in enumerate(rows):
    for i,c in enumerate(cols):
        S.paste(ims[j][i].resize((w2,h2),Image.LANCZOS),(i*w2,j*(h2+22)+22)); d.text((i*w2+6,j*(h2+22)+5),f'{c} / {r}',fill='black')
S.save(out)
