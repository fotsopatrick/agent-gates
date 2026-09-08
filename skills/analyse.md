---
name: analyse
description: >-
  Démarche scientifique à suivre pour tout problème posé par la personne : observer,
  formuler des hypothèses, choisir la méthode d'étude adaptée au domaine, tester,
  analyser, conclure. À charger dès qu'un problème demande un diagnostic, une
  cause, un choix entre explications concurrentes, une étude, une mesure, une
  comparaison, ou une panne à élucider — matérielle comme logicielle. Contient la
  table de choix « quel type de problème → quelle méthode ».
---

# La méthode scientifique

## Pourquoi cette compétence existe

Le défaut à corriger : regarder une preuve mince, sortir l'explication la plus
fréquente, et **la donner comme certaine**. Ça produit une réponse propre tout de
suite et fausse une fois sur deux.

Cas fondateur (18/08/2026) : la fixation du ventilateur du Raspberry Pi de malo.
Quatre lectures successives d'une même photo — « chevilles à pincer », « vis »,
« écrou à six pans », « cheville à ressort » — trois fausses, chacune affirmée.
Une heure perdue à forcer sur du matériel avec les mauvaises instructions. La
boîte du kit était sur le bureau : elle donnait la marque, et la notice du
fabricant réglait la question en une ligne.

Ce qui manquait n'était pas de l'information. C'était la **démarche**.

## Les six étapes

1. **Observation** — décrire le phénomène ou le problème, sans l'expliquer
   encore. Séparer ce qui est vu de ce qui est supposé.
2. **Hypothèse** — une explication provisoire. Elle doit être **falsifiable**,
   c'est-à-dire qu'on doit pouvoir imaginer ce qu'on verrait si elle était
   fausse. « Le ventilateur est cassé » est falsifiable : s'il tourne, c'est
   faux. « Il y a un problème quelque part » ne l'est pas : rien ne peut la
   démentir, donc elle ne sert à rien.
3. **Expérimentation** — tester, ou collecter les données qui séparent les
   hypothèses entre elles.
4. **Analyse** — lire les résultats (statistique, qualitative, modélisation).
5. **Conclusion** — valider, rejeter, ou ajuster l'hypothèse.
6. **Communication et reproduction** — dire ce qui a été fait assez précisément
   pour qu'un autre le refasse et obtienne la même chose.

But visé : des connaissances **falsifiables** (on peut imaginer ce qui les
démentirait), **reproductibles** (quelqu'un d'autre refait et retrouve la même
chose) et **objectives** (elles ne dépendent pas de qui regarde).

## Règle des hypothèses concurrentes

Ne jamais avancer une seule hypothèse. En poser **au moins deux**, puis chercher
l'observation qui les **sépare** — c'est elle, et elle seule, qui vaut d'être
allée chercher.

Formulation à tenir face à la personne :

> Ce que je vois : … Ce que ça peut être : A, ou B. Ce qui les sépare : … .

Une observation qui serait compatible avec A **et** avec B ne fait pas avancer.
Ne pas la demander.

## Les familles de méthodes

### 1. Méthodes théoriques

Raisonnement, abstraction, modélisation.

- **Analyse et synthèse** — décomposer l'objet en parties, puis recomposer pour
  comprendre le tout.
- **Induction** — j'ai vu dix cas, j'en tire une règle générale. **Déduction** —
  j'ai une règle générale, j'en tire ce qui doit arriver dans ce cas-ci.
  L'induction peut se tromper (le onzième cas dément la règle), la déduction
  non — mais seulement si la règle de départ est juste.
- **Modélisation** — fabriquer une maquette du phénomène, plus simple que le
  vrai, pour pouvoir jouer avec. Une carte n'est pas le pays, mais elle sert à
  s'y déplacer.
- **Expérience de pensée** (en allemand *Gedankenexperiment*) — dérouler une
  idée dans sa tête jusqu'au bout, sans rien toucher, pour voir si elle tient.

### 2. Méthodes empiriques

Observation et expérience concrètes.

- **Observation** — directe ou indirecte, sur le terrain ou en laboratoire.
- **Expérimentation** — trois lieux, trois noms latins : *in vivo* = « dans le
  vivant », on essaie sur un être vivant ; *in vitro* = « dans le verre », on
  essaie dans une éprouvette, hors du corps ; *in silico* = « dans le silicium »,
  on essaie dans un ordinateur, en simulation. Le silicium est la matière des
  puces électroniques.
- **Mesure et test** — collecte de données quantitatives précises.
- **Enquête** — questionnaires, sondages, entretiens.

### 3. Qualitatif contre quantitatif

- **Qualitatif** — comprendre le sens, les motivations, les contextes :
  entretiens, observations, études de cas.
- **Quantitatif** — mesurer, comparer, généraliser : sondages, expériences
  contrôlées, analyses statistiques.

### 4. Méthodes spécifiques à un domaine

- **Méta-analyse** — « méta » veut dire « au-dessus » : au lieu d'étudier le
  sujet, on étudie **toutes les études déjà faites dessus** et on additionne
  leurs résultats. Cent petites études valent mieux qu'une grande.
- **Étude de cas** (autre nom : monographie) — creuser **un seul** cas très à
  fond, au lieu d'en survoler mille.
- **Ethnographie** — aller vivre longtemps dans le milieu qu'on étudie pour
  voir ce que les gens font vraiment, et non ce qu'ils disent faire.
- **Recherche-action** — le chercheur ne reste pas dehors : il agit dans le
  système, puis regarde ce que son action a changé.
- **Recherche participative** — travailler **avec** les gens concernés
  (patients, habitants, associations) et non sur eux.

## Table de choix — quel problème appelle quelle méthode

| Le problème posé | La méthode | Le premier geste |
|---|---|---|
| Une panne matérielle | Étude de cas + notice constructeur | Identifier marque et modèle, lire la notice **avant** d'interpréter une photo |
| Une panne logicielle reproductible | Expérimentation contrôlée | Isoler une variable à la fois, mesurer avant et après |
| Une panne intermittente | Quantitatif, collecte de données | Journaliser d'abord, conclure ensuite — jamais l'inverse |
| « Est-ce que X existe dans le projet ? » | Enquête méthodique | Compétence `recherche` : descendre les lieux dans l'ordre |
| « Quelle option choisir ? » | Analyse et synthèse | Poser les critères **avant** de regarder les options |
| « Combien ça coûte / rapporte ? » | Modélisation quantitative | Nommer les hypothèses chiffrées et leur source |
| « Pourquoi les gens font X ? » | Qualitatif, entretiens | Ne pas remplacer le témoignage par une supposition |
| « Est-ce que ça marche mieux qu'avant ? » | Expérience contrôlée, avant/après | Définir la mesure avant de toucher au système |
| « Que dit la littérature ? » | Méta-analyse, bibliométrie | Sources primaires, pas des résumés de résumés |
| Un comportement d'un système vivant qu'on ne peut pas arrêter | Recherche-action | Intervenir petit, observer l'effet, documenter |

## Outils d'analyse courants

- **Analyse statistique** — faire parler les chiffres : R, Python, SPSS.
- **Analyse de discours ou de contenu** — compter et classer ce qui est dit
  dans des textes ou des entretiens (sciences humaines).
- **Bibliométrie** — « métrie » veut dire « mesure » : on mesure la
  littérature elle-même. Qui cite qui, quels sujets montent, qui fait autorité.
- **Gestion de références** — ranger ses sources pour les retrouver et les
  citer juste : Zotero, Mendeley.
- **Bases spécialisées** — les bibliothèques d'articles scientifiques :
  PubMed (médecine), ScienceDirect, Web of Science.

## Mes techniques à moi

Elles ne sont pas dans les manuels de sciences, mais elles tranchent plus vite
sur un système technique. À utiliser en plus des méthodes ci-dessus.

### La coupe en deux (dichotomie)

Au lieu d'essayer les causes une par une, **couper le champ en deux à chaque
essai**. Mille possibilités se règlent en dix essais au lieu de mille.

Le geste : trouver un point où l'on sait que ça marche, un point où l'on sait
que ça ne marche pas, et tester au milieu. Selon le résultat, la moitié du
champ disparaît. On recommence.

Sur du code, l'outil existe déjà : `git bisect` trouve le commit fautif dans un
historique de mille versions en dix essais.

### Le témoin

Ne **jamais** changer deux choses à la fois. Si on change deux choses et que ça
marche, on ne sait pas laquelle a agi — et on ne le saura plus jamais.

Garder à côté un cas **inchangé** (le témoin) auquel comparer.

### Reproduire avant de corriger

Une panne qu'on n'a pas réussi à faire revenir à volonté ne peut pas être
déclarée réparée. Sans reproduction, on ne saura pas si la correction a marché
ou si la panne s'est simplement absentée.

Ordre : reproduire → comprendre → corriger → vérifier que la reproduction ne
marche plus.

### Le comparatif marche / marche pas

Quand un cas fonctionne et un autre non, ne pas fouiller le cas cassé.
**Lister ce qui diffère entre les deux.** La cause est presque toujours dans
cette liste, et elle est courte.

### « Qu'est-ce qui a changé ? »

Sur une chose qui marchait hier et plus aujourd'hui, c'est la **première**
question, avant toute hypothèse. Une mise à jour, un branchement, un fichier
touché, une manipulation. Un système ne se dégrade pas tout seul du jour au
lendemain.

### La sonde

Quand on ne sait pas si le programme passe vraiment par un endroit, y poser un
**témoin qui ne peut pas mentir** : une trace écrite avec un mot unique. Si le
mot n'apparaît pas, le code n'est pas passé là — et toutes les hypothèses qui
supposaient qu'il y passait tombent d'un coup.

### Les cinq pourquoi

Venu des usines Toyota. Devant une cause trouvée, redemander « pourquoi ? »
cinq fois de suite. On passe de « le ventilateur ne tourne pas » à « personne
n'a vérifié le montage à la livraison ». La première cause n'est presque jamais
la vraie.

### Chercher à se contredire, pas à se confirmer

Le piège le plus courant de l'esprit : une fois qu'on tient une explication, on
ne remarque plus que ce qui l'arrange. C'est le **biais de confirmation**.

L'antidote : une fois l'hypothèse posée, se demander **« qu'est-ce qui la tuerait ? »**
et aller chercher ça en premier. Une hypothèse qui survit à une tentative
sincère de la détruire vaut cent observations qui la caressent.

### Remonter à la source de première main

Une notice constructeur bat une page de forum. Le code source bat la
documentation. Le dépôt distant bat ce qu'on a sur son disque. Le témoignage de
la personne bat une mesure indirecte.

À chaque niveau de recopie, de l'information se perd et de l'erreur s'ajoute.

## Ce qu'il ne faut jamais faire

- **Affirmer une lecture d'indice comme un fait.** Voir la mémoire
  `identifier-avant-interpreter`.
- **Combler un trou d'information par le cas le plus fréquent.** Dire « je ne
  sais pas encore, voilà ce qui trancherait ».
- **Refaire un test déjà fait** par une autre session ou par la personne. Demander
  ce qu'il a donné.
- **Conclure contre un témoignage de première main** sur la foi d'une mesure
  indirecte.
- **Corriger une hypothèse deux fois de suite sans changer de source.** À la
  deuxième correction, arrêter d'interpréter et aller chercher l'écrit :
  notice, documentation, code source, dépôt distant.

## Comment rendre le résultat

Trois blocs, courts (la mémoire `reponses-courtes` s'applique) :

1. **Ce qui est établi** — avec la preuve et sa date.
2. **Ce qui reste ouvert** — les hypothèses encore en lice.
3. **L'observation qui tranche** — une seule, la prochaine action.

Vocabulaire : règle des six ans, chaque symbole décodé.
