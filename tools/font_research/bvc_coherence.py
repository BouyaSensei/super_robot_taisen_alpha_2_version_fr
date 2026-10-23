#!/usr/bin/env python3
# Tester la coherence: decoder des phrases de dialogue normales (15-30 codes) avec le mapping frequence.
import json, re
from collections import Counter
EN='D:/Boulot/Freelance/game_translation/work/iso_files/en_all/BVC.BIN'
en=open(EN,'rb').read()
cnt=Counter()
for j in range(0,len(en)-1,2):
    c=en[j]<<8|en[j+1]
    if 0x8140<c<0x9FFF: cnt[c]+=1
PUNCT={0x88c7:'!',0x88c8:'!!'}
letters_ranked=[c for c,_ in cnt.most_common() if c not in PUNCT]
ENG='ETAOINSHRDLCUMWFGYPBVKXJQZ'
mapping={c:ENG[i] for i,c in enumerate(letters_ranked[:26])}
mapping.update(PUNCT)
def dec(codes): return ''.join(mapping.get(c,'?') for c in codes)

pairs=json.load(open('D:/Boulot/Freelance/game_translation/work/bvc_pairs.json',encoding='utf-8'))
def clean(t): return re.sub(r'[\x00-\x1f\x7f]','',t)
# phrases normales: 15-30 codes, JP lisible en kana/kanji
cands=[p for p in pairs if 15<=len(p['en'])<=30 and len(clean(p['jp']))>=8]
import random; random.seed(1)
sample=random.sample(cands,25)
for p in sample:
    codes=[int(x,16) for x in p['en']]
    print(f"JP: {clean(p['jp'])}")
    print(f"   -> '{dec(codes)}'")
    print()
