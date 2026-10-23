#!/usr/bin/env python3
# Mapping statistique: frequence (ponctuation exclue) -> lettres anglaises par rang.
# Validation: decodage des cris de combat JP connus.
import json, re
from collections import Counter
EN = 'D:/Boulot/Freelance/game_translation/work/iso_files/en_all/BVC.BIN'
en=open(EN,'rb').read()
cnt=Counter()
for j in range(0,len(en)-1,2):
    c=en[j]<<8|en[j+1]
    if 0x8140<c<0x9FFF: cnt[c]+=1

# ponctuation identifiee
PUNCT={0x88c7:'!', 0x88c8:'!!'}
letters_ranked=[c for c,_ in cnt.most_common() if c not in PUNCT]
# ordre de frequence anglaise (majuscules)
ENG='ETAOINSHRDLCUMWFGYPBVKXJQZ'
mapping={}
for i,c in enumerate(letters_ranked[:26]):
    mapping[c]=ENG[i]
for c,s in PUNCT.items(): mapping[c]=s

def dec(codes):
    return ''.join(mapping.get(c,'?') for c in codes)

# cris de combat connus (jp -> traduction anglaise attendue approximative)
pairs=json.load(open('D:/Boulot/Freelance/game_translation/work/bvc_pairs.json',encoding='utf-8'))
def clean(t): return re.sub(r'[\x00-\x1f\x7f「」…！。、？\s]','',t)
cribs=['行けっ','もらった','落ちろ','沈め','くらえ','邪魔だ','今だ','行くぞ','当たれ','遅い',
       'そこだ','このやろう','やらせるか','逃がすか','恨みっこなしだぞ','母艦さえ沈めれば','チッ邪気が来たか']
print("=== validation: decodage des cris de combat ===")
seen=set()
for p in pairs:
    t=clean(p['jp'])
    if t in cribs and t not in seen:
        seen.add(t)
        codes=[int(x,16) for x in p['en']]
        print(f"  {t:20s} -> '{dec(codes)}'   (codes={[hex(c) for c in codes]})")
    if len(seen)>=len(cribs): break

# aussi: top 30 codes avec mapping propose
print("\n=== top 30 codes + lettre proposee ===")
for c,n in cnt.most_common(30):
    print(f"  {hex(c)}: {n:6d}  -> '{mapping.get(c,'?')}'")
