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

## Le problème des accents / latine dans la police

La map de glyphes de l'exécutable (0x327186, ~3160 codes) couvre hiragana,
katakana et kanji — **pas la latine fullwidth** (０-９/Ａ-Ｚ/ａ-ｚ absents),
contrairement à une première analyse. La ponctuation « ！？」。、 » est gérée
hors de cette table.

Le patch EN de Gyasuke rend du latin en **surécrivant des slots kanji
existants** avec des glyphes latins, puis en utilisant ces codes (plage
0x8a-0x97) dans le texte. Chaque lettre = 1 code 2 octets = 1 slot.

Stratégie FR (chemin robuste, sans casser le bitmap) :
1. **Extraire le mapping code→lettre de Gyasuke** par analyse de fréquence de
   son BVC.BIN EN (les codes les plus fréquents = e/t/a/o/i/n/s/h/r…).
2. Mapper les lettres FR sur ces mêmes slots ; accents → lettre de base
   pour l'instant.
3. (Optionnel, plus tard) injecter de vrais glyphes accentués dans des
   slots vides une fois le format `FTALL.P04` compris.

Contrainte : texte FR concis, ≤ `max_bytes // 2` caractères par ligne
(tous fullwidth, 2 octets chacun), pour tenir dans l'allocation JP.

## Prochaines étapes

- [ ] Outil de propagation des doublons (traduire 1 fois, copier aux N).
- [ ] Traduire par lots : d'abord les cris de combat hauts-fréquence, puis
      le récit principal.
- [ ] Glossaire FR canonique (`glossary/fr-glossary.csv`).
- [ ] Outil de build (validation + patch in-place) adapté au PS2.
