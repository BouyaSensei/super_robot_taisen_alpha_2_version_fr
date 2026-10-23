#!/usr/bin/env python3
# Diagnostic compact: slot du code EN le plus frequent (prob. 'e') a plusieurs strides.
from collections import Counter
EXE = 'D:/Boulot/Freelance/game_translation/work/iso_files/jp_all/SLPS_252.28'
FONT_EN = 'D:/Boulot/Freelance/game_translation/work/iso_files/en_all/FTALL.P04'
BVC_EN = 'D:/Boulot/Freelance/game_translation/work/iso_files/en_all/BVC.BIN'
exe = open(EXE,'rb').read(); font_en = open(FONT_EN,'rb').read()
start=0x327186; codes=[exe[start+2*k]<<8|exe[start+2*k+1] for k in range(3646)]
bvc=open(BVC_EN,'rb').read(); cnt=Counter()
for j in range(0,len(bvc)-1,2):
    c=bvc[j]<<8|bvc[j+1]
    if 0x8140<c<0x9FFF: cnt[c]+=1
top=[c for c,_ in cnt.most_common(6)]
slots=[codes.index(c) for c in top if c in codes][:3]
print("slots a rendre:", slots, "codes:", [hex(c) for c in top[:3]])

from PIL import Image, ImageDraw
strides=list(range(208,257,4))  # 208..256
scale=3; gw,gh=40,24  # fenetre d'echantillon (octets/row = gw//8=5)
W=len(strides)*(gw*scale)+16; H=len(slots)*(gh*scale+18)+8
img=Image.new('L',(W,H),255); dr=ImageDraw.Draw(img)
for si,s in enumerate(strides):
    for gi,slot in enumerate(slots):
        base=slot*s
        if base>=len(font_en): continue
        for y in range(gh):
            bi=base+y*(gw//8)
            if bi>=len(font_en): break
            rb=font_en[bi:bi+gw//8]
            for x in range(gw):
                if rb[x//8]>>(7-(x%8))&1:
                    px=si*(gw*scale)+8+x*scale; py=gi*(gh*scale+18)+y*scale
                    img.paste(0,(px,py,px+scale,py+scale))
    dr.text((si*(gw*scale)+8, 2), str(s), fill=0)
out='D:/Boulot/Freelance/game_translation/work/font_diag.png'
img.save(out); print("PNG", out, img.size)
