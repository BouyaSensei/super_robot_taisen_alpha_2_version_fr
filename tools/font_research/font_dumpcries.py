#!/usr/bin/env python3
# Dump du dataset complet des cris de combat (JP + codes + freq) + ancres digrammes.
import json
from collections import Counter, defaultdict
pairs=json.load(open('D:/Boulot/Freelance/game_translation/work/bvc_pairs.json'))
def codes_of(p): return [int(x,16) for x in p['en'] if 0x8140<int(x,16)<0x9FFF]

byjp=defaultdict(list)
for p in pairs:
    cs=codes_of(p)
    njp=sum(1 for ch in p['jp'] if '\u3040'<=ch<='\u30ff' or '\u4e00'<=ch<='\u9fff')
    if len(cs)>=2 and 1<=njp<=8:
        byjp[p['jp']].append(cs)

out=[]
for jp,cslist in sorted(byjp.items(),key=lambda kv:-len(kv[1])):
    first=cslist[0]
    stable=all(c==first for c in cslist)
    out.append({'jp':jp,'n':len(cslist),'stable':stable,'codes':[hex(c) for c in first]})
json.dump(out,open('D:/Boulot/Freelance/game_translation/work/battle_cries.json','w'),ensure_ascii=False,indent=1)
print(f"dump: {len(out)} cris de combat uniques -> work/battle_cries.json")

# ancres de confiance (digrammes) a partir des cris monosyllabiques clairs
print("\n=== ANCRES DIGRAMMES (haute confiance) ===")
anchors={
 '0x88c7':'!',          # ponctuation, confirme partout
 '0x974d':'GO',         # 「行けっ！」= GO!  (1 code + !)
 '0x96e2':'FA','0x93e5':'LL',   # 「落ちろ！」= FALL!
 '0x8d61':'SI','0x945b':'NK',   # 「沈めっ！」= SINK!
}
for k,v in anchors.items(): print(f"  {k} = {v!r}")
json.dump(anchors,open('D:/Boulot/Freelance/game_translation/work/digraph_anchors.json','w'),indent=1)
print("ancres -> work/digraph_anchors.json")
