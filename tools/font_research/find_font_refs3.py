#!/usr/bin/env python3
# Chercher lui/ori chargeant les VA REELLES des chaines police (0x42e4xx).
import struct
EXE='D:/Boulot/Freelance/game_translation/work/iso_files/jp_all/SLPS_252.28'
d=open(EXE,'rb').read(); N=len(d)
CODE_START=0x1900; CODE_END=0x35EE80; BASE=0x100000-CODE_START
def u32(off): return struct.unpack_from('<I',d,off)[0]

# VA reelles des chaines (file+0xFE700)
FONT_VAS={0x42e437:'scissor',0x42e467:'alpha',0x42e497:'bright',0x42e4ea:'ftall.p04'}
# hi candidats pour toute la zone 0x42e4xx-0x42e5xx
hi_set=set()
for va in list(FONT_VAS)+[0x42e4c0,0x42e4d0,0x42e4e0]:
    hi=va>>16; lo=va&0xffff
    hi_set.add(hi)
    if lo&0x8000: hi_set.add(hi+1)
print(f"hi a chercher: {[hex(h) for h in sorted(hi_set)]}")

hits=[]
for off in range(CODE_START,CODE_END-4,4):
    ins=u32(off)
    if (ins&0xFF000000)==0x0F000000:
        imm=ins&0xFFFF
        if imm in hi_set:
            rt=(ins>>16)&0x1F
            for k in range(1,4):
                o2=off+4*k
                if o2>=CODE_END-4: break
                i2=u32(o2); op2=(i2>>26)&0x3F; imm2=i2&0xFFFF
                if op2 in (0x33,0x09) and ((i2>>16)&0x1F)==rt:
                    # adresse reconstituee
                    addr=imm<<16|imm2
                    # addiu signed
                    if op2==0x09 and imm2&0x8000: addr=(imm<<16)+(imm2-0x10000)
                    if 0x42e000<=addr<0x42f000:
                        hits.append((BASE+off,hex(BASE+off),hex(addr)))
seen=set(); uniq=[]
for h in hits:
    if h[1] not in seen: seen.add(h[1]); uniq.append(h)
print(f"\n=== {len(uniq)} sites de code chargeant une VA dans 0x42e000-0x42f000 ===")
for f,fx,a in uniq[:50]:
    print(f"  code VA {fx} -> charge {a}")
