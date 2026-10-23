#!/usr/bin/env python3
# Verifier l'hypothese "ligature/token" + commencer a batir le vocabulaire de fragments.
import json
from collections import Counter, defaultdict
pairs=json.load(open('D:/Boulot/Freelance/game_translation/work/bvc_pairs.json'))

def codes_of(p): return [int(x,16) for x in p['en'] if 0x8140<int(x,16)<0x9FFF]

# 1) ratio: longueur JP (proxy) vs nb de codes EN, sur segments courts
print("=== ratio codes vs texte (segments courts, vrais textes) ===")
ratios=[]
for p in pairs:
    jp=p['jp']
    # compter chars japonais reels dans jp (unicode)
    njp=sum(1 for ch in jp if '\u3040'<=ch<='\u30ff' or '\u4e00'<=ch<='\u9fff')
    nc=len(codes_of(p))
    if 2<=njp<=8 and 2<=nc<=12:
        ratios.append(nc/njp)
if ratios:
    import statistics
    print(f"  {len(ratios)} echantillons, ratio codes/charJP: moyenne={statistics.mean(ratios):.2f} mediane={statistics.median(ratios):.2f}")

# 2) cris de combat: segments courts finissant par 0x88c7 ("!"), groupes par texte JP identique
print("\n=== cris de combat (finissent par ! = 0x88c7), groupes par texte JP ===")
byjp=defaultdict(list)
for p in pairs:
    cs=codes_of(p)
    if len(cs)>=2 and cs[-1]==0x88c7:
        njp=sum(1 for ch in p['jp'] if '\u3040'<=ch<='\u30ff' or '\u4e00'<=ch<='\u9fff')
        if 2<=njp<=6:
            byjp[p['jp']].append(cs)
# afficher les plus frequents
for jp,cslist in sorted(byjp.items(),key=lambda kv:-len(kv[1]))[:25]:
    # codes stables?
    first=cslist[0]
    stable=all(c==first for c in cslist)
    print(f"  {jp!r:20} x{len(cslist):3d} {'OK' if stable else 'VAR'} -> {[hex(c) for c in first]}")
