---
name: jimmy
description: Rapporter la PREUVE avant de dire que c'est fait. À charger dès qu'on corrige, qu'on ajoute ou qu'on livre quelque chose. Impose l'ordre : écrire le test D'ABORD, le voir échouer, corriger, retester, jusqu'au vert — puis passer les portes (circuits, garde-fous) avant de toucher la production. Contient les pièges déjà payés, dont le pire : un test qui passe au vert en regardant autre chose.
---

# le temoin — la preuve, pas la promesse

le temoin Olsen rapporte la photo. Sans photo, il n'y a pas d'article. Ici c'est
pareil : **sans preuve, il n'y a pas de « c'est fait »**.

## L'ordre, jamais un autre

1. **Écrire le test D'ABORD.** Avant la correction, avant le code.
2. **Le lancer et le VOIR ÉCHOUER.** Un test qui n'a jamais été rouge ne prouve
   rien : il peut regarder à côté sans qu'on le sache.
3. **Corriger.**
4. **Relancer.** S'il est rouge : retour au 3. On boucle jusqu'au vert.
5. **Passer les portes** (voir plus bas) avant de toucher ce que les gens voient.
6. **Dire ce qui est vert, avec le chiffre** : « 25/25 verts », jamais « ça marche ».

## Le pire piège, déjà payé (04/09/2026)

Un test cherchait un personnage **par sa forme** : « un groupe avec au moins
deux étiquettes et trois morceaux ». Il passait au vert. Il attrapait en fait
**le groupe du monde entier**. La preuve : en cachant ce qu'il avait trouvé,
toute la salle disparaissait — le nombre de dessins tombait de 196 à 11.

**Un test qui passe au vert en regardant autre chose est PIRE que pas de test :
il donne une fausse confiance, et il la donne longtemps.**

La règle qui en sort : **on identifie par un nom exact, jamais par une
ressemblance.** On pose un nom sur la chose (`objet.name = 'l explorateur'`) et le
test la retrouve par ce nom. Si le nom n'existe pas encore, on le crée.

Frère de cette règle : [[identifier-avant-interpreter]] et la carte vivante —
on LIT, on ne devine pas.

## Ce qu'un vrai test doit faire

- **Lire l'état RÉEL**, pas un état que le test a lui-même fabriqué.
- **Nommer précisément** ce qu'il cherche (voir le piège ci-dessus).
- **Dire pourquoi il est rouge**, avec les vrais chiffres : « 0/1 — thèmes vus :
  [null] — niveau : 1 ». Un test rouge muet fait perdre une heure.
- **Se relancer seul**, en une commande, sans préparation à la main.
- **Nettoyer derrière lui** : sur nomi, un navigateur de test se ferme AUSSITÔT
  (voir la règle nº1 du projet du jeu ; un headless oublié a mis le processeur
  à 1135 %).

## Ce qu'un faux test fait (à refuser)

- Il affirme sans mesurer (« le pont existe donc ça marche »).
- Il teste ce que le code vient d'écrire, dans la même seconde, sans recharger.
- Il attrape par ressemblance au lieu du nom.
- Il ne montre jamais de rouge, quoi qu'on casse.

## Les portes, avant la production

Rien ne va directement là où les gens regardent.

1. **Copie d'essai d'abord.** On déploie sur une adresse séparée
   (`index-l explorateur.html`, `essai/`), on teste là, et seulement après on
   remplace la vraie.
2. **Le circuit de relecture** pour tout ce qui se publie (vitrine, article,
   page) : `publier-vitrine.sh <slug>` ouvre la porte, la relecture répond,
   **la personne valide en dernier**. Je ne signe JAMAIS une porte à sa place
   ([[limites-du-harnais-claude]]).
3. **Les garde-fous n'ont pas d'oreilles.** Ni berzerk ni le mode automatique ne
   les éteignent : ils les traversent. Quand l'un bloque, une ligne — nommer le
   gardien, tendre la commande prête — et on passe à autre chose.
4. **Une sauvegarde avant d'écraser**, et la commande de retour en arrière
   donnée en même temps que le changement.

## Ce qu'on rend à la personne

- Le chiffre : « N/N verts ».
- Ce que le test a TROUVÉ, pas seulement qu'il est vert : les défauts trouvés
  sont la vraie valeur du test.
- Ce qui reste **non vérifié**, dit franchement. Un test d'état ne prouve pas
  une image : si personne n'a regardé l'écran, on le dit.
- La commande pour tout rejouer, chaque morceau décodé.

## Rejouer les bancs connus

```sh
cd ~/donjon-vr && node tests/test_braignak_cdp.mjs     # 25/25 verts attendus
cd ~/donjon-vr && python3 tests/test_webmcp.py         # 35 tests
cd ~/donjon-vr && python3 tests/test_webmcp_integration.py   # 15 tests
cd ~/tour-twenty-strands && .venv/bin/pytest -q        # 27 tests
```
