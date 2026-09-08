---
name: imprimer
description: Mettre un texte en PDF propre (CV, rapport, lettre, mode d'emploi, facture), sans navigateur et sans rien de payant, puis le MONTRER en image. À invoquer quand la personne dit « fais-moi un PDF », « mets ça en PDF », « imprime ce document », « un CV en PDF », ou quand un livrable doit partir chez quelqu'un d'extérieur. Ne jamais répondre « je ne sais pas faire de PDF ».
---

# Imprimer — mettre un texte en PDF

## L'outil

`~/outils/faire-pdf.py` transforme un texte simple en PDF mis en page.

```sh
python3 ~/outils/faire-pdf.py mon-texte.md ~/livrables/mon-doc.pdf --titre "Mon document"
```

Chaque morceau : `mon-texte.md` = le texte d'entrée ; le deuxième chemin = le PDF
qui sort ; `--titre` = le nom qui s'affiche dans l'onglet du lecteur de PDF.
Option `--marge 15` pour serrer la page (en millimètres, 18 par défaut).

**La preuve de réussite** : l'outil affiche le chemin du PDF, et
`pdfinfo mon-doc.pdf` annonce au moins une page.

## Ce que le texte d'entrée sait faire

```
# Grand titre          ## Partie          ### Sous-partie
- une puce             1. une liste numerotee
**gras**   *italique*  `code`   [lien](https://exemple.fr)
> une citation
---                    (un trait de separation)
\pagebreak             (passer a la page suivante)
```

Tout le reste devient un paragraphe justifié.

## La règle : MONTRER le PDF, pas le nommer

Un PDF ne se juge pas sur son nom. Après l'avoir fabriqué, **en faire une image
et l'afficher dans la réponse** :

```sh
pdftoppm -png -r 100 ~/livrables/mon-doc.pdf /tmp/apercu
```

Puis lire `/tmp/apercu-1.png` pour le montrer. Sans cette image, on n'a pas vu
si c'est beau ou cassé. Voir [[montrer-pas-nommer]] et [[lire-nest-pas-voir]].

## Où déposer le PDF

Toujours dans `~/livrables/`. la personne le retrouve par **Mes travaux, flèche 1 -
A lire et a montrer**. On lui parle en flèches, jamais en chemins.

## Une mise en page plus riche (CV, plaquette)

Quand le texte simple ne suffit pas — bandeau, deux polices, sections serrées —
on écrit la page directement en Python avec `reportlab`. Le patron réutilisable :

```sh
~/miniconda3/bin/python3 ~/outils/modeles-pdf/generer-cv-fr.py   # CV français
~/miniconda3/bin/python3 ~/outils/modeles-pdf/generer-cv-en.py   # CV anglais
```

La mise en page commune est dans `~/outils/modeles-pdf/mise-en-page-cv.py` :
on y change les couleurs, les marges et les tailles une seule fois pour les deux.

## Si l'outil se plaint

Il lui faut la bibliothèque `reportlab`. Elle est déjà posée dans le Python de
miniconda sur nomi, et l'outil s'y branche tout seul. Ailleurs :

```sh
python3 -m pip install --user reportlab
```

## Interdits

- **Ne jamais ouvrir un navigateur** (ni Chrome, ni `xdg-open`, même caché) pour
  fabriquer un PDF. Cet outil n'en a pas besoin. Voir [[interdiction-ouvrir-navigateur]].
- Ne jamais rendre un PDF sans l'avoir regardé en image d'abord.

## Le contrôle

```sh
bash ~/outils/test-faire-pdf.sh
```

Doit finir sur `VERT : l'outil PDF marche.` — 7 contrôles, dont le saut de page
et la disparition des étoiles du gras.
