---
name: recherche
description: Chercher une trace de travail passé (« qu'est-ce qui a été fait sur X ? », « où est passé Y ? », « on l'avait déjà fait »). Ouvre par la carte vivante — le relevé de ce qui EXISTE — puis descend une liste de lieux dans l'ordre, et ne conclut jamais « pas de trace » sans nommer les lieux interrogés, leur date, et les portes restées fermées. À invoquer AVANT le premier grep.
---

# Chercher

Le défaut à éviter : partir grepper au hasard dans le premier dossier sous la
main, ne rien trouver, et annoncer « ça n'existe pas ». C'est faux presque à
chaque fois. Ce qui existe est **ailleurs**, pas nulle part.

La règle de la personne (02/08) : **on retient que les choses EXISTENT** — un nom,
une adresse, une ligne. On ne recopie que ce qui sert. Donc la mémoire du
travail n'est pas un gros fichier : c'est un **index**, et l'index s'appelle la
carte vivante.

## Étape 0 — La carte vivante, toujours en premier

La carte vivante est le relevé de ce qui existe **pour de vrai** sur la tour,
pas une note écrite à la main. Elle se refait toute seule.

| Quoi | Où |
|---|---|
| **La vraie carte, vivante** | `https://tour.mon-site.example/tour/cockpit/cartes` — page Odoo interne, derrière la connexion (303 en anonyme = normal). Ne PAS confondre avec la carte publique de la vitrine, destinée aux visiteurs. |
| Le relevé en JSON | `~/atelier/cartes.json` **sur la tour** — copie fichier ; vue VIDE le 18/08/2026 (son générateur `carte-zones.sh` pendait) : vérifier `releve_le` ET que les zones ont des éléments avant de s'y fier |
| Ce qui fabrique les zones | `deploy/carte-zones.sh` |
| Ce qui la rafraîchit chaque minute | `piloter-vivant.py` (cron en place) |
| Le mode d'emploi | lien « guide », en haut à droite, à côté de « fils droits » |

Ses zones : **Les conteneurs**, **Les volumes**, **Les outils**, **Le
pilotage**, **Les circuits**. Un clic sur un circuit allume ses portes : ambre
vif = portes franchies, ambre pâle = portes à venir.

Ce qu'on lui demande, ce n'est pas la réponse — c'est **la direction** : quel
conteneur, quel volume, quel outil, quel circuit porte le sujet. Ensuite on va
lire au bon endroit.

**Ne jamais inventer l'adresse publique de la carte.** Elle est publiée comme
réalisation sur la vitrine : on la relève, on ne la devine pas.

## L'ordre des lieux

On descend, on ne saute pas. À chaque lieu on note **sa date** : un lieu daté
d'hier ne prouve rien sur aujourd'hui.

1. **La carte vivante** (ci-dessus) — pour la direction.
2. **La tour elle-même**, parce que l'essentiel n'est pas dans des fichiers :
   - les circuits en base : `circuit.modele`, `circuit.etape`,
     `circuit.instance`, `circuit.passage` — attention, `etape_courante` est un
     **rang**, pas une séquence (les séquences valent 10, 20, 30) ;
   - les missions et le journal de l'atelier ;
   - les tâches numérotées (`#1432`, `#1230`…) — une demande de la personne devient
     une tâche, et la tâche survit à la conversation ;
   - `~/tour/SESSION.md` **sur le VPS** : c'est le vrai journal, et il est
     toujours plus récent que la copie locale.
3. **Le paquet local** `~/paquet-connaissances/` — utile mais c'est une
   **photo**, rapatriée le 16/08/2026. Toujours annoncer sa date quand on s'en
   sert, sinon on fait passer du vieux pour du frais.
4. **Les historiques de sessions de ce poste** :
   `~/.claude/projects/<votre-dossier>/*.jsonl`. Ce sont des lignes JSON
   très longues ; `grep -n` rend une ligne illisible. Le geste qui marche :

   ```sh
   grep -o -i '.\{300\}le-mot-cherché.\{300\}' fichier.jsonl | head
   ```

   (`-o` = ne montre que ce qui colle ; `.\{300\}` = 300 caractères autour.)
5. **Les autres sessions Claude** — `ListAgents`, puis `SendMessage` sur le nom
   exact. Une session qui a fait le travail sur une autre machine détient ce
   qu'aucun fichier d'ici ne contient. C'est un lieu, pas un dernier recours.
6. **GitHub, dépôts privés compris.** Le compte se lit dans vos réglages.
   Recherche restreinte à un propriétaire :
   `https://github.com/search?q=user%3A<compte>+<mot>&type=repositories`.
   Un dépôt privé ne sort **que** si la porte est ouverte : si le navigateur
   affiche « Sign in to GitHub », le zéro résultat ne veut rien dire — ce n'est
   pas une absence, c'est une porte fermée.
7. **L'écran.** Certains travaux n'ont laissé **aucun fichier** : ils ont eu
   lieu dans une session qui pilotait un logiciel — Chrome piloté, ou
   l'éditeur WinDev piloté (regarder l'écran, cliquer, taper). La trace est
   dans l'historique de **cette** session, sur **cette** machine. Si le lieu
   est hors d'atteinte, le dire, et proposer de refaire le geste.
8. **Lire le web** — quand la chose cherchée vit dehors (une notice, une
   documentation, un service, un concurrent, un benchmark, une compétence
   publique). L'outil opencode s'appelle `webfetch` : on lui donne une URL
   complète, il rend la page en markdown (ou texte, ou html). Côté agents de
   la tour, l'outil s'appelle `lire_web`. Trois règles, sans exception :
   - **Ne jamais répondre de mémoire quand la page existe** — la lire, puis
     citer l'URL d'où vient chaque fait rendu.
   - **Préférer la source de première main** (le site du fabricant, le dépôt
     officiel, la doc officielle) à un forum ou un résumé qui en parle.
   - **Vérifier que la page lue est à jour** : une doc datée d'avant n'est pas
     la version courante. Noter la date du contenu lu, et la rendre.

## Les portes, et qui les ouvre

Une porte fermée n'est pas une réponse. On la nomme, et on demande la clé.

- **La tour** : la clé de votre serveur a une passphrase, donc un `ssh` sans
  agent chargé échoue en `Permission denied (publickey)` alors que la clé est
  bonne. Vérifier d'abord si l'agent existe (`ls ~/.ssh/agent.sock`) ; s'il
  manque, **seul la personne** peut lancer `~/connexion-tour.sh` et taper la
  passphrase. Ensuite :
  `SSH_AUTH_SOCK=~/.ssh/agent.sock ssh mon-serveur '…'`.
  Ne jamais écrire la passphrase sur le disque.
- **GitHub** : ne jamais saisir de mot de passe ni de jeton. Proposer à la personne
  de se connecter lui-même dans le navigateur, ou de lancer `! gh auth login`
  dans la session.

## Deux règles empruntées au moteur `windev`

Le moteur `windev.sh` existe parce que les modèles **inventent des noms qui
n'existent pas**. Il recopie un corpus de 6 284 fonctions WLangage et compare,
avant ET après. La même discipline s'applique à une recherche :

- **Ne pas inventer** un chemin, une adresse, un nom de fichier ni une API
  pour combler un trou. On relève, ou on dit qu'on ne sait pas.
- **Vérifier après**, pas seulement avant : ce qu'on croit avoir trouvé, on le
  confronte au réel (le fichier s'ouvre, la route répond, la commande rend 0).

## Comment on rend la réponse

Trois blocs, courts :

1. **Ce qui existe** — avec le chemin ou l'adresse exacte, et la date.
2. **Ce qui manque** — nommé, pas noyé : « aucune trace de X **dans les lieux
   1, 3 et 4** », jamais « X n'existe pas ».
3. **La porte à ouvrir** — la commande précise, et qui doit la lancer.

Écrit pour être compris par un enfant de six ans : chaque symbole et chaque
sigle décodé au moment où il apparaît. Et on finit sur **la prochaine action**,
jamais sur un bilan.

## Sur ce poste

`nomi` est une petite machine : **pas de sous-agents ici**. On cherche en
direct, ou on fait chercher la tour.
