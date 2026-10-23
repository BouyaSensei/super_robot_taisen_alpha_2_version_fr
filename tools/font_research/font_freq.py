#!/usr/bin/env python3
# Analyse frequentielle: les codes du patch EN = substitution simple -> frequences de lettres anglaises.
from collections import Counter
BVC_EN = 'D:/Boulot/Freelance/game_translation/work/iso_files/en_all/BVC.BIN'
bvc=open(BVC_EN,'rb').read()
cnt=Counter()
for j in range(0,len(bvc)-1,2):
    c=bvc[j]<<8|bvc[j+1]
    if 0x8140<c<0x9FFF: cnt[c]+=1
total=sum(cnt.values())
print(f"total codes (plage kanji): {total}, nb codes distincts: {len(cnt)}")

# frequence anglaise standard (minuscules)
eng_freq = dict(e=.127,t=.091,a=.082,o=.075,i=.070,n=.067,s=.063,h=.061,r=.060,d=.043,
                l=.040,c=.028,u=.028,m=.024,w=.024,f=.022,g=.020,y=.020,p=.019,b=.015,
                v=.009,k=.008,j=.0015,x=.0015,q=.001,z=.0007)

print("\nTop 30 codes EN (frequence %):")
print(f"{'code':>8} {'count':>7} {'pct':>6}")
for c,n in cnt.most_common(30):
    print(f"{hex(c):>8} {n:>7} {100*n/total:5.2f}%")

# on note: la frequence totale inclut espaces/punctuation/digraphes, donc les % seront dilues
# mais le RANG des codes doit suivre e>t>a>o>i>n>s...
