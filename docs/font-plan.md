# Plan police — caractères français

## Problème

La police du jeu ne contient que des glyphes japonais (kana, kanji, quelques symboles). Aucun caractère latin. Le projet EN a contourné le problème en :
- travaillant en **majuscules uniquement** (moitié des glyphes à fournir) ;
- mappant des **paires de lettres** dans des slots vides du font (y compris les slots katakana/hiragana libérés par la traduction).

Pour le français, il faut en plus les **accents**. Options :

## Option A — Slots vides + accents (comme l'EN)

- Réutiliser la technique des paires pour A-Z a-z.
- Accents : é è ê à â ç ù û î ô (+ majuscules É È Ê À Â Ç Ù Û Î Ô) = 20 glyphes supplémentaires à mapper dans des slots vides.
- Risque : il faut assez de slots vraiment vides (le font a déjà servi pour les paires EN ; nous repartons du font JP d'origine, donc tous les slots kana sont disponibles tant qu'on traduit tout le texte — c'est notre cas).
- Avantage : pas besoin de reconstruire la police, seulement un tableau de mapping.

## Option B — Reconstruction complète du font (recommandée)

Le projet EN a démontré que la police peut être **convertie en PNG éditable puis réencodée dans le format original**. On peut donc :
1. Extraire la police de l'exécutable (IOPRP253.IMG → EBOOT.BIN) — localiser via signature + taille des glyphes.
2. La convertir en grille PNG (slot par slot).
3. Dessiner/remplir une police latine complète avec accents dans les slots nécessaires (police bitmap de la bonne taille, style proche du font original pour rester sobre).
4. Réencoder et réinjecter dans l'exécutable.

Avantages : contrôle total, pas de dépendance aux slots vides, rendu propre.
Inconvénients : plus de travail initial ; il faut valider le format binaire du font (taille des glyphes, compression éventuelle, table d'index).

## Décision

**Option B en priorité** (plus robuste pour le FR), Option A en repli si le format du font s'avère trop verrouillé.

## Premiers pas concrets (quand on aura localisé la police)

1. Identifier la taille des glyphes (probablement 8x8, 16x16 ou 24x24 — vérifier avec FONTCOL.C16 et le rendu).
2. Dump d'une page de font → PNG visuel pour confirmer la lecture.
3. Canary : remplacer 5 slots par des glyphes test (A, é, Ç, œ, ?) + chaîne de test dans un stage → booter sur PCSX2 → screenshot.

## Glyphes FR à prévoir (liste complète)

- Base : A-Z a-z 0-9 espace
- Ponctuation : . , ; : ! ? ' " ( ) - — … « »
- Accents minuscules : é è ê ë à â ù û ü î ô ç
- Accents majuscules : É È Ê Ë À Â Ù Û Ü Î Ô Ç
- Ligatures (option) : œ Œ
- Divers : © ™ % ° ‰
