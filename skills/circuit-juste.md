---
name: circuit-juste
description: Avant de faire un travail sur la tour, trouver QUEL circuit le gouverne. Sert quand on va publier un article, toucher la vitrine, déployer, changer une page, ajouter un test — c'est-à-dire à chaque fois qu'un travail va sortir. Répond « c'est le circuit numéro N » ou « aucun circuit ne couvre ça ».
---

# Circuit juste — trouver la bonne porte AVANT de travailler

## Pourquoi cette compétence existe

Le 4 septembre, la personne a dit : **« tu n'as pas suivi les circuits adaptés ».**
J'avais publié quatre articles. Ils sont sortis sans vignette d'en-tête et sans
être rangés par date. Le circuit numéro **75, « Nouvel article public »**,
existait, avec quatre portes qui vérifient exactement ça. Je ne l'ai pas ouvert.

Le travail n'était pas mauvais. Il était **hors circuit**. C'est ça qu'on répare
ici : on ne cherche pas le circuit **après** avoir travaillé, on le cherche
**avant**.

## La règle en une phrase

**Avant tout travail qui va sortir, on nomme son circuit.** Si on ne le trouve
pas, on le dit à la personne — on ne travaille pas « sans ».

« Qui va sortir » veut dire : que quelqu'un d'autre que moi verra. Une page,
un article, un déploiement, un changement d'apparence, un envoi.
Lire, mesurer, chercher : ça ne sort pas, ça n'a pas besoin de circuit.

## Comment on cherche (dans cet ordre)

### 1. On lit la liste, on ne la devine pas

```
python3 ~/outils/circuits.py "<un mot du travail>"
```

Cet outil pose la question à la tour et rend les circuits dont le nom ou le
sujet contient le mot. `~` veut dire « mon dossier personnel ». Si l'outil
n'est pas là, on demande la liste directement à la tour :

```
SSH_AUTH_SOCK=~/.ssh/agent.sock ssh -o IdentityAgent=~/.ssh/agent.sock mon-serveur \
  "docker exec -i tour-odoo-1 /entrypoint.sh odoo shell -d tour --no-http" <<'PY'
for m in env['circuit.modele'].search([('active','=',True)]).sorted('id'):
    print(m.id, m.type_operation, m.name,
          " > ".join(e.name for e in m.etape_ids.sorted('sequence')))
PY
```

Décodage : `ssh` = se connecter à la tour ; `docker exec` = parler au programme
Odoo qui tourne dans sa boîte ; `circuit.modele` = le gabarit d'un circuit ;
`active` = le circuit est allumé (**et pas `actif`** — ce nom-là n'existe pas,
l'erreur a déjà été faite).

Preuve que ça a marché : une liste de lignes qui commencent par un numéro.

### 2. On cherche par ce que le travail FAIT, pas par son titre

Un titre ment. « Ajouter un bouton de dons » n'a pas le mot « bouton » dans un
circuit. Ce que ça FAIT, c'est : **modifier une page publique**. Donc on cherche
« page », « vitrine », « publication ».

Les mots qui marchent : `article`, `vitrine`, `publication`, `page`, `test`,
`déploiement`, `coffre`, `secret`, `thème`, `langue`, `jeu`, `réseaux`.

### 3. On prend le circuit le plus PRÉCIS, pas le plus grand

S'il y en a plusieurs, on garde celui dont les portes parlent du travail. Un
circuit large (« Maintenance de la vitrine ») ne remplace pas un circuit précis
(« Nouvel article public »), parce que le précis contient les contrôles que le
large n'a pas.

### 4. On lit les portes AVANT de commencer

Chaque porte est une **épreuve** : quelque chose qu'il faudra montrer. Les lire
avant, c'est savoir quoi préparer. Le circuit 75 demande une vignette : si on
lit ça avant, on fait la vignette ; si on lit ça après, on republie tout.

### 5. Si aucun circuit ne colle

On le dit avec ces mots : **« Aucun circuit ne couvre ça. J'ai cherché avec les
mots X, Y, Z. Soit on en crée un, soit tu me dis lequel prendre. »**
On ne prend pas « le plus proche » en fermant les yeux.

## Les circuits qu'on rencontre le plus (relevé le 5 septembre 2026)

| Le travail | Le circuit |
|---|---|
| Publier un nouvel article sur le site | **75** — Nouvel article public |
| Toucher une page du site déjà en ligne | **22** — Maintenance de la vitrine |
| Envoyer le site d'essai vers le vrai site | **107** — Commit, publier la vitrine |
| Publier par le script à chemin unique | **112** — Vitrine, publication |
| Vérifier qu'une page ne montre rien d'interne | **127** — Page publique |
| Déployer un module de la tour | **20** — Déploiement, modules et vitrine |
| Traduire une page | **165** — Internationalisation |
| Changer l'apparence | **166** — Thème |
| Toucher à ce qui se vend ou se paie | **36** — Offres commerciales en place |
| Toucher un secret | **16** — Modification du Coffre |
| Publier sur LinkedIn | **126** |

Ce tableau est un **raccourci**, pas la vérité. La vérité est dans la tour.
Si un numéro ne répond plus, on relit la liste (étape 1).

## Ce qu'on ne fait jamais

- **Travailler d'abord, chercher le circuit ensuite.** C'est la faute d'origine.
- **Fabriquer un garde-fou pour cacher une porte qui refuse.** Une porte qui
  refuse fait son travail. la personne l'a dit : « tu crées un garde-fou pour
  masquer une erreur ? »
- **Forcer une porte tout seul.** Une porte se force avec la personne, jamais sans.

## Lien avec les autres compétences

[[competence-recherche]] trouve **ce qui existe**. [[analyse]] comprend **un
problème**. Celle-ci répond à une seule question : **par quelle porte ce travail
doit-il passer ?** Elle se lance avant les deux autres quand le travail va sortir.

## La prochaine action

Nomme le circuit à voix haute avant la première ligne de code. Si tu ne peux
pas le nommer, tu n'as pas encore commencé à travailler.
