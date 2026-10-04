# provenance audit of image attachments (read-only): full SHA-256, bytes, JPEG structure, EXIF/orientation, ICC description, quantization
# table, chroma subsampling, and two 64-bit perceptual hashes (aHash 8x8, dHash 9x8 on grayscale, LANCZOS) that can be recomputed
# locally on the original files (apply EXIF orientation first) to compare by Hamming distance. Outputs numbers only - no pixels.
# usage: python provenance_audit.py out.json label=path [label=path ...]
import sys,json,hashlib
from PIL import Image,ImageOps,JpegImagePlugin
def phash(im):
    g=ImageOps.exif_transpose(im).convert('L')
    a=list(g.resize((8,8),Image.LANCZOS).getdata()); m=sum(a)/64; ah=''.join('1' if v>m else '0' for v in a)
    d=list(g.resize((9,8),Image.LANCZOS).getdata()); dh=''.join('1' if d[r*9+c]>d[r*9+c+1] else '0' for r in range(8) for c in range(8))
    return '%016x'%int(ah,2),'%016x'%int(dh,2)
out=[]
for arg in sys.argv[2:]:
    lab,p=arg.split('=',1); b=open(p,'rb').read(); im=Image.open(p); ex=im.getexif()
    icc=im.info.get('icc_profile',b''); desc='Google Inc. 2016' if b'G\x00o\x00o\x00g\x00l\x00e' in icc else ('present' if icc else None)
    ah,dh=phash(im)
    out.append({'label':lab,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'format':im.format,'size':list(im.size),'mode':im.mode,'aspect':round(im.size[0]/im.size[1],4),
      'exif_tag_count':len(ex),'exif_orientation':ex.get(274),'jfif':im.info.get('jfif'),'icc_copyright_text':desc,'app_markers':[m for m,_ in im.applist],
      'quant_table0_first8':list(im.quantization[0])[:8] if hasattr(im,'quantization') else None,'chroma_subsampling':JpegImagePlugin.get_sampling(im),
      'ahash64':ah,'dhash64':dh})
json.dump(out,open(sys.argv[1],'w'),indent=1); print(json.dumps(out,indent=1))
