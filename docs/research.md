# Recherche — format du jeu & projet anglais

## Le jeu

- **Titre** : Dai-2-Ji Super Robot Taisen Alpha (2nd Super Robot Taisen Alpha / SRW Alpha 2)
- **Plateforme** : PlayStation 2, Banpresto, 2003
- **Serial requis** : **SLPS-25228** (édition standard). À exclure : SLPS-25227 (Collection Gear Box), SLPS-73206 (The Best).
- **Volume de texte** (chiffres du projet EN) : 69 715 chaînes principales + ~28 782 dialogues de bataille, 150 chapitres.

## Projet anglais (référence directe)

- Auteur : **Gyasuke** — romhacking.net/translations/7745, version 0.8.0 ("Fully Playable", 150/150 chapitres, 69 715/69 715 chaînes).
- Patch : xdelta3 (`reference/english-translation/SRTAlpha2_0.8.0.xdelta`, 2,5 Mo — patch compact car seule les zones de texte changent dans l'ISO).
- **Outils non publics** : le GitHub de Gyasuke ne contient que un repo "Trial". Ses outils d'extraction/insertion sont privés. Son xdelta ne peut PAS être réutilisé pour du français (c'est une diff binaire ISO JP→EN, pas des données de texte).
- Traduction faite avec aide IA (Claude) + vérification manuelle.

## Faits techniques clés (depuis son fil romhacking.net/forum topic 41712)

1. **VN et stratégie dans le même fichier** : contrairement à Alpha DC, la section visual novel (2 textboxes) et la section stratégie sont stockées dans le même conteneur → une seule passe d'extraction couvre tout le script.
2. **Outil maison** (inspiré de closedsockets/dreamcast-translation-kit, code non réutilisé) :
   - extraction/réinsertion du texte ;
   - conversion de la police du jeu en PNG éditable et retour au format original ;
   - système de remplacement : paires de caractères anglais → valeurs de slots vides du font.
3. **La police n'a pas de caractères latins** : le font ne contient que des glyphes japonais (kana, kanji). Le projet EN a travaillé en **majuscules uniquement** pour réduire le nombre de combinaisons, et a déplacé ses mappings dans les slots katakana/hiragana (libres une fois le texte traduit) + un grand espace vide du font.
4. **Codes variables** : des codes inline affichent le nombre d'unités/équipes pouvant encore agir et le numéro du dernier stage terminé — ils ont cassé au premier essai et ont dû être préservés explicitement. À conserver tels quels dans l'extraction FR.
5. **Limites d'octets** : très strictes (1 à 4 lignes par textbox). Compromis EN : ponctuation répétée réduite (`!!`→`!`, `...`→`..`), abréviations (Federation→Fed, Organization→Org, Neo Zeon→NZeon), noms raccourcis en dernier recours.
6. **Textures** : les lore d'intro sont des textures → le projet EN les gère par remplacement de texture (à prévoir aussi pour FR).

## Références outils publiques

- `closedsockets/dreamcast-translation-kit` (GitHub) — workflow GDI Dreamcast : extraction de chaînes, conversion font↔PNG, réinsertion. Même famille de problèmes, autre plateforme : utile comme modèle d'architecture, pas de code directement applicable au format PS2 de ce jeu.
- Projets SRW PS2 voisins avec outils publics (pour comparer les formats de conteneur) : `retro-trans/SRW-Z` (SRT Z, 134k chaînes), `camd11/srw-og-gaiden-en`, `srwogs2ndeng/og2-translation`.

## Ce qu'il faut de l'utilisateur pour débloquer

1. **L'ISO japonaise SLPS-25228** (dump légal de son propre disque) — déposée dans `work/iso/` (non versionnée).
2. Confirmation du lecteur PS2 cible : PCSX2 (recommandé) — pour calibrer les tests de rendu.

## Prochaines analyses une fois l'ISO en main

- Liste des fichiers de l'ISO, tailles, identification des conteneurs de script (probablement des `.bin`/`.dat` dans le système de fichiers du disque).
- Hexdump + recherche de séquences kana UTF-16/Shift-JIS pour localiser les zones de texte.
- Comparaison avec l'ISO patchée EN (appliquer le xdelta sur notre ISO JP) : la diff JP→EN révèle exactement quels offsets ont changé → carte des zones de texte sans deviner. **C'est la méthode la plus directe** : le xdelta EN sert de "traceur" pour identifier les emplacements du texte.
