#!/usr/bin/env python3
# Rendre FTALL.P04 comme texture-atlas GS (16-bit index -> gris), plusieurs dims.
import struct, zlib
f=open('D:/Boulot/Freelance/game_translation/work/iso_files/jp_all/FTALL.P04','rb').read()
N=len(f)
print(f"taille {N} ({hex(N)})")

def write_png(path, W, H, gray):  # gray: list of rows of 0..255
    def chunk(t,d):
        c=t+d; return struct.pack('>I',len(d))+c+struct.pack('>I',zlib.crc32(c)&0xffffffff)
    raw=b''.join(b'\x00'+bytes(row) for row in gray)
    png=b'\x89PNG\r\n\x1a\n'
    png+=chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,0,0,0,0))
    png+=chunk(b'IDAT',zlib.compress(raw))
    png+=chunk(b'IEND',b'')
    open(path,'wb').write(png)

# 16-bit LE index -> gris (index/255*255). Essayer plusieurs dims.
cands=[(768,525),(1280,315),(640,630),(1024,393),(512,787)]
for (W,H) in cands:
    need=W*H*2
    if need>N: 
        print(f"  {W}x{H}: pas assez de data ({need}>{N})"); continue
    gray=[]
    for y in range(H):
        row=[]
        for x in range(W):
            off=(y*W+x)*2
            idx=struct.unpack_from('<H',f,off)[0]
            # index 16-bit: si c'est un CLUT index (8 bits utiles) -> gris
            g=min(255,idx if idx<256 else (idx&0xFF))
            row.append(g)
        gray.append(row)
    # mesurer l'encre (pixels non-nuls)
    ink=sum(1 for r in gray for v in r if v>0)
    p=f'D:/Boulot/Freelance/game_translation/work/atlas_{W}x{H}.png'
    write_png(p,W,H,gray)
    print(f"  {W}x{H}: encre={ink}/{W*H} ({100*ink/(W*H):.1f}%) -> {p.split('/')[-1]}")
