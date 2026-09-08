---
name: courrier
description: Envoyer un courrier depuis la tour — pour la porte des études, les agents, les rapports et les alertes. À invoquer dès qu'on parle d'« envoyer un mail », « le code n'arrive pas », « l'alerte n'est pas partie », « prévenir par courriel », ou quand un envoi échoue. Ne jamais répondre « je ne sais pas envoyer un courrier ».
---

# Envoyer un courrier depuis la tour

**Règle absolue : on ne dit JAMAIS « la tour ne sait pas envoyer de mail ».**
Il y a quatre routes. Trois sont mortes, et on sait pourquoi. La quatrième
marche. Cette page dit laquelle prendre et comment le prouver.

## 1. L'outil à utiliser, et lui seul

    echo "le texte du message" | python3 ~/tour/deploy/envoyer-courrier.py "Le sujet" qui@exemple.fr

Il rend `COURRIER -> qui@exemple.fr | depuis ... | parti` quand c'est fait.
Sinon il **nomme chaque serveur qui a refusé et pourquoi**. Un outil qui
échoue en silence ne sert à rien : celui-ci parle.

Il essaie quatre portes, dans cet ordre, et s'arrête à la première qui
s'ouvre :

1. un mot de passe rangé dans un fichier chez nous ;
2. celui de la boîte `contact@mon-site.example`, **ouvert directement
   dans le coffre de la tour** ;
3. celui d'application Gmail, ouvert dans le coffre lui aussi ;
4. les serveurs déjà configurés dans la tour.

Rien de tout cela n'est **jamais** affiché, recopié, ni écrit dans un
journal. C'est ouvert au moment de l'envoi et oublié juste après.

## 2. Les trois routes mortes — ne pas les réessayer

**Demander à la tour de poster le courrier** (l'ancien `mail-rapide.py`).
La tour refuse : le compte technique `tuyau` n'a pas le droit de créer un
courrier sortant. Son message exact : « Vous n'êtes pas autorisé à créer des
enregistrements 'Outgoing Mails' ». Ce droit appartient au groupe
Administration. Mesuré le 07/09/2026, après quatre codes d'entrée jamais
partis entre 23 h 12 et 01 h 23.

**Poster un message à un contact** (la voie normale d'Odoo). Refusée aussi :
le même compte ne peut pas créer de contact.

**Le facteur de la machine** (`sendmail`, `postfix`). Il prend le courrier,
mais Gmail le rejette : *« Your email has been blocked because the sender is
unauthenticated »*. Essayé deux fois — au nom du domaine, puis au nom de la
machine — refusé deux fois. La règle du domaine (`v=spf1 include:mx.ovh.com
-all`) n'autorise **que** les serveurs d'OVH à écrire en son nom.

## 3. Quand un envoi échoue quand même

Le guetteur `~/tour/deploy/veille-envoi-courrier.sh` essaie un vrai envoi
chaque matin à 8 h 05. S'il échoue, il **crie** : il écrit un fichier
d'alerte et ouvre une fiche dans la tour. On peut le lancer à la main à
tout moment.

Lire ce que dit le guetteur avant de chercher ailleurs. Il nomme le refus.

## 4. Quand le serveur répond « refusé »

Si le serveur répond `535 Authentication failed`, ce qui est rangé n'est
plus bon. Deux gestes, dans l'ordre :

1. le corriger dans le coffre de la tour — c'est là que tout le monde lit ;
2. ou, en dépannage, le ranger dans le fichier `~/.courrier-contact`,
   avec les droits `600` pour que son seul propriétaire puisse le lire.
   L'outil prend ce fichier en premier.

## 5. Ce qu'on ne fait jamais

- Le recopier dans un message, un journal, ou un enregistrement.
- Dire « le courrier est parti » sans avoir vu la ligne `| parti`.
- Faire crier une alerte par un courrier **sans** garde-fou : si le courrier
  est en panne, l'alerte sur la panne du courrier n'arrivera jamais. Le
  guetteur écrit donc AUSSI un fichier et une fiche.
- Réparer la conséquence : rallonger un délai, retenter en boucle. La cause
  est toujours une **autorisation**, jamais du code.

## 6. Le lecteur devient un contact

Depuis le 07/09/2026, chaque personne à qui la tour écrit entre dans le
carnet d'adresses. La porte des études pose l'étiquette
« Lecteur des etudes ». On les retrouve dans le module Contacts.
Si le droit de créer un contact manque, **le courrier part quand même** :
on le dit, on ne bloque pas.

Compétences sœurs : [[eveil]] pour l'état réel avant d'agir,
[[ovh]] pour tout ce qui touche au domaine et à la signature des courriers.
