# Recherche — police FTALL.P04 & mapping code→lettre

Objectif : obtenir le mapping code (2 octets) → glyphe/lettre du patch EN de Gyasuke,
pour écrire du français avec les mêmes codes (accents en repli é→e), OU construire
notre propre police avec accents.

## DÉCOUVERTE CLÉ — c'est une police en DIGRAMMES/TOKENS, pas A-Z (session 23/10)
**Cela change toute l'approche.** Vérifié sur les cris de combat (stables, texte JP lisible) :
- **Ratio ~1.24 code / caractère-JP**, et un mot entier tient parfois dans 1 code.
  Ex. 「行けっ！」= « GO! » → `0x974d` + `0x88c7(!)` ⇒ **1 code = le mot "GO"**.
- **Ce n'est PAS un code par lettre.** Chaque code (2 octets) = un FRAGMENT de texte
  (souvent un digramme = 2 lettres, parfois plus). Gyasuke a découpé l'anglais en
  fragments, créé un GLYPHE LIGATURE par fragment, et stocké les codes dans BVC.BIN.
- **Ancres digrammes établies** (haute confiance, `work/digraph_anchors.json`) :
  - `0x88c7` = « ! » ; `0x974d` = "GO" ; `0x96e2`+`0x93e5` = "FA"+"LL" (FALL) ;
    `0x8d61`+`0x945b` = "SI"+"NK" (SINK).
- **Conséquence** : le « mapping » à cracker n'est pas 26 lettres mais un **vocabulaire de
  ~3000 fragments de texte**. Pour écrire du FR, il faut (a) la table code→fragment et
  (b) découper mon français dans les MÊMES fragments. C'est un problème d'**alignement
  texte-anglais ↔ séquences de codes**, crackable si on a le plaintext anglais fiable.
- Dataset : **3018 cris de combat uniques** (JP + codes + freq) → `work/battle_cries.json`.

### Corrections apportées cette session
- Les chaînes police sont à **offsets FICHIER** 0x32fdxx ⇒ **VAs réelles 0x42e4xx**
  (section texte : VA = file_off + 0xFE700). Le nom de fichier réel est `st:data/ftall.p04`
  (chemin IOP PS2, st: = lecteur CD/DVD), à file 0x32fdea / VA 0x42e4ea.
- **Ces strings semblent être du code mort/debug** : 0 instruction `lui/ori` les charge,
  0 pointeur LE (word) ne pointe vers le bloc 0x42e4xx, pas de `set_gp` trouvé, pas
  d'accès gp-relatif détectable. ⇒ chasser le parser via ces chaînes = impasse.
- **ELF strippé confirmé** : 202 sections, 197 progbits, **aucune section REL/RELA**.
  La clé « relocations ELF » ne s'applique pas (pas de relocations).
- Le font n'est PAS un bitmap plat ni vectoriel simple : rendus 1bpp/8bpp à TOUTES les
  tailles de slot testées (256/240/224/192/128) = bruit. Les glyphes sont des ligatures
  pré-rendues dans un format structuré (tables scissor/alpha/bright), il faut le parser
  pour les rasteriser — MAIS on peut contourner en crackant le vocabulaire par alignement.

## Constats établis (vérifiés, reproductibles via work/*.py)

### 1. FTALL.P04 n'est PAS un atlas bitmap plat
- Taille : 806 400 octets (JP et EN identiques en taille).
- Rendu de glyphes à tous les pas testés (208..256, fenêtre 40×24, MSB-first) → **bruit**
  pour les slots des codes EN les plus fréquents. Aucun pas ne produit de forme lisible.
  Script : `work/font_diag.py` (PNG `work/font_diag.png`).
- Autocorrélation : pic faible à lag 160 ; bosse de runs de zéros à 16-17 octets
  (alignement 16). Signal insuffisant pour conclure. Script : `work/font_analyze.py`.

### 2. La police a 3 sous-tables : scissor / alpha / bright
- Chaînes dans l'exécutable SLPS_252.28 :
  - `0x32fd37` « ERROR: font scissor table is full. »
  - `0x32fd67` « ERROR: font alpha table is full. »
  - `0x32fd97` « ERROR: font bright table is full. »
- ⇒ Le format est structuré (rectangles de recorte + transparence + luminosité + bitmap),
  pas un simple tableau de glyphes. C'est pourquoi les rendus plats échouent.

### 3. Table des codes caractères (à l'exécutable, offset 0x327186)
- **3646 entrées fixes** de 2 octets (codes SJIS), du `0x327186` au `0x328E02`.
- Commence par un placeholder `0x8140` ; `0x8140` = slot vide.
- **487 slots vides, 3159 remplis.** Index de slot = position dans le tableau (0..3645).
- Script : lecture dans `work/font_calib2.py`.

### 4. Objet « police » à l'exécutable, offset 0x32fdc0
- Structure : **8 pointeurs** (vers du code/data en 0x12xxxx) + chaîne `host:data/ftall.p04`
  (à 0x32fde0). Ressemble à un objet C++ (vtable + nom de fichier).
- Pointeurs : 0x1251e8, 0x1251f8, 0x125208, 0x125218, 0x125248, 0x125248, 0x125228, 0x125238.
- Le parser bitmap est dans l'une de ces fonctions (à identifier).

### 5. Le mapping du patch EN n'est PAS monoalphabétique
- BVC.BIN EN : **3115 codes distincts** (plage kanji), 378 178 occurrences.
- Gyasuke a utilisé des **digraphes** (2 lettres → 1 slot) ⇒ alphabet > 26 lettres.
- Analyse fréquentielle seule insuffisante (distribution lisse, pas de « the » net en trigramme).
- Top unigrammes : `0x88c7` (3,78 % ≈ 'e'), `0x8951` (2,27 %), `0x8ade` (2,11 %),
  `0x89f0`, `0x94f5`, `0x8aec`, ... Script : `work/font_freq.py`, `work/font_crypto.py`.

### 6. Références indirectes (blocage du désassemblage rapide)
- Aucune instruction `lui $rX, 0x32fd` dans l'exécutable (0 occurrence).
- Aucun pointeur big-endian vers 0x32fde0 / 0x32fd37 / 0x32fd67.
- ⇒ Les adresses data sont résolues via le **tableau de relocation ELF** (indirection),
  pas par chargement d'adresse absolue. Il faut traiter les relocations pour trouver
  le code qui charge « host:data/ftall.p04 » et parse le bitmap.

## État : BLOQUÉ sur le format bitmap exact
Pour débloquer, il faut (effort RE dédié, multi-sessions) :
1. Traiter les relocations ELF de SLPS_252.28 (segments .text/.rodata, base 0x100000).
2. Trouver la fonction qui ouvre `host:data/ftall.p04` et parse scissor/alpha/bright + bitmap.
3. En extraire : taille des tables, offset du bitmap, pas par glyphe, packing des bits.
4. Rendre les glyphes EN → lire visuellement le mapping code→lettre (ou corréler avec le texte).

Outils en place : `capstone 5.0.9` dans `work/.venv` (désassemblage MIPS32 OK, voir
`work/mips_dis.py`). Pas d'objdump/radare2 local.

## Pistes alternatives (peut-être plus rapides)
- **Crib-decoding** : aligner BVC.BIN JP↔EN (mêmes offsets), utiliser le texte JP lisible +
  les noms de personnages (tags de speaker) comme cribs pour déduire code→lettre par segments.
  Nécessite d'identifier les zones de tags de speaker dans BVC.BIN.

## Path A — recherche de dump/mapping public : ÉPUISÉE (conclusion)
Recherché et vérifié (aucune source publique du mapping ou du font décodé) :
- **GitLab Gyasuke** (`gabalva98`) — 4 repos : `2nd-...-ps2` (README + xdelta),
  `super-robot-taisen-alpha-for-dreamcast` (README + xdelta + `T20602M.zip` = PNG textures
  uniquement), `3rd-...`, `back-up-patch`. **Aucun outil source, aucun dump de police,
  aucune table code→lettre.** Ses outils PS2 sont privés.
- **GitHub closedsockets** — `dreamcast-translation-kit` (public) + `tricolore-crise` (patches).
  Le kit DC est pour le format **PowerVR Dreamcast**, pas PS2.
- **Web** : aucun dump public du font PS2 SRT Alpha 2.
- **Kapml (Alpha 3, romhacking 7842)** — « HD font » mais distribution Discord/téléchargement,
  **pas de repo public d'outils**.

### Intelligence récupérée (change l'approche C et B)
Sources : fil forum romhacking topic 41712 (spoil détaillé de Gyasuke) + `pvr_tool.py` du kit DC.
1. **La police est MAJUSCULES uniquement** (A-Z) + digraphes + ponctuation.
   Gyasuke : « A decision I made was to work directly in Uppercase, so I don't need to add too
   many combinations ». ⇒ Alphabet restreint (~26 + dizaine de digraphes), pas 52 lettres.
2. **Système de digraphes** : son outil remplace les *combinaisons de 2 lettres* par une valeur
   de police (1 slot). Les slots vides (`0x8140`, 487 disponibles) reçoivent ces combos + lettres.
   ⇒ Le mapping n'est PAS A-Z en positions fixes : c'est un assignment custom sur slots
   kanji-réutilisés + slots vides.
3. **Le bitmap n'est PAS row-major naïf.** Le kit DC (`pvr_tool.py`) décode des textures avec un
   **twiddle** (interleaving des coords x,y via `_untwiddle`). Le font PS2 a très probablement son
   propre interleave ⇒ explique pourquoi tous les rendus plats = bruit. En RE (path C), chercher
   une transformation de coordonnées dans le parser, pas un simple stride linéaire.
4. **Workflow confirmé** : decoder font→PNG éditable → éditer → re-encoder à longueur d'octets
   identique (patch en place sûr).
5. Le blocage central de Gyasuke était exactement « the mapping of the values of the font » —
   même problème que le nôtre. Il n'a jamais publié la table.

## Path B — crib-decoding JP↔EN : acquis + plafond atteint
### Acquis solides (réutilisables)
- **Alignement PARFAIT** : `BVC.BIN` JP et EN = **157 676 segments identiques** (mêmes offsets).
  Dump complet des paires alignées → `work/bvc_pairs.json`. Base solide pour toute méthode.
- **Ancre ponctuation** : code `0x88c7` = « ! » (termine ~tous les cris de combat), slot **311**.
  `0x88c8` = « !! », slot 316.
- **Structure du font FTALL.P04** (diff JP↔EN, 3150 slots × 256 octets) :
  - Slots **0–1001** : IDENTIQUES JP/EN (glyphes japonais conservés).
  - Slots **1002–3149** : TOUS modifiés par Gyasuke (bloc contenu anglais, contigu, gap=1).
  - **1972 codes** pointent vers le bloc EN ; assignation **non séquentielle** (slots 1006–3136),
    PAS un bloc A-Z propre. Certains codes très fréquents réutilisent des slots JP (< 1002) :
    `0x8951`→388, `0x8ade`→735, `0x89f0`→565, `0x8aec`→754. Ancre « GO » (`0x974d`) → slot 3273.
- **Les glyphes ne sont PAS des bitmaps plats** : les bytes bruts d'un slot (ex. 311) montrent des
  records structurés 16-bit répétés + zones de zéros, beaucoup de bytes non-nuls (pas le profil
  d'un bitmap 0x00/0xFF). ⇒ très probablement **contours vectoriels** rasterisés à l'exécution
  (cohérent avec les tables scissor/alpha/bright de l'exécutable).

### Plafond atteint (pourquoi B seul ne suffit pas)
- **Mapping par fréquence = bruit** : les digraphes polluent le classement ; décodage des phrases
  normales illisible (`??Z?O???A???I?AC?`). Hypothèse monoalphabétique invalidée.
- **Solving par plaintext connu = trop bruité** : sans le texte anglais EXACT de Gyasuke (son repo
  n'a que le xdelta, pas de dump de chaînes), mes traductions approximatives ne s'alignent pas
  fiablement sur les codes (seuls FALL→FA+LL, SINK→SI+NK propres, car partition forcée).
- **Rendu des glyphes = bruit** à tous les layouts testés (8bpp/1bpp, strides 208–256) : confirmé
  que ce n'est pas un atlas bitmap naïf.

### Conclusion
Path B donne la base (alignement, structure, ancres) mais **ne produit pas une map complète** :
l'assignation code→slot est custom/non séquentielle ET les glyphes sont vectoriels ⇒ il faut les
**rendre pour les lire**, ce qui = piste C (RE du format/parser de police).

## Session 2 (continuation) — texture/compressé + parser hors exécutable
Poursuite piste C après la découverte digrammes. Conclusions nouvelles :
- **FTALL.P04 n'est un bitmap lisible dans AUCUN layout simple.** Testés : 8bpp/1bpp
  (strides 208–256), 16-bit index→gris à 5 dimensions (768×525, 1280×315, 640×630,
  1024×393, 512×787). Tous = **bruit pur** (vision_analyze confirmé : « aucune forme de
  lettre »). Taux d'encre ~54 % indépendant du layout ⇒ profil NON bitmap. Les glyphes
  sont **compressés/structurés**, rasterisés par le parser à l'exécution.
- **Le parser n'apparaît PAS dans l'exécutable SLPS_252.28** :
  - Section [4] (file 0x1900..0x35ee80, VA 0x100000) = SEULE section réelle (code+data
    mélangés, monolithique). Scannée intégralement.
  - String « st:data/ftall.p04 » (file 0x32fdea / VA 0x42e4ea) : **1 occurrence unique,
    0 référence** (ni lui/ori, ni pointeur LE word). ⇒ code mort/debug.
  - Constantes du format absentes : taille fichier 806400 (0xC4E00), nb slots 3150 (0xC4E),
    taille slot 256 → **0 site** lui/ori ET 0 word LE.
  - Pas de relocations (ELF strippé, confirmé).
  ⇒ Le rendu de la police est très probablement dans une **lib externe** (libgpu.spr système,
    non livrée dans l'ISO) ou via un mécanisme non détectable sans RE profonde.
- **Hypothèse PSM/CLUT** : extensions « .P04 » + compagnons `FONTCOL.C16` (512 o),
  `HEN.P04`, `HEN.C16` ⇒ PSM (Pixel Storage Mode) GS + CLUT. FTALL.P04 = atlas texture,
  FONTCOL.C16 = sa palette. MAIS le contenu n'est pas row-major naïf (twiddle/compression).
- **ps2sdk fontx.c** (récupéré, `work/fontx_ref.c`) : header `id[7],name[9],w,h,type,
  table_num, blocks{start,end}[]` — c'est le format **KROM/BIOS** (rom0:KROM), ne matche
  PAS FTALL.P04 (qui commence par des zéros, pas un id texte). Pas réutilisable tel quel.

### État honnête du blocage mapping
Cracker la table code→fragment complète reste **un effort RE multi-sessions sans win rapide** :
(a) parser hors exécutable (lib système à RE), (b) glyphes compressés (format inconnu),
(c) plaintext anglais exact de Gyasuke non public, (d) tokenisation variable (alignement
positionnel pur invalide). La découverte digrammes + le dataset de 3018 cris sont des acquis
solides réutilisables.

## Session 3 — structure de table cracker + guessing format EPUISE
### Structure de la table code→slot (CORRECTION importante)
- La région `0x327186` de l'exe est une **liste de codes 2 octets en BIG-ENDIAN**
  (pas des indices de slot !). `81 40` = code 0x8140 (placeholder VIDE), `82 4f`=0x824f...
- **3646 entrées**, fin à l'offset file `0x328e02`. **3159 glyphes réels** (non 0x8140),
  487 vides. min code=0x8140, max=0x98b5.
- La **POSITION dans la liste = index de slot** dans FTALL.P04. Map code→position :
  - `0x88c7` (« ! ») → position **311** (confirmé)
  - `0x974d` (« GO ») → position **3273**
  - `0x824f` (1er code réel) → position **1**
- NB : 806400/3646 n'est pas entier ; 806400/3150=256, /3360=240, /3600=224. La taille
  par slot exacte reste ambiguë (les slots vides consomment-ils de l'espace ?).

### Guessing aveugle du format : EPUISE (tous = bruit)
Testés sur le slot « ! » (pos 311) et montages, TOUS donnent du bruit (vision confirmée) :
- 8bpp row-major (5 dims), 16bpp row-major (5 dims)
- 16×16 twiddled DC + PS2 GS (montage 64 slots)
- DCT 8×8 blocks (IDCT) — range ±42000, DCs ~0, non
- planaire/intercalé (strides 3150/1008/5040)
- bit-packé 1bpp (4 dims)
- tailles de slot 256/240/224/192 (240 donne 9% encre, le plus sparse, mais pas un « ! »)
- Distribution valeurs : JP ≈ EN (0x00 dominant, max=221), pas de diff d'encodage.
⇒ **Le data est compressé/encodé ; aucun layout pixel simple ne le rend lisible.**

### Le decodeur n'est PAS dans l'ISO
- Scan de tous les fichiers ISO (71) : constantes format (806400/3150) absentes des .IRX.
- Main exe : string « ftall.p04 » morte, 0 ref code, 0 constante format, ELF strippé.
⇒ Decodeur dans **libgpu.spr** (lib systeme PS2, non livree) ou code live a localiser par RE.

### REFRAEMENT STRATEGIQUE (important pour l'objectif FR)
Pour un **patch francais**, on a besoin de la map **code→lettre**, PAS du decodeur de la
police. La compression de FTALL.P04 n'est necessaire que pour AJOUTER des glyphes — or
Gyasuke a deja ajoute tous les glyphes anglais/digraphes, et majuscules FR = majuscules EN.
⇒ Voie a plus forte valeur : **alignement sur les NOMS DE PERSONNAGES** (tags speaker dans
BVC.BIN = plaintext latin fiable « CAMILLE », « AMURO »...) pour cracker code→lettre SANS
toucher au format. RE du decodeur = fallback si la map letters est insuffisante.

## Scripts (reproductibles, dans work/)
- `font_analyze.py` — hexdump + facteurs + autocorrélation + runs de zéros.
- `font_calib2.py` — lecture table 3646 codes + rendu multi-pas (PNG).
- `font_diag.py` — rendu compact slot×pas (PNG `font_diag.png`).
- `font_freq.py` / `font_crypto.py` — unigrammes/bigrammes/trigrammes du BVC EN.
- `mips_dis.py` — désassemblage capstone des cibles de vtable.
