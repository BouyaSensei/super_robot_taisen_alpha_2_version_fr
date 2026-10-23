#!/usr/bin/env python3
"""Force-fit: ajuste chaque valeur d'un dictionnaire TR dans son budget.

Usage: python tools/autofit.py work/lot5.py

Lit unique.csv pour le budget (max_bytes//2 par ligne), puis pour chaque
valeur dont une ligne depasse, retire d'abord la ponctuation/espaces de fin,
puis des mots de fin, jusqu'a ce que ca tienne. Ecrit le fichier en place.
Sert de filet de securite apres avoir ecrit un lot a la main.
"""
import csv, re, sys, importlib.util, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm(s):
    return re.sub(r'[\x00-\x7f\u3000]', '', s)


def load_budgets():
    budgets = {}
    with open(os.path.join(ROOT, 'strings/ja/unique.csv'), encoding='utf-8-sig') as f:
        for r in list(csv.reader(f))[1:]:
            if len(r) >= 3:
                budgets[norm(r[2])] = int(r[1]) // 2
    return budgets


def fit_line(line, budget):
    """Retire ponctuation/espaces de fin, puis mots de fin, jusqu'a budget."""
    line = line.rstrip()
    # 1) ponctuation + espaces de fin
    while len(line) > budget and line and line[-1] in ' \t?!.,;:」』！？。、':
        line = line[:-1]
    line = line.rstrip()
    # 2) mots de fin
    while len(line) > budget and ' ' in line:
        line = line[:line.rfind(' ')]
    return line


def main():
    if len(sys.argv) < 2:
        print("usage: autofit.py <fichier_dico.py>")
        sys.exit(1)
    path = sys.argv[1]
    budgets = load_budgets()

    spec = importlib.util.spec_from_file_location('lot', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tr = {norm(k): v for k, v in mod.TR.items()}

    changed = 0
    for k, v in list(tr.items()):
        budget = budgets.get(k)
        if budget is None:
            continue
        lines = v.split('\n')
        new_lines = [fit_line(ln, budget) for ln in lines]
        new_v = '\n'.join(new_lines)
        if new_v != v:
            tr[k] = new_v
            changed += 1
            print(f"ajusté (b={budget}): {v!r} -> {new_v!r}")

    # reecrit le fichier avec les valeurs ajustees
    items = ',\n'.join(
        f"{k!r}: {v!r}" for k, v in tr.items()
    )
    content = f"# Lot (autofit applique)\nTR = {{\n{items}\n}}\n"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n{changed} valeur(s) ajustee(s), fichier reecrit.")


if __name__ == '__main__':
    main()
