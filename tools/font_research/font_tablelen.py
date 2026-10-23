#!/usr/bin/env python3
# Trouver la vraie fin de la table de codes (0x327186) en detectant la sortie de plage.
import struct
exe=open('D:/Boulot/Freelance/game_translation/work/iso_files/jp_all/SLPS_252.28','rb').read()
base=0x327186
# codes police attendus ~ 0x8140..0x9FFF (et placeholder 0x8140)
def in_range(v):
    return 0x8000 <= v <= 0x9FFF
codes=[]
i=0
while i < 20000:  # max 20000 entrees
    off=base+i*2
    if off+2>len(exe): break
    v=struct.unpack_from('>H',exe,off)[0]
    codes.append(v)
    i+=1
# trouver la premiere sequence de valeurs hors plage (fin de table)
end=None
for idx,v in enumerate(codes):
    if not in_range(v):
        # verifier que les 8 suivantes sont aussi hors plage (pas un trou isole)
        if all(not in_range(codes[idx+k]) for k in range(1,9)):
            end=idx; break
print(f"longueur table detectee: {end} entrees")
if end:
    print(f"  taille = {end*2} o, fin a l'offset file {base+end*2:#x}")
    NFILE=806400
    print(f"  bytes/slot si {end} slots = {NFILE/end} (reste {NFILE%end})")
# stats
from collections import Counter
real=[v for v in codes[:end] if v!=0x8140] if end else [v for v in codes if v!=0x8140]
print(f"  entrees reelles (non 0x8140): {len(real)}")
print(f"  min={min(codes[:end]):#x} max={max(codes[:end]):#x}")
# afficher les dernieres valeurs avant la fin + apres
if end:
    print("  dernieres 6 avant fin:", [hex(v) for v in codes[end-6:end]])
    print("  premieres 6 apres fin:", [hex(v) for v in codes[end:end+6]])
