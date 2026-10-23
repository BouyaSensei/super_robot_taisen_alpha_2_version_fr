#!/usr/bin/env python3
# Histogramme des frequences de codes EN; trouver le "coude" texte reel vs bruit binaire.
from collections import Counter
EN='D:/Boulot/Freelance/game_translation/work/iso_files/en_all/BVC.BIN'
en=open(EN,'rb').read()
cnt=Counter()
for j in range(0,len(en)-1,2):
    c=en[j]<<8|en[j+1]
    if 0x8140<c<0x9FFF: cnt[c]+=1
total=sum(cnt.values())
print(f"codes distincts: {len(cnt)}, occurrences totales: {total}")

# trier par frequence dec; afficher le profil
ranked=cnt.most_common()
print("\n=== profil de frequence (top 60) ===")
for i,(c,n) in enumerate(ranked[:60]):
    bar='#'*min(60,n//200)
    print(f"  {i+1:3d}. {hex(c)}: {n:5d} ({100*n/total:4.1f}%) {bar}")

# le coude: ou la frequence chute brutalement?
print("\n=== recherche du coude (chute >5x entre rangs consecutifs) ===")
for i in range(1,len(ranked)):
    prev=ranked[i-1][1]; cur=ranked[i][1]
    if prev>20 and prev/cur>4:
        print(f"  coude apres rang {i}: {hex(ranked[i-1][0])}({prev}) -> {hex(ranked[i][0])}({cur})")
        break

# combien de codes apparaissent >=50, >=20, >=10 fois?
for thr in [100,50,30,20,10,5]:
    n=sum(1 for c,v in cnt.items() if v>=thr)
    cov=sum(v for c,v in cnt.items() if v>=thr)/total*100
    print(f"  codes >= {thr:3d}x: {n:4d}  (couvre {cov:.1f}% des occurrences)")
