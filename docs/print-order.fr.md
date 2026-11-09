# Ordre d'impression : RackMate TT couché, Centauri Carbon 2, version écrous M5

Fichiers : `stl/print-sets/centauri-carbon-2/<1U|2U|3U>/`. Il y a un dossier par hauteur (`1U`, `2U`, `3U`), et chacun contient tout ce qu'il faut pour cette hauteur.
Les numéros donnent l'ordre d'impression.

Réglages pour toutes les pièces : PETG, 4 parois, 30 % gyroïde, couches de 0,2 mm, **sans supports**, à imprimer telles quelles (déjà orientées).

## Avant tout : 1 minute avec une règle

L'entraxe des trous des pieds a été mesuré sur le plan officiel (DP-0054), pas sur ton TT. Retourne le TT ou regarde dessous, puis mesure de centre à centre entre les vis des pieds :

- [ ] gauche ↔ droite : **248,5 mm** attendus (le trou de la rehausse tolère ±1 mm) ;
- [ ] avant ↔ arrière : **130 mm** attendus (aucune tolérance) ;
- [ ] les pieds sont bien vissés dans le panneau du dessous du TT couché, et pas dans les cadres avant et arrière.

Si une de ces mesures ne correspond pas, ne lance rien : il faut corriger le script.

## N°1 ensuite, avant de lancer la nuit

`1_test_fit.stl` dure environ 30 min, imprime-la seule. Avant de lancer le reste :

- [ ] un écrou M5 entre dans sa fente ;
- [ ] la pièce posée sous le TT, à la place d'un pied : la vis M4 entre dans le trou du pied ;
- [ ] un écrou M4 tient dans le logement du pied.

## Ensuite, par hauteur

| Hauteur | TT final | Plateau de la nuit | Plateau suivant | Filament total |
|---|---|---|---|---|
| **1U** | 4U | n° 2 + 3 + 4 + 5 ensemble | (rien) | ~185 g |
| **2U** | 5U | n° 2 + 3 + 4 + 5 ensemble ¹ | (rien) | ~225 g |
| **3U** | 6U | n° 2 + 4 + 5 | n° 3 | ~270 g |

¹ En 2U, ça rentre de justesse : 224 × 238 mm sur 256, vérifié par le script. Si l'arrangement automatique du slicer n'arrive pas à tout placer, reproduis la disposition de `docs/images/2U/04_bed_night_2U.png` : les 2 côtés et la n° 4 debout côte à côte, et la n° 5 couchée au-dessus des côtés.

En 3U, les 2 côtés côte à côte font 267 mm, ce qui dépasse le plateau. Il faut donc 2 nuits, ou une nuit et une journée.

Les n° 4 et 5 (traverse A et B) sont le même fichier en double. Il en faut 2 identiques : au montage, on en retourne une.

## Rendus

Ils sont dans `docs/images/<1U|2U|3U>/`, un dossier par hauteur :

| Image | Contenu |
|---|---|
| `01_tt_on_riser_…_total_…U.png` | le TT couché posé sur la rehausse, vu de 3/4 avant |
| `02_riser_…_rear.png` | la rehausse seule, vue de l'arrière avec la traverse |
| `03_front_….png` | la façade |
| `04_bed_night_….png` | la disposition des pièces sur le plateau 256 de la nuit |
| `05_bed_next_3U.png` | 3U uniquement : le 2e plateau (n° 3) |

Couleurs sur les vues de plateau : bleu = n° 2, orange = n° 3, vert foncé = n° 4, vert clair = n° 5.
