#!/usr/bin/env python3
# Analyse structurelle data-driven de FTALL.P04: header + variance par position de byte.
import struct
from collections import Counter
FONTP='D:/Boulot/Freelance/game_translation/work/iso_files/en_all/FTALL.P04'
f=open(FONTP,'rb').read()
N=len(f)
print(f"taille: {N} ({hex(N)})")

# facteurs de N
print("facteurs (n_slots x n_bytes):")
for s in [64,128,192,224,240,252,256,320,384,400,448,480,512,600,640]:
    if N%s==0: print(f"  {N//s} slots x {s} bytes")

# header: premieres 64 bytes
print("\npremier 64 bytes:", ' '.join(f'{b:02x}' for b in f[:64]))
# valeurs 32-bit LE au debut (candidats: nb glyphs, taille glyphe)
for i in range(0,32,4):
    v=struct.unpack_from('<I',f,i)[0]
    print(f"  word@{i}: {hex(v)} ({v})")

# variance par position de byte (hypothese 256 bytes/slot)
S=256; nslots=N//S
print(f"\n=== variance par position (hypothese {S}b/slot, {nslots} slots) ===")
print("positions a faible variance = metrics/header; forte = data")
lowvar=[]
for pos in range(S):
    vals=[f[s*S+pos] for s in range(nslots)]
    mean=sum(vals)/len(vals)
    var=sum((v-mean)**2 for v in vals)/len(vals)
    mn=min(vals); mx=max(vals)
    if var<50 and mx<128:  # petit + stable = metric
        lowvar.append((pos,round(var,1),mn,mx))
print(f"positions 'metric-like' (var<50, max<128): {len(lowvar)}")
for pos,var,mn,mx in lowvar[:30]:
    print(f"  pos {pos:3d}: var={var} range=[{mn},{mx}]")
