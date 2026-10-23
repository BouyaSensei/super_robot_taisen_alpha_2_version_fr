#!/usr/bin/env python3
"""Worklist unique + propagation des doublons.

Workflow: on traduit chaque chaîne UNIQUE une fois (dans strings/ja/unique.csv,
triée par fréquence décroissante), puis on propage la traduction à toutes les
occurrences dans strings/ja/strings.csv.

Usage:
  python tools/dedupe_worklist.py --build       # génère unique.csv (à traduire)
  python tools/dedupe_worklist.py --propagate   # remplit strings.csv depuis unique.csv
"""
from __future__ import annotations
import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FULL_CSV = ROOT / "strings" / "ja" / "strings.csv"
UNIQ_CSV = ROOT / "strings" / "ja" / "unique.csv"


def unescape(v: str) -> str:
    out, i = [], 0
    while i < len(v):
        if v[i] == "\\" and i + 1 < len(v):
            n = v[i + 1]
            if n in ("r", "n", "\\"):
                out.append({"r": "\r", "n": "\n", "\\": "\\"}[n]); i += 2; continue
        out.append(v[i]); i += 1
    return "".join(out)


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("\r", "\\r").replace("\n", "\\n")


def build() -> None:
    rows = list(csv.reader(FULL_CSV.open(encoding="utf-8-sig")))
    data = [r for r in rows[1:] if not r[5]]  # hors JUNK
    freq = Counter(r[3] for r in data)
    maxbytes = defaultdict(int)
    for r in data:
        maxbytes[r[3]] = max(maxbytes[r[3]], int(r[2]))
    uniq = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    UNIQ_CSV.parent.mkdir(parents=True, exist_ok=True)
    with UNIQ_CSV.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["freq", "max_bytes", "source_jp", "final_fr"])
        for src, c in uniq:
            w.writerow([c, maxbytes[src], esc(src), ""])
    done = 0
    print(f"{len(uniq):,} chaînes uniques -> {UNIQ_CSV.relative_to(ROOT)}")
    print(f"(fréquence décroissante; traduis la colonne final_fr)")


def propagate() -> None:
    uniq = list(csv.reader(UNIQ_CSV.open(encoding="utf-8-sig")))[1:]
    tr = {}
    for freq, mb, src, fr in uniq:
        if fr.strip():
            tr[unescape(src)] = unescape(fr)
    rows = list(csv.reader(FULL_CSV.open(encoding="utf-8-sig")))
    hdr, data = rows[0], rows[1:]
    filled = 0
    for r in data:
        if r[5]:
            continue
        src = unescape(r[3])
        if src in tr:
            r[4] = esc(tr[src])
            filled += 1
    with FULL_CSV.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(hdr)
        w.writerows(data)
    total = sum(1 for r in data if not r[5])
    done = sum(1 for r in data if not r[5] and r[4])
    print(f"propagé: {filled:,} occurrences remplies")
    print(f"progression: {done:,}/{total:,} ({100*done//max(total,1)}%)")


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--build", action="store_true")
    g.add_argument("--propagate", action="store_true")
    a = ap.parse_args()
    (build if a.build else propagate)()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
