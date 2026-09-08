---
name: eveil
description: S'éveiller à l'état RÉEL de la tour (le VPS) AVANT d'agir dessus. À invoquer dès qu'on va toucher au serveur, à la vitrine, aux circuits, au pare-feu ou aux conteneurs. Ouvre la porte de la tour, lit la carte vivante, les outils, les circuits et le pare-feu dans le bon ordre, et rappelle les règles qui font qu'on ne se trompe pas. Le but : ne jamais agir en aveugle.
---

# Éveil — se réveiller sur la tour avant d'agir

Le défaut à éviter : foncer taper une commande sur le serveur sans avoir ouvert
la porte ni lu l'état. On casse, ou on annonce faux. **On s'éveille d'abord.**
On agit après. L'éveil se fait dans cet ordre, chaque pas avec sa **preuve**.

## Le rituel complet (trois compétences enchaînées)
Comme une tour de contrôle : les mêmes gestes, le même ordre, à chaque fois.
1. **éveil** (ci-dessous) — ouvrir la porte, lire l'état.
2. **[[presentation]]** — me présenter pareil à chaque fois : qui je suis, ce que j'ai
   en main, ce que je vois, ce que je peux / ne peux pas.
3. **[[mes-outils]]** — montrer mes outils par familles, puis demander laquelle ouvrir.
Après avoir lu l'état, j'enchaîne **toujours** sur `presentation`, puis j'offre `mes-outils`.

## Piège n°0 — je suis root, `~` ment
Sur nomi je tourne en **root** : `~` vaut `/root`, PAS `~`. Toujours
écrire les chemins en entier : `~/...`, `~/.claude/skills/...`.
Sur la tour, l'utilisateur est **ubuntu** : là `~` vaut `~`.

## Pas 1 — Ouvrir la porte de la tour
```sh
SSH_AUTH_SOCK=~/.ssh/agent.sock ssh mon-serveur 'hostname; uptime'
```
- **Preuve de réussite** : le nom du serveur répond (`vps-0ceddf17`) avec sa durée d'allumage.
- **Si « Permission denied (publickey) »** : la clé n'est PAS chargée dans l'agent.
  Ce n'est pas une mauvaise clé. → Demander à la personne de lancer une fois
  `~/connexion-tour.sh` (il tape sa **phrase secrète**, ça ouvre l'agent).
  **Ne jamais écrire la phrase secrète sur le disque.** Ne pas conclure « la clé est morte ».

## Pas 2 — Lire la CARTE VIVANTE, en premier, toujours
La carte est le relevé de ce qui EXISTE sur la tour. On la LIT, on ne la devine jamais.
```sh
SSH_AUTH_SOCK=~/.ssh/agent.sock ssh mon-serveur 'python3 ~/outils/carte-tour.py'        # le résumé
SSH_AUTH_SOCK=~/.ssh/agent.sock ssh mon-serveur 'python3 ~/outils/carte-tour.py <un mot>' # chercher dedans
```
- **Preuve** : le total des éléments et les zones s'affichent (webapps, façades, équipe, pilotage, serveurs, conteneurs, volumes, outils, circuits).
- **Règles dures** : ne jamais deviner le nom d'un champ ; « zéro trouvé » veut dire
  « absent de la carte », pas « ça n'existe pas » — alors on NOMME la porte qu'on n'a pas ouverte.
  Ne jamais déduire un produit d'une seule de ses fonctions : on lit la description entière, ou on demande.
- **Contrôle** : `SSH_AUTH_SOCK=... ssh mon-serveur 'bash ~/outils/test-carte-tour.sh'` doit passer au vert.

## Pas 3 — Mes outils (avant d'inventer une commande)
La zone « Les outils » liste ce qui est déjà écrit (~260). On s'en sert plutôt que
de bricoler.
```sh
SSH_AUTH_SOCK=~/.ssh/agent.sock ssh mon-serveur 'ls ~/outils/'
```
- **Preuve** : la liste des outils existants. Si un outil fait déjà le travail, on l'utilise.

## Pas 4 — Les circuits (les épreuves)
Les circuits vivent dans la base Odoo, pas dans des fichiers : `circuit.modele`
(le gabarit), `circuit.etape` (la porte), `circuit.instance` (en cours), `circuit.passage`.
Attention : `etape_courante` est un **rang**, pas une séquence — les séquences valent 10, 20, 30.
On les lit par la carte (`carte-tour.py circuit`) ou par `~/tour/deploy/tache.sh`.
- **RÈGLE DURE** : ne jamais publier ni déployer en prod **hors circuit** sans
  l'autorisation **explicite** de la personne. Pour pousser sans feu vert, il faut le
  DEMANDER et utiliser la compétence **bypasse** — c'est le seul chemin.

## Pas 5 — Le pare-feu (déclaratif)
Le pare-feu se DÉCLARE, il ne se bricole pas. Une règle `ufw` posée à la main
**disparaît en ~15 minutes** (une remise en ordre automatique la balaie). Tout se
déclare dans `deploy/security/pare-feu.sh`.
- **Preuve avant de toucher** : lire ce fichier ; toute modif du pare-feu passe par lui, jamais par une commande `ufw` directe.

## Pas 6 — Publier proprement (le bon chemin, pas le raccourci)
- **Vitrine** (le site public) : un seul chemin sanctionné, `~/vitrine/deploy/publier-vitrine.sh` —
  il fige, promeut l'essai → la prod, régénère plan du site + flux RSS, lance le banc de test,
  et **revient en arrière si c'est rouge**. Les articles vitrine **n'ont pas de date**.
- **Le reste** : par les circuits.
- **Classifieur dev/prod sur nomi** : écrire dans `~/dev` du VPS passe ; `~/demo`, `~/tour`
  et les scripts de sécurité sont **bloqués** → on prépare en dev, **la personne publie**.

## Règles transverses (toujours vraies)
- **Heure = Europe/Paris.** Tout horodatage lu en UTC / suffixe `Z` se convertit avant
  d'être rapporté : `date -d '2026-08-20T05:58:33Z'` rend l'heure locale. Jamais brut.
- **État = lire jusqu'au bout, depuis la source.** Fil d'e-mails entier, historique complet,
  fichier entier. La fin de ce qu'on a récupéré n'est PAS la fin de la conversation.
- **Tout service tourne en conteneur.** L'utilisateur `ubuntu` a `sudo` sans mot de passe et
  le groupe docker : une faille qui sort d'un conteneur = **toute la machine**. Prudence maximale.
- **Secrets** : ils restent dans `~/tour/.env` **sur le VPS**. On ne les recopie jamais sur nomi.
- **Vérifier un rendu** : dans un vrai navigateur. Sans écran, chromium en mode headless sur le
  VPS : `chromium --headless --disable-gpu --no-sandbox --virtual-time-budget=15000 --dump-dom <url>`.

## Ce qui se transporte partout, et ce qui reste ici (03/09/2026)
Un jour, éveil pourra servir ailleurs (une autre boîte, un vrai système
d'entreprise). Alors il faut garder le **geste sûr**, et NE PAS transporter le
**protocole de ce poste-ci**.

**Le geste sûr — vrai partout, à garder :**
- lire l'état **avant** d'agir ; montrer une **preuve** ; être **reproductible** ;
- « **zéro trouvé ≠ ça n'existe pas** » ; un outil qui **refuse de mentir** (il
  s'arrête avec une erreur au lieu d'inventer) ;
- lire **jusqu'au bout, depuis la source**, dans le **bon fuseau horaire**.

**Le protocole de CE poste — à réécrire ailleurs, pas à copier :**
- « le **feu vert oral** de la personne » → une **autorisation vérifiable** (un
  ticket, une demande de changement, une liste de droits) que l'agent peut prouver
  AVANT d'agir.
- « la **carte unique** » → les **vraies sources**, en **traçant** lesquelles on a lues.
- le **bypass** (passer outre) comme voie normale → **interdit** : en entreprise,
  contourner une porte = un **incident** ; la sortie de secours est un **vrai canal
  d'exception**, lui-même **contrôlé**.
- « **sudo sans mot de passe + docker** » (être root sur toute la machine) → des
  **droits limités à SA tâche** (moindre privilège), jamais la machine entière.

## Clôture de l'éveil
Une fois l'état lu, j'enchaîne sur **[[presentation]]** (le bloc fixe en quatre temps),
puis je propose **[[mes-outils]]**. La toute première ligne dit : **porte ouverte**
(nom du serveur) + **carte lue** (date du relevé). Puis seulement, on agit.
