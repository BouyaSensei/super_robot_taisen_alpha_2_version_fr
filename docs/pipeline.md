# Pipeline — patch français SRT Alpha 2 (PS2)

## Étape 0 — Matériel (fait)

- ISO japonaise **SLPS-25228** : 2 501 378 048 octets, dans le dossier du projet (non versionné).
- Patch EN de référence : `reference/english-translation/SRTAlpha2_0.8.0.xdelta`.

## Étape 1 — Cartographie de l'ISO (fait)

71 fichiers. Les conteneurs pertinents pour le texte :

| Fichier | Rôle probable |
|---|---|
| `DATA/MTPRO.BIN` + `MTPROCH.BIN` | Script principal (scénario / prologue) — "MT" = main text ? |
| `DATA/MTEV.BIN` + `MTEVBG.BIN` | Événements (dialogues VN) |
| `DATA/MTST.BIN` + `MTSTCHAP.BIN` | Stages / chapitres (section stratégie) |
| `DATA/NAME.BIN` | Noms (personnages, unités) |
| `BATTLE/CM/COMMON.BIN`, `CMNHED.BIN`, `CMNBDY.BIN` | Dialogues de bataille ("Combat Message") |
| `DATA/FONTCOL.C16` | Couleurs de la police (la police elle-même est ailleurs, probablement dans l'exécutable) |
| `IOPRP253.IMG` | Image RAM IOP — contient EBOOT.BIN (exécutable du jeu : font + code d'affichage) |

## Étape 2 — Décodage du patch EN comme "traceur" (en cours)

Méthode : appliquer le xdelta EN à notre ISO JP → `patched_en.iso`, puis comparer octet par octet l'ISO JP et l'ISO EN. Les régions modifiées = **exactement** les emplacements de texte utilisés par le projet EN. Avantages :
- pas de devinette sur les formats ;
- on obtient la liste des fichiers + offsets + longueurs de toutes les zones de texte d'un coup ;
- en lisant le texte anglais à ces offsets, on déduit l'encodage et le format de chaîne (borne, codes variables).

## Étape 3 — Extraction des chaînes japonaises

À partir de la carte d'offsets : extraire chaque chaîne JP originale (même offset dans l'ISO JP) → `strings/ja/*.json` :
```json
{"id": "mtpro_000123", "file": "DATA/MTPRO.BIN", "offset": 123456, "len": 48, "ja": "...", "en_ref": "..."}
```
Préserver les codes variables (n° d'unité, n° de stage) tels quels — le projet EN a eu ce bug au début.

## Étape 4 — Analyse de la police

La police est dans l'exécutable (IOPRP253.IMG → EBOOT.BIN). Plan détaillé : `font-plan.md`.
Objectif : glyphes latins A-Z a-z 0-9 ponctuation **+ accents FR** (é è ê à â ç ù û î ô + majuscules, œ/Œ si possible).

## Étape 5 — Traduction FR

- Par lots de fichiers (NAME → MTPRO → MTEV → MTST → BATTLE/CM).
- Glossaire imposé (`glossary/fr-glossary.csv`) : noms de pilotes/méchas/armes/orgs alignés sur les conventions officielles FR (Akurasu / wiki SRW) quand elles existent.
- Contrainte dure : limite d'octets par chaîne (1 à 4 lignes). Script de vérification `tools/check_fit.py` qui flague les dépassements ; stratégie de condensation : ponctuation allégée, abréviations du glossaire, raccourcis de noms en dernier recours.
- Le français sans accents est proscrit (lisibilité) — d'où l'importance de l'étape 4.

## Étape 6 — Insertion + patch

1. Script `tools/insert_strings.py` : réécriture des zones de texte dans une copie de l'ISO JP avec les chaînes FR encodées (mêmes offsets, mêmes longueurs max).
2. Vérification : re-extraction de l'ISO modifiée → toutes les chaînes FR présentes, aucune zone hors-texte touchée.
3. `xdelta3 -e -s original.iso patched_fr.iso SRTAlpha2_FR_0.1.0.xdelta` (via Docker).

## Étape 7 — Test

- PCSX2 : boot, chapitres 1-2 de chaque route, un stage complet avec dialogues de bataille.
- Vérifier : accents rendus correctement, codes variables fonctionnent, texte dans les boîtes.

## Commits

Chaque étape validée = 1 commit (outils + données + docs). Les ISO et gros binaires restent hors git (.gitignore).
