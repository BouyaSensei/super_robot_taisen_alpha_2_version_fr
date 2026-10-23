#!/usr/bin/env python3
# Solving par plaintext connu: cris de combat JP -> traduction EN (majuscules).
# Chaque code = 1 ou 2 lettres consecutives. Enumerer partitions, voter.
from collections import Counter, defaultdict

# cribs: (jp, [codes], traduction_en_majuscule_sans_ponctuation)
# ponctuation "!" separatee (0x88c7/0x88c8 deja connus)
BANG={0x88c7,0x88c8}
cribs=[
 ("行けっ",[0x974d],"GO"),
 ("落ちろ",[0x96e2,0x93e5],"FALL"),
 ("沈め",[0x8d61,0x945b],"SINK"),
 ("もらった",[0x974d,0x8ade,0x95c2,0x8d58],"GOTIT"),
 ("やらせるか",[0x8952,0x958e,0x8ca8,0x8ade,0x93de,0x8ade,0x95c2,0x8d58],"ILLDOIT"),
 ("当たれ",[0x9761,0x8ade,0x9380,0x93f8],"HIT"),   # hit it
 ("落ちろっ",[0x974d,0x8c92,0x9482,0x8ce4],"FALL"),  # var
 ("行くぞ",[0x97c6,0x8cb1,0x8aec,0x9365],"GO"),
 ("今だ",[0x97f4,0x8c96,0x9371,0x9453],"NOW"),
]

# votes: code -> Counter de lettres (chaque code peut etre 1 ou 2 lettres)
vote=defaultdict(Counter)

def partitions(s, k):
    """partitions de s en k groupes de taille 1 ou 2. yield tuples."""
    if k==0:
        if not s: yield ()
        return
    if len(s)<k or len(s)>2*k: return
    for t in (1,2):
        if t<=len(s):
            for rest in partitions(s[t:], k-1):
                yield (s[:t],)+rest

for jp,codes,en in cribs:
    # enlever les codes ponctuation de la fin
    body=[c for c in codes if c not in BANG]
    n=len(body)
    found=0
    for part in partitions(en,n):
        if len(part)!=n: continue
        ok=all(len(g) in (1,2) for g in part)
        if not ok: continue
        for c,g in zip(body,part):
            vote[c][g]+=1
        found+=1
    print(f"{jp:12s} {en:10s} ({n} codes) -> {found} partitions valides")

print("\n=== mapping emergeant (vote) ===")
for c in sorted(vote, key=lambda c:-sum(vote[c].values())):
    top=vote[c].most_common(3)
    tot=sum(vote[c].values())
    s=', '.join(f"'{g}'({n})" for g,n in top)
    print(f"  {hex(c)}: {s}   [total={tot}]")
