---
name: concordance
description: Vérifier qu'une vidéo dit la même chose à l'oreille et à l'œil — la voix, les écrits à l'écran, et le moment où chaque phrase tombe. À invoquer avant de livrer une vidéo, quand la personne dit « il y a un déphasage », « le son ne colle pas », « vérifie la concordance », ou avant d'envoyer une démonstration à un concours.
---

# Concordance — l'image et la voix disent-elles la même chose ?

## Pourquoi cette compétence existe

Née d'une faute réelle, le 08/09/2026. la personne, sur la vidéo d'Alice :
« il y a un déphasage entre l'audio et le texte en français, alors qu'Alice
répond en anglais ».

Une vidéo fausse est **pire** qu'une vidéo absente. Elle a l'air d'une
démonstration, et elle montre autre chose que ce qu'elle raconte. Un juge de
concours ne pardonne pas ça : il en déduit que le reste est faux aussi.

Le même jour, une mesure sur les neuf vidéos existantes a trouvé, en trente
secondes, ce que personne n'avait vu en trois jours :

```
circuit-de-la-tour.mp4      7,2 s d'image   AUCUNE VOIX
my-control-tower.mp4        1,1 s de silence a la fin
salle-des-agents-narree.mp4 0,6 s d'ecart
```

## Les quatre fautes, et pourquoi aucune ne se voit à l'œil

**1. La vidéo muette.** Une image, pas de voix. On ne s'en aperçoit qu'en la
montrant à quelqu'un — donc trop tard.

**2. Le silence de fin.** La voix s'arrête, l'image continue. Le spectateur
croit que ça a planté.

**3. Le déphasage.** La voix dit une chose pendant que l'écran en montre une
autre. **Ça ne se voit dans aucune durée** : les deux peuvent faire exactement
la même longueur et ne rien avoir en commun. C'est la faute la plus fréquente
et la plus invisible.

**4. Le mélange de langues.** La voix parle anglais, l'écran affiche du
français. Depuis le 06/09/2026, tout est en anglais : la voix **et** les
écrits. La voix officielle est `en-US-Chirp3-HD-Kore`, vitesse 0,94, validée
par la personne — ne pas en changer sans qu'il le demande.

## La méthode, dans l'ordre

### 1. Écrire le script AVANT de filmer

C'est la seule façon d'éviter le déphasage. On ne colle pas une voix sur une
capture : on décide d'abord ce qui se dit et ce qui se montre, en même temps.

Un fichier `<video>.script.json`, à côté de la vidéo :

```json
{"langue": "en",
 "segments": [
   {"a": 0,  "dure": 8,
    "dit": "This is the control tower. Every agent has a name and a trade.",
    "montre": "la salle de commandement, les pastilles vertes a gauche"},
   {"a": 8,  "dure": 12,
    "dit": "Every gate can refuse, and each one has to say no at least once.",
    "montre": "la liste des gardes, avec la colonne banc d'essai"}
 ]}
```

`a` = à quelle seconde ce morceau commence. `dure` = combien de temps il dure.
`dit` = ce que la voix raconte. `montre` = ce que l'écran affiche **au même
moment**. Le champ `montre` est obligatoire : sans lui, personne ne peut
vérifier que les deux concordent.

### 2. Filmer en suivant le script

Chaque morceau correspond à un moment de l'écran. On filme dans l'ordre du
script, pas l'inverse.

### 3. Mesurer, avant de livrer

```
python3 ~/outils/concordance-video.py <video.mp4> [script.json]
```

Sans le script, il ne peut vérifier que les durées — il le dit lui-même.
Avec le script, il vérifie les quatre fautes.

### 4. Ne livrer qu'au vert

Un rouge, une raison, un chiffre. Pas de « ça a l'air bon ».

## Le contrôle de l'outil lui-même

```
bash ~/controles/test-concordance-video.sh
```

Il fabrique de fausses vidéos, chacune avec une faute connue, et vérifie que
l'outil la trouve — puis qu'il laisse passer une vidéo juste. **6 verts sur
6** au 08/09/2026.

Un piège déjà payé dans ce banc : la fausse vidéo « silence de fin » était mal
fabriquée, `ffmpeg` coupait à la plus courte, et la faute à tester n'existait
pas. Le banc croyait donc l'outil aveugle. **Un test qui échoue accuse
d'abord le test.**

## Ce qu'on ne fait jamais

- Coller une voix sur une capture déjà filmée en espérant que ça tombe juste.
- Livrer une vidéo dont on n'a pas mesuré la concordance.
- Laisser un écran en français sous une voix anglaise.
- Dire « c'est synchronisé » sans le chiffre de l'écart.

Voir [[video-narree]] pour fabriquer la vidéo, et [[jimmy]] pour la règle du
test écrit d'abord.
