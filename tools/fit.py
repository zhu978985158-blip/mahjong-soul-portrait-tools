from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
root=Path(__file__).resolve().parents[1]; r=root/'output'; r.mkdir(parents=True,exist_ok=True)
im=Image.open(root/'inputs/replacement.png').convert('RGBA')
w,h=872,1305
s=(w-16)/im.width;tx=8.;ty=24.
# Exactly the same affine scale on both axes; interpolate premultiplied color to avoid RGB halos.
canvas=im.convert('RGBa').transform((w,h),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),resample=Image.Resampling.BICUBIC).convert('RGBA')
canvas.save(r/'full_872x1305.png')
assert canvas.size==(872,1305)
# Four source corners fit within canvas; no cropped source content.
assert tx>=0 and ty>=0 and tx+im.width*s<=w and ty+im.height*s<=h
assert np.asarray(canvas)[:,:7,3].max()==0 and np.asarray(canvas)[:,-7:,3].max()==0
for name,col in [('黑底','#15151d'),('白底','#ffffff'),('灰底','#6b6b6b')]:
 b=Image.new('RGBA',canvas.size,col);b.alpha_composite(canvas);b.convert('RGB').save(r/(name+'.png'))
preview=Image.new('RGB',(1173,1000))
for i,col in enumerate(['#15151d','#ffffff','#6b6b6b']):
 b=Image.new('RGBA',(391,1000),col);p=canvas.copy();p.thumbnail((381,970));b.alpha_composite(p,((391-p.width)//2,15));preview.paste(b.convert('RGB'),(391*i,0))
preview.save(r/'三背景预览.jpg',quality=96)
# Full resolution edge diagnostics on both light and dark backgrounds.
boxes=[('发丝',(430,20,690,300)),('手与剑',(390,325,680,535)),('光效',(560,550,865,905))]
for name,box in boxes:
 q=canvas.crop(box);ww,hh=q.size;b=Image.new('RGB',(ww*2,hh))
 for i,col in enumerate(['#10101a','#ffffff']):
  t=Image.new('RGBA',q.size,col);t.alpha_composite(q);b.paste(t.convert('RGB'),(i*ww,0))
 b.resize((ww*4,hh*2),Image.Resampling.NEAREST).save(r/(name+'_200%检查.png'))
(r/'对齐记录.json').write_text(json.dumps({'canvas':[w,h],'source':str(root/'inputs/replacement.png'),'source_size':list(im.size),'scale_x':s,'scale_y':s,'offset':[tx,ty],'all_source_corners_inside':True,'note':'Complete design fitted without squeezing or new cropping; overall scale smaller than prior cropped candidate. No extra shadow added.'},ensure_ascii=False,indent=2))
print('uniform scale',s,'alpha bbox',canvas.getbbox())
