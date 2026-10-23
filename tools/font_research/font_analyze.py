#!/usr/bin/env python3
# Analyse structurale de FTALL.P04 — trouver l'organisation réelle (tables + bitmaps)
import sys, math

def load(path):
    with open(path, 'rb') as f:
        return f.read()

jp = load('D:/Boulot/Freelance/game_translation/work/iso_files/jp_all/FTALL.P04')
en = load('D:/Boulot/Freelance/game_translation/work/iso_files/en_all/FTALL.P04')
print(f"taille JP={len(jp)} EN={len(en)}")

# 1) hexdump de l'en-tete (300 octets)
def hxdump(b, off=0, n=300):
    print(f"--- hexdump @{off:#x} ---")
    for row in range(off, min(off+n, len(b)), 16):
        chunk = b[row:row+16]
        hexs = ' '.join(f'{c:02x}' for c in chunk)
        asc = ''.join(chr(c) if 32<=c<127 else '.' for c in chunk)
        print(f"{row:06x}  {hexs:<48}  {asc}")

hxdump(jp, 0, 256)

# 2) facteurs de la taille
N = len(jp)
print(f"\n--- facteurs de {N} ---")
for d in [16,32,48,64,80,96,112,128,160,192,224,256,288,320]:
    if N % d == 0:
        print(f"  {N} / {d} = {N//d}  (entier)")

# 3) autocorrelation normalisee pour detecter la periode des glyphes
def autocorr(b, max_lag=256):
    n = len(b)
    a = [float(x) for x in b]
    mean = sum(a)/n
    var = sum((x-mean)**2 for x in a)
    if var == 0: return []
    base = var*n
    out = []
    for lag in range(1, max_lag+1):
        s = 0.0
        # echantillonner pour la vitesse
        step = 7
        cnt = 0
        for i in range(0, n-lag, step):
            s += (a[i]-mean)*(a[i+lag]-mean)
            cnt += 1
        out.append((lag, s/(base/cnt)))
    return out

print("\n--- top autocorrelation (lags 8..256) ---")
ac = autocorr(jp, 256)
top = sorted(ac, key=lambda t: -t[1])[:20]
for lag, val in sorted(top):
    print(f"  lag {lag:3d}  corr={val:+.4f}")

# 4) runs de zeros (lignes vides de bitmaps) — structure des glyphes
print("\n--- distribution des runs de zeros dans tout le fichier ---")
runlen = {}
r = 0
for c in jp:
    if c == 0:
        r += 1
    else:
        if r > 0:
            runlen[r] = runlen.get(r,0)+1
        r = 0
if r>0: runlen[r]=runlen.get(r,0)+1
for k in sorted(runlen)[:25]:
    print(f"  run de {k:3d} zeros: x{runlen[k]}")
