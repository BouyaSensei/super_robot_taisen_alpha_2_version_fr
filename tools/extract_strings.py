#!/usr/bin/env python3
"""Extracteur de chaînes Shift-JIS pour le patch FR de SRT Alpha 2 (PS2).

Adapté du workflow de closedsockets/dreamcast-translation-kit (scan SJIS +
filtre de bruit), appliqué aux fichiers .bin extraits à plat de l'ISO.

Sortie: strings/ja/strings.csv  [asset, offset, max_bytes, source_jp, final_fr, note]

Usage:
  python tools/extract_strings.py                 # scanne la liste par défaut
  python tools/extract_strings.py FICHIER.BIN ... # scanne des fichiers précis
"""
from __future__ import annotations
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "work" / "iso_files" / "jp_all"
OUT_CSV = ROOT / "strings" / "ja" / "strings.csv"

# Fichiers candidats au texte (on évite les gros assets: audio/models/textures).
DEFAULT_FILES = [
    "BVC.BIN",        # dialogues principaux (~69715 chaînes)
    "NAME.BIN",       # noms de stages
    "MTPRO.BIN",      # ? (haute entropie, peut-être chiffré)
    "MTWM.BIN",       # ?
    "MTST.BIN",       # stratégie
    "MTEV.BIN",       # événements
    "MTSTCHAP.BIN",   # chapitres
    "COMMON.BIN",     # texte commun
    "BA.BIN", "HB.BIN", "U.BIN", "XP.BIN", "RB.BIN",
    "WSI.BIN", "S_IMISS.BIN", "MTPROCH.BIN",
    "MTZKN_PT.BIN", "MTZKN_RT.BIN",
]

MIN_BYTES = 4
MIN_JP_CHARS = 2


def is_lead(c: int) -> bool:
    return 0x81 <= c <= 0x9F or 0xE0 <= c <= 0xEF


def is_jp(ch: str) -> bool:
    return "぀" <= ch <= "ヿ" or "一" <= ch <= "鿿" or ch in "。、！？…ー〜・「」（）"


def plausible_text(t: str) -> bool:
    """Filtre le bruit binaire: du vrai texte japonais contient des kana,
    est majoritairement japonais en bytes, avec des runs consécutifs."""
    def isjp(ch):
        return "぀" <= ch <= "ヿ" or "一" <= ch <= "鿿" or ch in "。、！？…「」ー・（）　"
    kana = sum(1 for ch in t if "ぁ" <= ch <= "ん" or "ァ" <= ch <= "ヶ")
    if kana < 1:
        return False
    jp = sum(1 for ch in t if isjp(ch))
    total = len(t.encode("shift_jis", errors="replace"))
    if jp * 2 / max(total, 1) < 0.66:
        return False
    run = best = 0
    for ch in t:
        run = run + 1 if isjp(ch) else 0
        best = max(best, run)
    return best >= 2


def looks_junk(t: str) -> bool:
    body = t.replace("\r", "").replace("\n", "").replace(" ", "").replace("　", "")
    return bool(body) and len(set(body)) <= 2 and len(body) >= 4


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("\r", "\\r").replace("\n", "\\n")


def scan(data: bytes):
    """Retourne [(offset, nb_octets, texte)] des runs SJIS plausibles."""
    out = []
    j, N = 0, len(data)
    while j < N - 1:
        c = data[j]
        if 0x20 <= c <= 0x7E or is_lead(c):
            start = j
            jp = 0
            while j < N - 1:
                c = data[j]
                if 0x20 <= c <= 0x7E or c in (0x09, 0x0A, 0x0D):
                    j += 1
                    continue
                if is_lead(c) and 0x40 <= data[j + 1] <= 0xFC and data[j + 1] != 0x7F:
                    jp += 1
                    j += 2
                    continue
                break
            if j == start:
                j += 1
                continue
            b = data[start:j]
            if len(b) >= MIN_BYTES and jp >= MIN_JP_CHARS and (j >= N - 1 or data[j] < 0x20):
                try:
                    t = b.decode("shift_jis")
                except UnicodeDecodeError:
                    t = None
                if t and plausible_text(t) and len(b) <= 300:
                    out.append((start, len(b), t))
        else:
            j += 1
    return out


def main() -> int:
    args = sys.argv[1:]
    files = [Path(a) for a in args] if args else [SRC_DIR / f for f in DEFAULT_FILES]

    rows = []
    per_file = {}
    for f in files:
        if not f.exists():
            print(f"  [manque] {f.name}")
            continue
        data = f.read_bytes()
        found = scan(data)
        per_file[f.name] = (len(data), len(found))
        for off, n, t in found:
            note = "JUNK - do not translate" if looks_junk(t) else ""
            rows.append([f.name, f"0x{off:x}", n, esc(t), "", note])

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["asset", "offset", "max_bytes", "source_jp", "final_fr", "note"])
        w.writerows(rows)

    print(f"{'fichier':<16} {'taille':>12} {'chaînes':>8}")
    for name, (size, cnt) in per_file.items():
        print(f"{name:<16} {size:>12,} {cnt:>8,}")
    junk = sum(1 for r in rows if r[5])
    print(f"\nTOTAL: {len(rows):,} chaînes ({junk:,} junk) -> {OUT_CSV.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
