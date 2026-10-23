#!/usr/bin/env python3
# Cryptanalyse du mapping code->lettre du patch EN.
from collections import Counter
BVC_EN = 'D:/Boulot/Freelance/game_translation/work/iso_files/en_all/BVC.BIN'
bvc=open(BVC_EN,'rb').read()

# sequence de codes 2 octets; on garde les runs (on note les 00 comme separateur)
seq=[]
i=0
while i+1 < len(bvc):
    c = bvc[i]<<8 | bvc[i+1]
    if c==0: 
        seq.append(None); i+=2; continue
    if 0x8140 <= c < 0x9FFF:
        seq.append(c); i+=2
    else:
        i+=1  # byte non-aligne, on avance

# enlever les None des bords
codes=[c for c in seq if c is not None]
print(f"nb codes: {len(codes)}")

# unigrammes
uni=Counter(codes)
total=len(codes)
print("\nTop 15 unigrammes:")
for c,n in uni.most_common(15):
    print(f"  {hex(c)}: {n} ({100*n/total:.2f}%)")

# trigrammes (sequences de 3 codes consecutifs, sans None)
tri=Counter()
run=[]
for c in seq:
    if c is None:
        run=[]; continue
    run.append(c)
    if len(run)>=3:
        tri[tuple(run[-3:])]+=1
print("\nTop 20 trigrammes (sequences de 3 codes):")
for t,n in tri.most_common(20):
    print(f"  {[hex(x) for x in t]}: {n}")

# bigrammes
bi=Counter()
run=[]
for c in seq:
    if c is None:
        run=[]; continue
    run.append(c)
    if len(run)>=2:
        bi[tuple(run[-2:])]+=1
print("\nTop 20 bigrammes:")
for t,n in bi.most_common(20):
    print(f"  {[hex(x) for x in t]}: {n}")
