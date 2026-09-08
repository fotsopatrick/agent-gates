---
name: carte-vivante
description: Généraliser la « carte vivante » de la tour sur un système neuf — une source de vérité dynamique nourrie par les sources réelles (conteneurs, webapps, serveurs, équipe, outils, circuits), servie par une API, et séparée de la doctrine (ACL). À invoquer quand la personne veut la carte « dynamique », « vivante », « brancher une carte sur un nouveau système », ou « généraliser la carte vivante ». Comprend le moteur de collecte, l'API de lecture, la doctrine, et un jeu de tests local.
---

# Carte vivante dynamique — généralisation sur un système neuf

## Pourquoi cette compétence existe

La tour a une **carte vivante** (`cartes.json` régénérée chaque minute, lue par
`carte-tour.py`). Elle marche parce que le système est à la taille d'une
personne : un fichier unique, maintenu par un processus, autorité humaine.

Le défaut à éviter en la transposant ailleurs : **emporter le fichier JSON
maison** et l'éditer à la main, ou croire qu'une « carte » unique suffit dans
un gros SI. On généralise **l'idée**, pas l'outil.

Cette compétence livre un **prototype fonctionnel** (module `system/carte_vivante/`)
qui implémente les cinq principes, testé en local. Elle répond au rapport
`rapportEveil.txt` : on garde ce qui est sûr partout (lire avant d'agir,
tracer, refuser de mentir), on ne transporte pas les conventions du poste
(bout d'un seul humain, feu vert oral).

## Les cinq principes (le contrat)

1. **Collecte ≠ lecture.** La carte n'est plus un fichier qu'on édite : c'est
   le **résultat d'un collecteur**. L'extracteur écrit un état ; personne ne
   le saisit.
2. **Nourrie par les sources réelles, pas à la main.** Chaque zone a SA source
   (voir `carte_vivante/sources.py`) :
   - conteneurs → API du scheduler (Docker / K8s) ;
   - webapps → déclaration infra (Terraform) ou reverse-proxy (Caddy) ;
   - serveurs → inventaire agentisé / CMDB ;
   - équipe / circuits → base applicative (ex. Odoo) ou répertoire ;
   - outils → arborescence des scripts + descripteurs.
   Le collecteur interroge et **fusionne** dans un schéma commun
   `{zone, noeuds, liens, horodatage}`.
3. **Le rafraîchissement est un événement, pas un timer.** Une source signale
   un changement → on recalcule la ou les zones touchées. Chaque entrée a un
   `interroge_le`. Pas de scrutation inutile.
4. **Une API de lecture, pas un fichier.** `GET /carte` sert la carte à jour,
   avec `releve_le` + un **hash de cohérence**. La lecture est identique d'un
   système à l'autre ; seul le collecteur change.
5. **Inventaire ≠ doctrine.** La carte dit ce qui EXISTE ; la doctrine dit QUI
   peut LIRE QUOI. L'accès passe par une ACL déclarative
   (`carte_vivante/doctrine.py`), pas par un « feu vert oral ». Et la carte
   garde la liste des **sources interrogées + leur date** (règle d'or :
   *zéro trouvé ≠ ça n'existe pas* — on nomme la porte qu'on n'a pas ouverte).

## Règle d'or (héritée de la tour)

La carte **ne ment jamais** : elle refuse (`code d'erreur ≠ 0`) une carte vide
ou mal formée plutôt que de servir un faux « il n'y a rien ». « Zéro trouvé »
veut toujours dire « absent de la carte / porte non ouverte », jamais
« ça n'existe pas ».

## Architecture

```
system/
  carte_vivante/
    collecte.py      moteur : interroge les collecteurs, fusionne, fige (hash)
    base.py          schéma commun + contrôle d'intégrité (refuse de mentir)
    sources.py       registre des sources réelles → zone (le « et-ia »)
    api.py           GET /carte, /carte/<zone>, /sante, /sources (HTTP)
    doctrine.py      ACL : qui peut lire quoi (inventaire ≠ doctrine)
    cli.py           lire en résumé / chercher un mot (équivalent carte-tour)
    collecteurs/
      mock/          collecteurs simulés (docker/K8s/CMDB/base/fs)
      vide/          collecteur « rien » pour prouver qu'on ne ment pas
  tests/
    test_carte_vivante.py   le parcours réel (voir « Vérifier »)
    test_carte_vivante.sh   enveloppe bash
  specs/COMPETENCE-CARTE-VIVANTE.md   (cette spec détaillée, si besoin)
```

## Vérifier (règle du poste : tests d'abord, livraison = tests verts)

```sh
cd system && python3 tests/test_carte_vivante.py
# ou
bash tests/test_carte_vivante.sh
# → attendu : « TOUT EST VERT » (23 contrôles)
```

Les tests prouvent le parcours réel :
- une collecte produce une carte valide au schéma commun ;
- une source vide renvoie une erreur (on ne ment jamais) ;
- le hash + le relevé sont exposés et cohérents ;
- un événement sur UNE source change le hash (recalcul vivant) ;
- la doctrine accorde/refuse la lecture ; les sources interrogées sont tracées.

## Usage (prototype local)

```sh
# 1. Produire la carte (collecte, découplée de la lecture)
python3 system/carte_vivante/collecte.py --sources mock --sortie /tmp/carte.json

# 2. La lire en résumé / en cherchant un mot
python3 system/carte_vivante/cli.py --sortie /tmp/carte.json
python3 system/carte_vivante/cli.py --sortie /tmp/carte.json caddy

# 3. La servir par une API (GET /carte, /sante, /sources, /carte/<zone>)
python3 system/carte_vivante/api.py --sortie /tmp/carte.json --port 8777
curl http://127.0.0.1:8777/carte

# 4. Simuler un changement de source (événement) → recalcul ciblé, hash change
python3 system/carte_vivante/collecte.py --sources mock \
  --evenement "conteneurs:deploye:web-crm" --sortie /tmp/carte.json

# 5. Vérifier l'ACL (inventaire ≠ doctrine, refus par défaut)
python3 system/carte_vivante/doctrine.py --role membre --action lecture-carte
python3 system/carte_vivante/doctrine.py --role visiteur --action lecture-carte
```

## Brancher une source RÉELLE (hors prototype)

Ajouter un collecteur dans `collecteurs/<groupe>/col_<zone>.py` qui expose
`collecter(contexte) → (noeuds, liens)`, en interrogeant la vraie source :
Docker/K8s, Terraform, CMDB, base applicative, système de fichiers. Le reste
de la carte ne change pas : c'est la définition même du « nouveau système ».

## Ce qui est sûr partout / ce qui ne l'est pas

À **garder** dans toute transposition : lire l'état avant d'agir, tracer
(sources + horodatage dans le fuseau de l'utilisateur), refuser de mentir,
reproductible, doctrine et ACL déclaratives, refus par défaut.

À **réécrire** pour un SI d'entreprise : le storage de fichiers → une vraie
base/objet ; l'authentification des rôles → couche d'identité externe
(SSO/OIDC) ; les événements de sources → un bus/queue réel. La philosophie
« une porte qui refuse fait son travail » reste, mais **sans** contournement :
l'exception passe par un canal auditable, jamais par un bypass silencieux.

## Fichiers connexes

- `rapportEveil.txt` (bureau) : l'analyse de laquelle ce prototype est tiré.
- `system/carte_vivante/sources.py` : le catalogue des sources réelles.
- `system/carte_vivante/doctrine.py` : l'ACL à entretenir (déclarative).
