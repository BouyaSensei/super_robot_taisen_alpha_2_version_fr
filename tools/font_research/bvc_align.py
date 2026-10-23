#!/usr/bin/env python3
# Path B: alignement JP<->EN par segments + identification de cribs.
import json
JP = 'D:/Boulot/Freelance/game_translation/work/iso_files/jp_all/BVC.BIN'
EN = 'D:/Boulot/Freelance/game_translation/work/iso_files/en_all/BVC.BIN'
jp = open(JP,'rb').read(); en = open(EN,'rb').read()
assert len(jp)==len(en), (len(jp),len(en))

def segments(b):
    """runs de bytes non-nuls -> liste de (offset, longueur)"""
    segs=[]; i=0; n=len(b)
    while i<n:
        if b[i]!=0:
            j=i
            while j<n and b[j]!=0: j+=1
            segs.append((i,j-i))
            i=j
        else:
            i+=1
    return segs

sjp=segments(jp); sen=segments(en)
print(f"segments JP={len(sjp)} EN={len(sen)}")

# verifier l'alignement: memes offsets?
same=sum(1 for a,b in zip(sjp,sen) if a[0]==b[0])
print(f"offsets identiques (zip): {same}/{min(len(sjp),len(sen))}")

# construire les paires alignees par offset
en_by_off={o:ln for o,ln in sen}
pairs=[]
for off,ln in sjp:
    eln=en_by_off.get(off)
    if eln is None: continue
    jraw=jp[off:off+ln]
    try: jtxt=jraw.decode('sjis', errors='replace')
    except: jtxt='?'
    # codes EN (2 octets)
    ecodes=[]
    for k in range(0,eln-1,2):
        c=en[off+k]<<8|en[off+k+1]
        ecodes.append(c)
    pairs.append((off,ln,jtxt,ecodes))

print(f"paires alignees: {len(pairs)}")
# sauvegarde complete
with open('D:/Boulot/Freelance/game_translation/work/bvc_pairs.json','w',encoding='utf-8') as f:
    json.dump([{"off":o,"ln":l,"jp":t,"en":[hex(c) for c in e]} for o,l,t,e in pairs], f, ensure_ascii=False, indent=0)
print("sauvegarde -> work/bvc_pairs.json")

# cribs: segments courts (1-3 codes EN) avec texte JP lisible
print("\n=== segments courts (1-2 codes EN) — meilleurs cribs ===")
short=[p for p in pairs if 1<=len(p[3])<=2]
from collections import Counter
cnt=Counter()
for o,l,t,e in short:
    cnt[tuple(e)]+=1
for codes,n in cnt.most_common(40):
    # un exemple de texte JP
    ex=[p for p in short if tuple(p[3])==codes][0]
    print(f"  {n:5d}x  codes={[hex(c) for c in codes]}  jp='{ex[2][:20]}'")
