#!/usr/bin/env python3
# Diff JP vs EN FTALL.P04: quels slots (256 bytes) ont change? = glyphes modifies par Gyasuke.
JP='D:/Boulot/Freelance/game_translation/work/iso_files/jp_all/FTALL.P04'
EN='D:/Boulot/Freelance/game_translation/work/iso_files/en_all/FTALL.P04'
j=open(JP,'rb').read(); e=open(EN,'rb').read()
assert len(j)==len(e)==806400
NSLOT=3150  # 806400/256
diff=[]; same=0
for s in range(NSLOT):
    jb=j[s*256:(s+1)*256]; eb=e[s*256:(s+1)*256]
    if jb==eb: same+=1
    else: diff.append(s)
print(f"slots identiques: {same}/{NSLOT}")
print(f"slots modifies: {len(diff)}")
print(f"premiers 40 slots modifies: {diff[:40]}")
print(f"derniers 20: {diff[-20:]}")

# distribution: sont-ils contigus? gaps?
gaps=[diff[i+1]-diff[i] for i in range(len(diff)-1)]
from collections import Counter
gc=Counter(gaps)
print("\nrepartition des gaps entre slots modifies:")
for g,n in gc.most_common(10): print(f"  gap={g}: {n}x")

# le slot 311 (="!") est-il modifie?
print(f"\nslot 311 ('!') modifie? {311 in diff}")
