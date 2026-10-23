#!/usr/bin/env python3
"""Appliquer un lot de traductions FR au worklist unique, valider les budgets,
et propager aux occurrences.

Usage:
    python tools/apply_translations.py <fichier_dico.py> [--propagate]

Le fichier dico définit une variable `TR` : dict {jp_normalise: francais}.
- jp_normalise : le texte JP SANS espaces fullwidth (U+3000) ni ASCII,
  c'est-à-dire la forme « pure » de la source. Le matching est fait par
  normalisation (strip ASCII + U+3000), donc on peut écrire la clé sans se
  soucier des \n / espaces fullwidth du CSV.
- francais : le texte FR, avec \n pour les sauts de ligne. Chaque ligne doit
  faire <= max_bytes//2 caractères (budget). Les accents sont remplacés par
  la lettre de base tant que la police n'a pas de glyphes accentués.

Exemple de dico (lot3.py):
    TR = {
      "「行くぞ！」": "Allez",
      "「敵だ…！\n構わず突っ込め！」": "C'est l'ennemi...\nFonce sans te retenir !",
    }
"""
import csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNIQ = ROOT / "strings" / "ja" / "unique.csv"
FULL = ROOT / "strings" / "ja" / "strings.csv"


def norm(s: str) -> str:
    """Forme pure de la source JP : sans ASCII ni espace fullwidth."""
    return re.sub(r'[\x00-\x7f\u3000]', '', s)


def load_dico(path: Path):
    ns = {}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), ns)
    if "TR" not in ns:
        sys.exit(f"ERREUR: {path} ne définit pas la variable TR")
    return ns["TR"]


def apply(tr, propagate=False):
    # Normaliser les CLÉS du dico pour matcher contre la forme pure des sources
    tr = {norm(k): v for k, v in tr.items()}

    rows = list(csv.reader(UNIQ.open(encoding="utf-8-sig")))
    hdr, data = rows[0], rows[1:]

    filled, overflow, unmatched = 0, [], []
    for r in data:
        n = norm(r[2])
        if n in tr:
            t = tr[n]
            budget = int(r[1]) // 2
            if any(len(line) > budget for line in t.split("\n")):
                overflow.append((r[2], t, int(r[1]), max(len(l) for l in t.split("\n"))))
            r[3] = t.replace("\n", "\\n")
            filled += 1

    # clés du dico jamais trouvées dans le CSV
    csv_norms = {norm(r[2]) for r in data}
    unmatched = [k for k in tr if norm(k) not in csv_norms]

    with UNIQ.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh); w.writerow(hdr); w.writerows(data)

    print(f"traduites: {filled}/{len(tr)}")
    if unmatched:
        print(f"\nNON TROUVEES dans le CSV ({len(unmatched)}):")
        for k in unmatched[:20]:
            print(f"  {k!r}")
    if overflow:
        print(f"\nDEBORDEMENTS budget ({len(overflow)}) - raccourcir:")
        for src, t, mb, mx in overflow:
            print(f"  budget {mb//2} max={mx}: {t!r}")
    else:
        print("TOUS LES BUDGETS RESPECTES")

    if propagate:
        # propager unique -> strings.csv
        # NB: layouts differ!
        #   unique.csv  = [freq, max_bytes, source_jp(2), final_fr(3)]
        #   strings.csv = [asset, offset, max_bytes, source_jp(3), final_fr(4), note]
        umap = {}
        for r in data:
            if len(r) > 3 and r[3].strip():
                umap[norm(r[2])] = r[3]
        frows = list(csv.reader(FULL.open(encoding="utf-8-sig")))
        fhdr, fdata = frows[0], frows[1:]
        for r in fdata:
            if len(r) > 4:
                n = norm(r[3])          # source_jp
                if n in umap and not r[4].strip():
                    r[4] = umap[n]      # final_fr
        with FULL.open("w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh); w.writerow(fhdr); w.writerows(fdata)
        done = sum(1 for r in fdata if len(r) > 4 and r[4].strip())
        print(f"propagé -> strings.csv: {done}/{len(fdata)} ({100*done//max(1,len(fdata))}%)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    tr = load_dico(Path(sys.argv[1]))
    apply(tr, propagate="--propagate" in sys.argv)
