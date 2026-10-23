# Pipeline d'extraction et de traduction FR

## Workflow (adapté de closedsockets/dreamcast-translation-kit)

Le patch EN de Gyasuke est « fortement inspiré » du kit Dreamcast de
closedsockets (workflow, pas le code). On reprend ce workflow éprouvé,
adapté aux fichiers `.bin` PS2 extraits à plat :

1. **Extraction** — `tools/extract_strings.py` scanne les `.bin` pour les
   runs Shift-JIS (détection byte par byte + filtre de bruit binaire), et
   produit la worklist `strings/ja/strings.csv`.
2. **Traduction** — on remplit la colonne `final_fr`, une fois par chaîne
   *unique*, puis on propage aux occurrences identiques.
3. **Validation + build** — remplacement in-place à largeur fixe : le texte
   cible doit tenir dans l'allocation byte d'origine (padding au byte
   d'origine, 0x00 si null-terminé, sinon espace). Vérification que les
   octets sources correspondent avant écriture.

## Format de la worklist (`strings/ja/strings.csv`)

`asset, offset, max_bytes, source_jp, final_fr, note`

- `offset` : décalage hex du début de la chaîne dans le fichier.
- `max_bytes` : allocation byte d'origine (le texte FR doit y tenir).
- `\r` / `\n` échappés en 2 caractères ; `{BLANK}` efface une chaîne.
- `note=JUNK` : bruit binaire, ne pas traduire.

## État de l'extraction (30 209 chaînes)

| Fichier | Chaînes | Contenu |
|---|---|---|
| BVC.BIN | 28 374 | Dialogues principaux + combat |
| MTZKN_PT.BIN | 717 | Encyclopédie (noms, voix, œuvres) |
| MTZKN_RT.BIN | 685 | Encyclopédie |
| RB.BIN | 272 | Texte divers |
| NAME.BIN | 90 | Noms de stages |
| MTEV.BIN | 29 | Événements |
| autres | ~40 | menus, unités |

**11 587 chaînes uniques** à traduire (62 % de doublons).

Fichiers **chiffrés/compressés** (non extraisibles en SJIS brut) :
MTPRO.BIN, MTWM.BIN, MTST.BIN, COMMON.BIN — restent bloqués (haute entropie).

## Le problème des accents français

Le kit closedsockets/Gyasuke sort en **ASCII pur** (l'anglais mappe 1:1 sur
les glyphes latins de la police JP). Le français a des **accents** (é è à ç
û ô î œ…) absents de la police JP.

Stratégie en deux temps :
1. **Maintenant** — le CSV garde du *vrai* français avec accents. Au build,
   un mapping accent→lettre de base (é→e) permet de produire un patch
   jouable sans toucher à la police.
2. **Plus tard** — casser le format `FTALL.P04` (slot→offset) pour injecter
   de vrais glyphes accentués dans les slots vides, comme Gyasuke l'a fait
   pour les lettres anglaises manquantes. Le CSV ne change pas.

## Prochaines étapes

- [ ] Outil de propagation des doublons (traduire 1 fois, copier aux N).
- [ ] Traduire par lots : d'abord les cris de combat hauts-fréquence, puis
      le récit principal.
- [ ] Glossaire FR canonique (`glossary/fr-glossary.csv`).
- [ ] Outil de build (validation + patch in-place) adapté au PS2.
