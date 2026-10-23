#!/usr/bin/env python3
# Map code->slot via table 0x327186; verifier si les codes frquents tombent dans 1002-3149
# et si l'ordre est alphabetique (bloc sequentiel).
EXE='D:/Boulot/Freelance/game_translation/work/iso_files/jp_all/SLPS_252.28'
EN='D:/Boulot/Freelance/game_translation/work/iso_files/en_all/BVC.BIN'
exe=open(EXE,'rb').read(); en=open(EN,'rb').read()
from collections import Counter
TAB=0x327186; NSLOT=3646
code2slot={}
for s in range(NSLOT):
    c=exe[TAB+s*2]<<8|exe[TAB+s*2+1]
    if c!=0x8140: code2slot[c]=s

# frequence des codes EN
cnt=Counter()
for j in range(0,len(en)-1,2):
    c=en[j]<<8|en[j+1]
    if 0x8140<c<0x9FFF: cnt[c]+=1

print("=== top 40 codes EN -> slot (dans 1002-3149?) ===")
for c,n in cnt.most_common(40):
    s=code2slot.get(c,'?')
    inblock = 'EN-BLOCK' if isinstance(s,int) and 1002<=s<=3149 else ('jp-zone' if isinstance(s,int) else '?')
    print(f"  {hex(c)}: {n:6d} -> slot {s}  [{inblock}]")

# ancre: 0x974d = "GO"
print(f"\nancre 0x974d ('GO') -> slot {code2slot.get(0x974d)}")
print(f"ancre 0x88c7 ('!')  -> slot {code2slot.get(0x88c7)}")

# si bloc sequentiel: les slots modifies 1002..3149. combien de codes y pointent?
inblock_codes=[c for c,s in code2slot.items() if 1002<=s<=3149]
print(f"\ncodes pointant vers le bloc EN (1002-3149): {len(inblock_codes)}")
# leur repartition de slot
slots_used=sorted(set(code2slot[c] for c in inblock_codes))
print(f"slots du bloc utilises: {len(slots_used)}, min={slots_used[0]}, max={slots_used[-1]}")
