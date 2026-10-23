#!/usr/bin/env python3
# Chercher le decodeur de police dans TOUS les fichiers ISO (libs .IRX surtout).
import os, struct, glob
base='D:/Boulot/Freelance/game_translation/work/iso_files/jp_all'
files=sorted(glob.glob(base+'/*'))
print(f"{len(files)} fichiers")

# constantes cibles (LE words)
targets={0xC4E00:'taille 806400',0x00C4E:'nb slots 3150',0x00100:'slot 256',0x00080:'128'}
# strings cibles
strs=[b'ftall',b'FTALL',b'.p04',b'.P04',b'scissor',b'SCISSOR',b'fontcol',b'FONTCOL',b'font']

for fp in files:
    d=open(fp,'rb').read()
    name=os.path.basename(fp)
    hits=[]
    for val,desc in targets.items():
        c=d.count(struct.pack('<I',val))
        if c and val!=0x00100:  # 0x100 trop commun
            hits.append(f"{desc}={c}")
    for s in strs:
        c=d.count(s)
        if c: hits.append(f"str'{s.decode(errors='ignore')}'={c}")
    if hits:
        print(f"  {name} ({len(d)}): {', '.join(hits)}")
