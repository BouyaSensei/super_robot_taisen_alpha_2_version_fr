#!/usr/bin/env python3
# Extraire les meilleurs cribs: segments JP lisibles recurrents + structure de speaker tags.
import json, re
from collections import Counter
pairs = json.load(open('D:/Boulot/Freelance/game_translation/work/bvc_pairs.json',encoding='utf-8'))
print(f"total paires: {len(pairs)}")

# garder les segments "propres": JP decodé en kana/kanji/symboles lisibles (pas de ctrl)
def clean_jp(t):
    # enlever les controles et garder seulement ce qui est lisible
    return re.sub(r'[\x00-\x1f\x7f]','',t)

clean=[p for p in pairs if len(clean_jp(p['jp']))>=1 and 2<=len(p['en'])<=20]
print(f"segments propres (2-20 codes): {len(clean)}")

# les textes JP les plus recurrents (noms, termes) avec leur sequence de codes EN
cnt=Counter()
jp_to_en={}
for p in clean:
    t=clean_jp(p['jp'])
    en=[int(x,16) for x in p['en']]
    # normaliser: enlever les guillemets 「」 et ponctuation japonaise pour le comptage
    key=re.sub(r'[「」…！。、？\s]','',t)
    if 1<=len(key)<=8:
        cnt[key]+=1
        jp_to_en.setdefault(key, Counter())[tuple(en)]+=1

print("\n=== textes JP recurrents (1-8 chars sans ponctuation) + codes EN ===")
for key,n in cnt.most_common(50):
    # la sequence de codes EN la plus frequente pour ce texte
    best_en, bn = jp_to_en[key].most_common(1)[0]
    print(f"{n:5d}x  '{key}'  -> {[hex(c) for c in best_en]}")
