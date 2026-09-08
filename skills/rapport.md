---
name: rapport
description: Écrire le rapport de session quand la personne le demande (« fais ton rapport », « ton rapport de session », « rapporte ta session »). Dépose un fichier dans ~/rapports-sessions/ qui dit ce qui a été fait, ce qui a été montré, ce qui reste, et ce qui attend la main de la personne. Le garde-fou garde-rapport.py refuse de finir le tour tant que ce fichier n'est pas écrit.
---

# Écrire son rapport de session

Quand la personne demande un rapport, tu **dois** écrire un fichier — pas seulement
répondre à l'écran. Le garde-fou `~/.claude/portes/garde-rapport.py` bloque la
fin du tour tant que le fichier n'existe pas. C'est un mur, pas une politesse.

## Où et comment

Un seul fichier, dans le dossier des rapports :

```
~/rapports-sessions/RAPPORT-AAAA-MM-JJ-sujet.md
```

- `AAAA-MM-JJ` = la date du jour, heure de Paris (Europe/Paris).
- `sujet` = deux ou trois mots qui disent de quoi parlait la session.
- On **ajoute**, on n'efface jamais un rapport déjà là.

Ce dossier a une flèche dans Mes travaux : « 13 - Rapports de session Claude ».

## Ce que le rapport contient (court, clair, à hauteur d'enfant de six ans)

1. **Ce que j'ai fait** — les vraies choses finies, une ligne chacune.
2. **Ce que j'ai montré** — les images/pages mises sous les yeux de la personne.
3. **Ce qui reste** — pas fini, et pourquoi.
4. **Ce qui attend TA main** — les gestes que seul la personne peut faire (un secret,
   un clic, une décision, la production), avec la commande exacte s'il y en a une.
5. **Preuves** — chemins de fichiers (en flèches Mes travaux, pas en chemins
   bruts), numéros, heures de Paris.

## Les règles qui s'appliquent aussi ici

- **Montrer, pas nommer** : le contenu se lit dans la réponse ; le nom du fichier
  vient après. Voir [[montrer-pas-nommer]].
- **Réponses courtes**, pas de pavé. Voir [[reponses-courtes]].
- **État vérifié** : on ne marque « fait » que ce qu'on a vu ou mesuré. Voir
  [[regle-etat-verifie-et-heure-locale]].
- **Heure de Paris** partout.

## Le geste, à la fin

Après avoir écrit le fichier, dis à la personne en une ligne ce que dit le rapport
et où il est (la flèche 13), puis finis sur la prochaine action.
