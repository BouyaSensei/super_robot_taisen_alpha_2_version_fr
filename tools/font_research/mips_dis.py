#!/usr/bin/env python3
# Desassembler MIPS les fonctions de la vtable de l'objet police -> trouver le parser.
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32
exe = open('D:/Boulot/Freelance/game_translation/work/iso_files/jp_all/SLPS_252.28','rb').read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32)
md.detail = True

def disasm(addr, n=40):
    out=[]
    for i in md.disasm(exe[addr:addr+4*n], addr):
        out.append(f"{i.address:08x}: {i.mnemonic:8} {i.op_str}")
    return out

# cibles de la vtable
targets = [0x1251e8,0x1251f8,0x125208,0x125218,0x125248,0x125228,0x125238]
for t in targets:
    print(f"\n===== @ {t:#x} =====")
    for line in disasm(t, 24):
        print(" ", line)
