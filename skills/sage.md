---
name: sage
description: "Le Grand Sage — AVANT de faire une tâche, lire tout ce que la tour sait déjà dessus : les articles publiés, les compétences, les règles, les cahiers de tests, les états datés. À invoquer sur « sage », « lis d'abord », « renseigne-toi avant », ou dès qu'une tâche touche un sujet sur lequel la personne a déjà écrit. Rend ce qu'il a trouvé, puis seulement après on agit."
---

# Sage (大賢者) — lire avant d'agir

Le Grand Sage de la tour. Il ne fait rien lui-même : il **lit tout ce qui
existe déjà** sur le sujet, le résume en règles applicables, et rend la main.

## Pourquoi il existe

Écrit le 08/09/2026, sur demande d'la personne. Ce jour-là il a dû dire, une par
une : « va lire les articles des tests », « lis encore berzerk et mode auto »,
« et les garde-fous lis », « va lire les articles circuits ». Quatre demandes
pour une seule chose : **ne pas travailler à côté de ce qu'il a déjà écrit**.

Une session qui n'a pas lu refait des erreurs déjà payées. Une session qui a
lu applique une doctrine au lieu d'improviser. La différence ne se voit pas
dans le code — elle se voit dans le nombre de fois où la personne doit répéter.

## Ce que tu fais, dans cet ordre

### 1. Nommer le sujet en un mot

Avant de chercher, écris la phrase : « le sujet, c'est X ». Un seul.
Si la tâche en touche deux, tu fais deux passages, pas un mélangé.

### 2. Chercher dans les CINQ endroits, toujours les cinq

Aucun n'est optionnel. Un endroit sauté est une erreur qui revient.

| Où | Ce qu'on y trouve | Comment |
|---|---|---|
| **Les articles publiés** | ce qu'la personne a compris et rendu public | `~/vitrine/prod/article-*.html` — chercher par titre ET par contenu |
| **Les compétences** | la méthode déjà écrite | `~/.claude/skills/*/SKILL.md` |
| **Les spécifications** | ce qu'une compétence autorise vraiment | `~/tour/specs/COMPETENCE-*.md` |
| **Les règles qui priment** | ce qu'on ne contourne jamais | `~/CLAUDE.md`, `~/tour/CLAUDE.md`, `~/tour/AGENTS.md` |
| **Les cahiers de tests** | la preuve déjà exigée sur ce sujet | `~/tour/deploy/recettes/*.sh`, `~/tour/deploy/test-*.sh` |

Chercher **par le contenu, pas seulement par le nom du fichier**. Un article
sur les tests peut s'appeler « le tunnel qui revenait ».

### 2 bis. LA QUESTION QU'ON OUBLIE : où ai-je le droit d'écrire ?

Payée deux fois le 08/09/2026, sur la même journée :

- une session a réparé trente pages **directement dans `~/vitrine/prod/`**.
  La production est une *copie* de `~/vitrine/essai/` : la prochaine
  publication effaçait 4 036 fichiers, dont un site entier ;
- la même session a écrit six fichiers **directement dans `~/tour/`**.
  La règle 0 de `~/tour/CLAUDE.md` l'interdit en toutes lettres : ce dossier
  est celui que l'application lit, et un garde empêche de l'enregistrer —
  donc le travail reste en l'air. Neuf fichiers étaient dans ce cas.

**Avant la première écriture, répondre à voix haute :**

| Ce qu'on touche | Où on écrit VRAIMENT |
|---|---|
| Le site | `~/vitrine/essai/` — jamais `prod/`, qui en est une copie |
| Le code de la tour | un chantier : `bash ~/tour/scripts/chantier.sh ouvrir <nom>` |
| Un membre de l'équipe | `equipe.recrutement` → fiche Décisions → embauche |
| Ce qui part en public | jamais sans l'accord explicite d'la personne |

Si la réponse n'est pas certaine, on la cherche avant d'écrire une ligne.

### 3. Lire pour de vrai

Pas le titre. Pas le premier paragraphe. **Le texte.** Un article d'la personne fait
trente lignes : il n'y a aucune excuse à ne pas le lire en entier.

### 4. Rendre trois choses, et rien d'autre

1. **Ce que j'ai lu** — la liste, avec le nombre de textes.
2. **Les règles qui s'appliquent à CETTE tâche** — une ligne chacune, avec
   d'où elle vient. Pas de résumé général : seulement ce qui change ce que
   je vais faire.
3. **Ce que ça m'interdit de faire** — la liste des gestes que la doctrine
   exclut. C'est la partie la plus utile, et celle qu'on oublie.

Puis **on s'arrête** et on annonce la première action. Le Sage ne construit
pas : il évite de construire à côté.

## Ce que tu ne fais jamais

- Dire « j'ai regardé » sans citer ce qui a été lu, et combien.
- Résumer un article dans un sens qui arrange la tâche du jour.
- Sauter un des cinq endroits parce que « ça n'a sûrement rien ».
- Inventer une règle qui n'est écrite nulle part. Une règle sans source
  n'existe pas — on dit « je n'ai rien trouvé sur ce point ».
- Enchaîner sur la construction sans avoir rendu les trois choses.

## Les raccourcis mesurés (au 08/09/2026)

Ce que le Sage trouve déjà, pour éviter de le chercher deux fois :

- **Tests** — quatre articles : « écrire les tests d'abord », « combien de
  tests lancer », « rejouer un test », « le tunnel qui revenait ». En un
  mot : la preuve s'écrit AVANT le code ; le nombre d'essais se choisit par
  le risque (1 déterministe, 3-5 instable, 5-20 critique, 30+ statistique) ;
  un vert qui ne prouve rien est pire qu'un rouge ; on regarde une
  **deuxième** fois, plus tard.
- **Autonomie** — `COMPETENCE-BERZERK` (écrit vraiment, seulement sur accord
  explicite) et `COMPETENCE-MODE-AUTOMATIQUE` (décide seul, mais dans le
  cadre ; l'argent, le contact externe et la publication non validée
  reviennent toujours à la personne).
- **Garde-fous** — cinq non négociables : jamais un secret en clair ; un seul
  objectif à la fois ; ne pas dire « c'est fait » sans avoir regardé l'écran ;
  écrire le prompt en entier, jamais un chemin de fichier ; clarté six ans.
- **Circuits** — voir la compétence [[circuits]] : rien ne part en public
  sans franchir ses portes, et les circuits vivent dans la tour, pas dans
  des fichiers.

Compétences sœurs : [[eveil]] pour l'état réel de la machine avant d'agir,
[[garde-fous]] pour les cinq règles mécaniques, [[kotodama]] pour ce qu'la personne
a demandé et qui reste ouvert.
