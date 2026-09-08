---
name: circuits
description: Circuits — les épreuves / workflows de la tour. Lire, suivre et ne jamais court-circuiter un circuit sans autorisation d'la personne. À invoquer dès qu'on parle de publier, déployer, valider ou passer en prod. Les circuits vivent dans Odoo, pas dans des fichiers.
---

# Circuits — les épreuves de la tour

Un circuit est un **chemin obligatoire** entre une intention et une action
publique. On ne le saute pas. On ne le raccourcit pas. On le suit, ou on s'arrête
et on nomme la porte bloquée.

## Ce qu'est un circuit

Les circuits vivent dans la **base Odoo**, pas dans des fichiers texte.
Quatre modèles :

| Modèle | Rôle |
|--------|------|
| `circuit.modele` | Le gabarit : quelles étapes, dans quel ordre |
| `circuit.etape` | Une porte : ce qu'on doit faire/prouver pour passer |
| `circuit.instance` | Un circuit en cours (pour un article, un déploiement…) |
| `circuit.passage` | La trace : qui a franchi quelle porte, quand |

**Piège connu** : `etape_courante` est un **rang** (position), pas une séquence.
Les séquences valent 10, 20, 30… — toujours vérifier lequel on lit.

## Comment lire les circuits

```sh
python3 ~/outils/carte-tour.py circuit   # vue d'ensemble
~/tour/deploy/tache.sh                   # tâches en cours
```

Ne jamais déduire l'état d'un circuit depuis un fichier texte ou un message.
La source de vérité, c'est Odoo. On lit, on ne suppose pas.

## La règle absolue

> **Ne jamais publier ni déployer en prod hors circuit sans l'autorisation
> explicite d'la personne.**

Le chemin est toujours : **dev → si la personne valide → prod**.

**Il n'y a plus de démo** : supprimée le 05/09/2026. Si une recette ou un
script parle encore de « démo », c'est une survivance — on ne la suit pas.

## Les étapes types d'un circuit de publication

1. **Essai** : le contenu est écrit et posé en essai.
2. **Relecture** : un humain (ou le circuit 38) vérifie avant publication.
3. **Circuit 38 — confidentialité** : si le circuit 38 dit « encore en cours »,
   on s'arrête là et on le dit. Aucune exception, même en mode berzerk.
4. **Feu vert la personne** : autorisation explicite, pas déduite.
5. **Publication** : via le script sanctionné uniquement —
   `~/vitrine/deploy/publier-vitrine.sh`
   (il fige, promeut, régénère le plan du site, teste, et **revient en arrière si rouge**).

## Ce qu'on ne fait jamais

- Pousser en prod depuis la ligne de commande directe sans passer par le script.
- Supposer qu'un feu vert verbal passé suffit pour la prochaine publication.
- Passer une étape parce qu'elle « semble évidente » ou « déjà faite ».
- Déduire l'état d'un circuit depuis un fichier — lire Odoo.
- Créer une « voie rapide » pour une urgence. Les urgences ont leur propre circuit.

## Le canal d'exception (si vraiment bloqué)

Si un circuit est bloqué par une porte technique (service down, outil manquant),
on nomme la porte, on la signale à la personne, et on attend. On ne contourne pas
en silence — c'est exactement ce que les circuits sont censés empêcher.

## Lien avec les autres skills

- **eveil** : lire l'état des circuits AVANT de toucher quoi que ce soit.
- **garde-fous** : le circuit 38 (confidentialité) est un garde-fou non contournable.
