---
name: fusion-sessions
description: Fusionner toutes les sessions Claude ouvertes en une seule. À invoquer quand la personne dit « trop d'onglets », « fusionne mes sessions », « fais le point de toutes mes sessions », ou avant de fermer des onglets. Produit un rapport (ce qui est fait, ce qui reste, ce qui attend sa main), les preuves à fournir, et le texte prêt à coller dans une nouvelle session.
---

# FUSIONNER MES SESSIONS

la personne, le 06/09/2026 : « y'a trop d'onglets Claude ouverts ». Chaque onglet
sait ce qu'il fait ; personne ne sait ce que font tous les onglets ensemble.

## La règle : on lit, on n'invente pas

Deux sources, et deux seulement :

1. **Le carnet** — `~/livrables/tableau-de-bord/sessions/*.json`. Chaque tâche
   y porte son état : `reste`, `encours`, `fait`, `bloque`. C'est la source
   propre, écrite par les sessions elles-mêmes.
2. **Les journaux des onglets** — `~/.claude/projects/*/*.jsonl`. Un journal
   touché récemment = un onglet encore ouvert. On y prend la dernière demande
   de la personne, rien d'autre.

Ce qu'on n'a pas pu lire, on le **dit**. On n'écrit jamais « tout va bien »
parce qu'on n'a rien vu. Voir [[un-defaut-se-repare-pas-se-raconte]].

## Le geste

```
python3 ~/outils/fusionner-sessions.py            le rapport entier
python3 ~/outils/fusionner-sessions.py --prompt   seulement le texte à coller
```

Le rapport et le texte sont gardés dans `~/livrables/fusion-sessions/`, avec
leur heure. Rien ne s'efface : on ajoute.

Son épreuve : `python3 ~/controles/test-fusion-sessions.py` — cinq contrôles.
Deux d'entre eux sont des pièges : l'outil doit dire qu'il est aveugle quand
il ne voit rien, et il ne doit pas rendre un texte vide.

## Ce que la personne voit

- **Un bouton** dans son cockpit, `http://127.0.0.1:8790/` : « Fusionner mes
  sessions Claude ». Il le clique, le rapport s'écrit, le dossier s'ouvre.
- **Dans Mes travaux** : la flèche « 19 - Fusion de mes sessions », et deux
  entrées sur la page d'accueil.

On ne lui donne **jamais** une commande à taper. Voir
[[jamais-de-commande-a-la personne]].

## Ce qu'il faut vérifier avant de rendre le rapport

1. Le nombre d'onglets annoncé correspond bien aux journaux récents.
2. Chaque tâche `bloque` dit **pourquoi** elle attend sa main — sinon la
   corriger dans le carnet avant de rendre le rapport.
3. Chaque tâche qui reste porte une **preuve attendue**. Si l'outil écrit
   « À ÉCRIRE », c'est une vraie dette : la phrase manque, il faut l'écrire
   en une ligne — ce qu'on verra à l'écran quand ce sera fini.

## Après la fusion

Le texte produit commence par la règle du travail : écrire le test avant, et
ne jamais rendre une commande. Ce n'est pas décoratif — c'est ce qui empêche
la nouvelle session de refaire les fautes des précédentes.
