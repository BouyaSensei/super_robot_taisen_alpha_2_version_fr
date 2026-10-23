#!/usr/bin/env python3
# Calibration v2: table de 3646 codes fixes a 0x327186, rendu des glyphes EN aux strides propres.
import struct
from collections import Counter

EXE = 'D:/Boulot/Freelance/game_translation/work/iso_files/jp_all/SLPS_252.28'
FONT_EN = 'D:/Boulot/Freelance/game_translation/work/iso_files/en_all/FTALL.P04'
BVC_EN = 'D:/Boulot/Freelance/game_translation/work/iso_files/en_all/BVC.BIN'

exe = open(EXE,'rb').read()
font_en = open(FONT_EN,'rb').read()

# 1) table de 3646 codes fixes (0x8140 = slot vide)
start = 0x327186
N_CODES = 3646
codes = []
for k in range(N_CODES):
    c = exe[start+2*k] << 8 | exe[start+2*k+1]
    codes.append(c)
n_empty = sum(1 for c in codes if c == 0x8140)
print(f"codes: {len(codes)}, vides(0x8140): {n_empty}, remplis: {len(codes)-n_empty}")

# 2) codes frequents dans BVC.BIN EN
bvc = open(BVC_EN,'rb').read()
cnt = Counter()
for j in range(0, len(bvc)-1, 2):
    c = bvc[j] << 8 | bvc[j+1]
    if 0x8140 < c < 0x9FFF:
        cnt[c] += 1
top_codes = [c for c,_ in cnt.most_common(30)]

# 3) indices dans la table des codes frequents
def idx_of(code):
    try: return codes.index(code)
    except ValueError: return -1

targets = [(c, idx_of(c)) for c in top_codes]
valid = [(c,ix) for c,ix in targets if ix>=0][:14]
print(f"codes frequents trouves dans la table: {len(valid)}")
for c,ix in valid[:14]:
    print(f"  {hex(c)} (x{cnt[c]}) -> slot {ix}")

# 4) rendu PNG compact
from PIL import Image, ImageDraw
strides = [210, 224, 240, 256]
scale = 5
cell_w, cell_h = 32, 32
W = len(valid)*cell_w*scale + (len(valid)+1)*8
H = len(strides)*(cell_h*scale+22) + 10
img = Image.new('L', (W, H), 255)
dr = ImageDraw.Draw(img)

for si, stride in enumerate(strides):
    for gi,(c,ix) in enumerate(valid):
        base = ix*stride
        if base >= len(font_en): continue
        for y in range(cell_h):
            byte_idx = base + y*(cell_w//8)
            if byte_idx >= len(font_en): break
            row_bytes = font_en[byte_idx:byte_w] if False else font_en[byte_idx:byte_idx+cell_w//8]
            for x in range(cell_w):
                bit = row_bytes[x//8] >> (7 - (x%8)) & 1
                if bit:
                    px = gi*(cell_w*scale)+8 + x*scale
                    py = si*(cell_h*scale+22) + y*scale
                    img.paste(0, (px,py,px+scale,py+scale))
    dr.text((4, si*(cell_h*scale+22)-16), f"stride {stride}", fill=0)

out = 'D:/Boulot/Freelance/game_translation/work/font_calib.png'
img.save(out)
print("PNG:", out, img.size)
