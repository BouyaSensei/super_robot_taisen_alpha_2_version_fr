#!/usr/bin/env python3
# Chercher le parser police par constantes magiques (taille fichier/slots/slot).
import struct
d=open('D:/Boulot/Freelance/game_translation/work/iso_files/jp_all/SLPS_252.28','rb').read()
CODE_START=0x1900; CODE_END=0x35EE80; BASE=0x100000-CODE_START
def u32(off): return struct.unpack_from('<I',d,off)[0]

# constantes a chercher comme immediats lui (hi) + ori/addiu (lo), ou word LE
MAGIC={0xC4E00:'fsize 806400',0xC4E:'nslots 3150',0x100:'slot 256',0x80:'128'}
print("=== lui/ori chargeant constantes magiques ===")
for target,name in MAGIC.items():
    hi=target>>16; lo=target&0xFFFF
    cands={hi}; 
    if lo&0x8000: cands.add(hi+1)
    hits=0
    for off in range(CODE_START,CODE_END-4,4):
        ins=u32(off)
        if (ins&0xFF000000)==0x0F000000 and (ins&0xFFFF) in cands:
            rt=(ins>>16)&0x1F; imm=ins&0xFFFF
            for k in range(1,4):
                o2=off+4*k
                if o2>=CODE_END-4: break
                i2=u32(o2); op2=(i2>>26)&0x3F; imm2=i2&0xFFFF
                if op2 in (0x33,0x09) and ((i2>>16)&0x1F)==rt:
                    addr=imm<<16|imm2
                    if op2==0x09 and imm2&0x8000: addr=(imm<<16)+(imm2-0x10000)
                    if addr==target:
                        print(f"  {name} ({hex(target)}): code VA {hex(BASE+off)} (lui r{rt},{hex(imm)})")
                        hits+=1
                        break
    if hits==0: print(f"  {name} ({hex(target)}): 0 site lui/ori direct")

# aussi word LE dans data
print("\n=== constantes magiques stockees en word LE (data) ===")
for target,name in MAGIC.items():
    pat=struct.pack('<I',target); idx=0; locs=[]
    while True:
        i=d.find(pat,idx)
        if i<0: break
        locs.append(i); idx=i+1
    print(f"  {name} ({hex(target)}): {len(locs)}x {[hex(l) for l in locs[:6]]}")
