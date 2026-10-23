#!/usr/bin/env python3
# Profil structurel: pour chaque offset 0..255 dans un slot, freq non-nul sur N slots.
import struct
f=open('D:/Boulot/Freelance/game_translation/work/iso_files/jp_all/FTALL.P04','rb').read()
e=open('D:/Boulot/Freelance/game_translation/work/iso_files/en_all/FTALL.P04','rb').read()

def profile(data, slots):
    nz=[0]*256
    for s in slots:
        base=s*256
        for i in range(256):
            if data[base+i]!=0: nz[i]+=1
    return [c/len(slots) for c in nz]

# echantillonner des slots JP (remplis) et EN (modifies)
jp_slots=list(range(1,301))
en_slots=list(range(1002,1302))
pj=profile(f,jp_slots); pe=profile(e,en_slots)

print("offset: freq_non_nul_JP  freq_non_nul_EN")
# afficher les offsets avec freq extreme (toujours nul ou toujours plein)
print("--- offsets TOUJOURS non-nuls (>0.9) ---")
for i in range(256):
    if pj[i]>0.9 or pe[i]>0.9:
        print(f"  {i:3d}: JP={pj[i]:.2f} EN={pe[i]:.2f}")
print("--- offsets TOUJOURS nuls (<0.01) dans les deux ---")
cnt=0
for i in range(256):
    if pj[i]<0.01 and pe[i]<0.01:
        cnt+=1
print(f"  {cnt} offsets quasi toujours nuls")
# distribution globale
import statistics
print(f"\nJP: moyenne non-nul/offset = {statistics.mean(pj):.3f}, min={min(pj):.2f} @ {pj.index(min(pj))}, max={max(pj):.2f} @ {pj.index(max(pj))}")
print(f"EN: moyenne non-nul/offset = {statistics.mean(pe):.3f}")

# hexdump complet d'un slot JP rempli et d'un slot EN modifie pour comparer structure
def find_filled(data, start, end):
    for s in range(start,end):
        if sum(1 for i in range(256) if data[s*256+i]!=0)>30: return s
    return None
sj=find_filled(f,1,1002); se=find_filled(e,1002,3150)
print(f"\nslot JP rempli = {sj}, slot EN modifie = {se}")
for label,data,s in [("JP",f,sj),("EN",e,se)]:
    print(f"--- {label} slot {s} (256 o) ---")
    for off in range(0,256,16):
        chunk=data[s*256+off:s*256+off+16]
        print(f"  {off:3d}: {' '.join(f'{b:02x}' for b in chunk)}")
