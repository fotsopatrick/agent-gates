---
name: publier-etude
description: Publier ou vérifier une étude sur la tour, par le circuit « Publier une étude » et son épreuve, depuis le bac à sable (packet tracer). À invoquer quand la personne dit « publie cette étude », « mets une étude en ligne », « vérifie qu'une étude est bien gardée », ou parle d'une page réservée aux humains (études, alice, agentracer). Garantit : gardée par la porte à code, jamais de vieux verrou à fenêtre, privée (à ne pas indexer), lisible avec un droit valide.
---

# Publier une étude — la bonne porte, prouvée avant de sortir

Une **étude** est une page réservée aux humains : personne ne la lit sans
passer la **porte à code** (on donne son adresse, on reçoit un code par
courrier, on le tape). Elle ne doit jamais être derrière un **vieux verrou à
fenêtre** (le mot de passe « guilde »), qui empêche même d'atteindre la porte.

## La règle en une phrase

**Aucune étude ne sort sans passer l'épreuve, jouée depuis le bac à sable.**
Rouge = on corrige, on ne force pas.

## Le circuit

Dans la tour, le circuit **« Publier une étude »** (base `tour_dev`, le bac à
sable) a quatre portes :
1. **Sécurité — le gardien** : l'étude passe l'épreuve (voir plus bas) ;
2. **Relecture — la relectrice** : rien de confidentiel ne fuit ;
3. **la personne** valide ;
4. **Publication** : mise en ligne + prévenir les inscrits (circuit 125).

## L'épreuve : « une étude est-elle publiable ? »

Cinq contrôles, joués comme un vrai visiteur, sur la vraie page :
- **P1** l'étude existe (le fichier est là) ;
- **P2** sans rien, on voit la porte (adresse + code), pas l'étude ;
- **P3** aucun vieux verrou à fenêtre (« guilde ») devant — sinon on ne voit
  même pas la porte ;
- **P4** l'étude est privée (marquée « à ne pas indexer », fermée aux robots) ;
- **P5** avec un droit d'entrer valide, l'étude entière se lit.

## Les gestes (sur la tour, base d'essai `tour_dev`)

Se connecter d'abord : `SSH_AUTH_SOCK=~/.ssh/agent.sock ssh mon-serveur`.
Les outils vivent dans `~/dev/circuit-etudes/` :

- **Vérifier une étude** (juste l'épreuve) :
  `python3 ~/dev/circuit-etudes/test-publier-etude.py <hôte> <chemin>`
  ex : `... https://mon-site.example /etude-truck-factor.html`
  Preuve : « PUBLIABLE : TOUT EST VERT ».

- **La publier depuis le bac à sable** (l'épreuve + le passage par le circuit) :
  `bash ~/dev/circuit-etudes/publier-depuis-bac.sh <hôte> <chemin>`
  Preuve : « PUBLIÉ EN PRIVÉ : l'étude passe toutes les portes. »
  Si rouge : « REFUSÉ par le circuit. Rien publié. On corrige, on ne force pas. »

## Retirer un vieux verrou à fenêtre (si P3 est rouge)

`bash ~/dev/circuit-etudes/retirer-verrou-alice.sh` — modèle à copier pour un
autre site : il retire **seulement** le verrou visé, valide le portier, le
recharge, et remet l'ancien fichier si la validation rate.

## Ce qu'on ne fait jamais

- **Publier une étude derrière un vieux verrou à fenêtre.** Un humain ne
  pourrait pas la lire.
- **Forcer une porte rouge.** On corrige la cause, on rejoue le bac à sable.
- **Toucher la production directement.** Le harnais le refuse — on prépare, et
  la personne clique le bouton (voir [[jamais-de-commande-a-la personne]]).

## Liens

[[circuit-juste]] trouve le circuit avant le travail. [[eveil]] ouvre la tour.
Le circuit 125 (« Étude — toute mise à jour est notifiée ») s'occupe de
prévenir les inscrits une fois l'étude publiée.
