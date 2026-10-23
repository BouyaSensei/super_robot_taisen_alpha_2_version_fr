#!/usr/bin/env python3
# Alignement digrammes: dictionnaire JP->EN (cris standards) + vote de coherence.
import json
from collections import Counter, defaultdict
cries=json.load(open('D:/Boulot/Freelance/game_translation/work/battle_cries.json'))
byjp={c['jp']:c for c in cries if c['stable']}

# dictionnaire JP -> EN (traductions standards SRTA2, majuscules). Mode: drop spaces, 2 chars/code.
DICT={
 '「行けっ！」':'GO',
 '「落ちろ！」「L':'FALL',   # placeholder
}
# construire par recherche de sous-chaine
def find(jp_sub):
    for jp,c in byjp.items():
        if jp_sub in jp: return c
    return None

# paires (jp_contient, en) — EN sans espaces, longueur paire de pref
PAIRS=[
 ('行けっ','GO'),
 ('落ちろ！','FALL'),
 ('沈めっ','SINK'),
 ('くらえ','TAKE THIS'),
 ('もらった','GOT IT'),
 ('当たれ','STRIKE'),
 ('遅い','TOO SLOW'),
 ('行くぞ','HERE I COME'),
 ('邪魔だ','OUT OF THE WAY'),
]

votes=defaultdict(Counter)   # code -> Counter(fragment)
examples=[]
for jp_sub,en in PAIRS:
    c=find(jp_sub)
    if not c: continue
    codes=c['codes']
    en_clean=en.replace(' ','').upper()
    # aligner: si len(en_clean) == 2*len(codes), digrammes directs
    n=len(codes)
    ok = (len(en_clean)==2*n)
    frag={}
    if ok:
        for i,code in enumerate(codes):
            frag[code]=en_clean[2*i:2*i+2]
    examples.append((jp_sub,en,codes,ok,frag))

print("=== alignements (mode digramme, espaces retires) ===")
for jp_sub,en,codes,ok,frag in examples:
    print(f"  {jp_sub!r:10} = {en!r:16} lenEN={len(en.replace(' ',''))} codes={len(codes)} {'OK' if ok else 'MISMATCH'}")
    if ok:
        for code,f in frag.items(): votes[code][f]+=1

print("\n=== vocabulaire par vote (codes vus >=2x avec accord) ===")
for code,vc in sorted(votes.items(), key=lambda kv:-len(kv[1])):
    top=vc.most_common(3)
    agree = top[0][1] if top else 0
    total=sum(vc.values())
    mark='OK' if (total>=2 and top[0][1]==total) else ('?' if total>=2 else ' ')
    print(f"  {code}: {dict(top)}  [{mark}]")
