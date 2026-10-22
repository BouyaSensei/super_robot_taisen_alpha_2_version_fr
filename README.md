# 2nd Super Robot Taisen Alpha — Patch Français (FR)

Traduction fan du jeu PS2 **Dai-2-Ji Super Robot Taisen Alpha** (Super Robot Wars Alpha 2, Banpresto, 2003) en français.

## État du projet

| Étape | Statut |
|---|---|
| Setup repo + structure | ✅ Fait |
| Recherche format texte / outils | ✅ Fait (voir `docs/research.md`) |
| Obtention ISO japonaise SLPS-25228 | ⏳ **En attente (fournie par l'utilisateur)** |
| Analyse binaire du conteneur de texte | ⏸️ Bloqué sur l'ISO |
| Outil d'extraction → `strings/ja/` | ⏸️ Bloqué sur l'ISO |
| Analyse police + plan caractères FR | ⏸️ Bloqué sur l'ISO (voir `docs/font-plan.md`) |
| Traduction (~69 700 chaînes) | ⏸️ Bloqué sur l'extraction |
| Outil d'insertion + ISO patchée | ⏸️ |
| Patch xdelta final | ⏸️ |

## Structure du repo

```
reference/english-translation/   Matériel du patch EN (README + xdelta 0.8.0 de Gyasuke)
docs/                            Recherche, pipeline, plan police
tools/                           Scripts d'extraction / insertion (à construire)
strings/ja/                      Chaînes japonaises extraites (JSON)
strings/fr/                      Traductions françaises
glossary/                        Terminologie FR (CSV)
patches/                         Patch xdelta final
work/                            Fichiers temporaires de travail (non versionné)
```

## Pipeline (résumé)

1. ISO japonaise **SLPS-25228** (édition standard — PAS SLPS-25227 ni SLPS-73206).
2. Extraction des conteneurs de texte → identification du format (encodage, compression, bornes).
3. Outil d'extraction : chaque chaîne = 1 bloc affiché dans une textbox (1 à 4 lignes), avec ses codes variables (n° d'unité, n° de stage) préservés.
4. Analyse de la police du jeu : le font ne contient que des glyphes japonais → il faut créer les glyphes latins + accents FR (stratégie dans `docs/font-plan.md`).
5. Traduction en lots avec glossaire imposé, contrôle des limites d'octets par chaîne.
6. Insertion dans l'ISO → génération du patch xdelta3.
7. Test sur PCSX2.

Détails complets : `docs/pipeline.md`.

## Notes importantes

- **Limites d'octets strictes** : le texte tient dans des textboxes de 1 à 4 lignes. Le français est plus long que le japonais/anglais → abréviations et condensations seront nécessaires (même approche que le patch EN).
- **Police sans caractères latins** : c'est le point technique n°1 du projet (le patch EN a dû mapper des paires de lettres dans des slots vides du font ; pour le FR il faut les accents é/è/à/ç…).
- **Aucun fichier de jeu dans ce repo** : uniquement outils, textes et docs. L'ISO est fournie par l'utilisateur (dump légal de son propre disque).

## Crédits & références

- **Gyasuke** — patch anglais 0.8.0 (romhacking.net/translations/7745) ; son README et son xdelta sont en `reference/english-translation/`.
- **closedsockets** — dreamcast-translation-kit, référence de workflow pour l'extraction/insertion et la conversion police↔PNG.
- **Akurasu** — base de noms officiels SRW (akurasu.net), à utiliser pour le glossaire.
