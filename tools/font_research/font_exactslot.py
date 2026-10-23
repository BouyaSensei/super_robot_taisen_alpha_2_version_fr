#!/usr/bin/env python3
# Map code->position (table BE), trouver position de codes connus, rendre le slot exact.
import struct, zlib
exe=open('D:/Boulot/Freelance/game_translation/work/iso_files/jp_all/SLPS_252.28','rb').read()
f=open('D:/Boulot/Freelance/game_translation/work/iso_files/jp_all/FTALL.P04','rb').read()
base=0x327186; NENT=3646
table=[struct.unpack_from('>H',exe,base+i*2)[0] for i in range(NENT)]
pos={}
for i,c in enumerate(table):
    if c!=0x8140 and c not in pos: pos[c]=i
print(f"codes uniques reels: {len(pos)}")

def png(path,W,H,rows,scale=12):
    def chunk(t,d):
        c=t+d;return struct.pack('>I',len(d))+c+struct.pack('>I',zlib.crc32(c)&0xffffffff)
    raw=b''.join(b'\x00'+bytes([min(255,v*scale) if v>0 else 0 for v in r]) for r in rows)
    p=b'\x89PNG\r\n\x1a\n';p+=chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,0,0,0,0))
    p+=chunk(b'IDAT',zlib.compress(raw));p+=chunk(b'IEND',b'')
    open(path,'wb').write(p)

# position de codes connus
for code,name in [(0x88c7,'!'),(0x974d,'GO?'),(0x824f,'premier code real')]:
    print(f"  {name} (0x{code:04x}) -> position/slot {pos.get(code)}")

# rendre le slot de "!" a plusieurs tailles de slot
slot=pos[0x88c7]
print(f"\nrendu du slot {slot} (!) a plusieurs tailles:")
for SS in [256,240,224,192]:
    data=f[slot*SS:(slot+1)*SS]
    # 16x16 row-major
    rows=[[data[y*16+x] if y*16+x<len(data) else 0 for x in range(16)] for y in range(16)]
    ink=sum(1 for r in rows for v in r if v>0)
    p=f'D:/Boulot/Freelance/game_translation/work/excl_slot{slot}_s{SS}.png'
    png(p,16,16,rows)
    print(f"  slotsize={SS}: encre={ink}/256 ({100*ink/256:.0f}%)")
