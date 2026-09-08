---
name: proteger-une-page
description: Fermer une page publique derrière une adresse e-mail et un code reçu par courrier, sans compte ni mot de passe. À invoquer dès qu'on parle de « protéger une page », « page privée », « accès sur invitation », « qui lit mes études », « demander l'email avant de montrer », ou quand une page doit rester lisible seulement par des gens vérifiés.
---

# Protéger une page — l'adresse, puis le code

**Éprouvé sur la tour le 07/09/2026** : 7 contrôles au vert, joués comme un
vrai visiteur — porte fermée, question posée, code envoyé, code retrouvé dans
la boîte, code tapé, étude ouverte (27 338 signes).

## La règle qui commande tout

**Le serveur ne doit JAMAIS envoyer la page à qui n'a pas prouvé son adresse.**

Pas « il l'envoie et la cache avec du style ». Pas « il met une balise
noindex ». Quand le robot lit la balise, il a **déjà reçu tout le texte** : il
promet de ne pas l'afficher, il ne promet pas de ne pas l'avoir.

Une page cachée par le style ou par du code de page n'est pas protégée : elle
est **déjà partie**.

## Les quatre marches, dans cet ordre

### 1. La porte remplace la page

Le serveur regarde le ticket du visiteur. Sans ticket valable, il renvoie la
**porte** — même adresse, même code de réponse, et **pas une ligne** du
contenu.

Le contrôle qui le prouve : demander la page sans rien, et compter les
octets. Sur la tour, la mesure a valu son pesant :

    biscuit invente  -> 3 873 octets, la porte
    aucun biscuit    -> 3 870 octets, la porte
    (avant reparation : 34 277 octets — l etude entiere)

### 2. Une question écarte les robots

Un petit calcul, écrit **en toutes lettres** (« Combien font trois plus
cinq ? »). Il ne protège de rien tout seul : il empêche juste un programme
bête de demander mille codes.

L'identifiant de la question est tiré au hasard et vit cinq minutes.

### 3. Le code arrive par courrier

Le serveur tire **six chiffres au hasard** — avec un vrai tirage, jamais à
partir de l'heure : un code devinable n'est pas un code. Il l'envoie à
l'adresse donnée.

Le code **s'use** : une seule fois, et il périme au bout de quinze minutes.
Un plafond par adresse et par heure empêche d'en faire une machine à envoyer
des courriers à n'importe qui.

### 4. Le ticket signé

Une fois le code bon, le serveur pose un ticket **signé** avec une clé qui ne
sort jamais du serveur, et qui porte sa date de péremption. Un ticket fabriqué
à la main ne passe pas : la signature ne correspond pas.

L'adresse n'est gardée **qu'une fois prouvée**, jamais avant.

## Ce qu'on ne fait jamais

- Cacher la page avec du style ou du code de page : elle est déjà envoyée.
- Fabriquer le code à partir de l'heure ou d'un compteur.
- Garder l'adresse avant que le code soit tapé.
- Faire confiance à un simple biscuit sans signature : n'importe qui l'écrit.
- Dire « ça marche » sans avoir joué le parcours **en entier**, code reçu
  compris.

## Le contrôle qui prouve, et rien d'autre

Un contrôle qui ne va pas chercher le code **dans la boîte** ne prouve rien.
Sur la tour : `deploy/test-porte-bout-en-bout.py` — il regarde que la page est
fermée, répond à la question, demande le code, **ouvre la boîte**, le tape, et
vérifie que la page s'ouvre enfin.

Deux pièges payés en l'écrivant :
- il cherchait un calcul **en chiffres**, la porte l'écrit **en lettres** ;
- « le courrier est parti » ne veut pas dire « arrivé » : il faut aller le
  chercher. Voir la compétence [[courrier]].

Compétences sœurs : [[courrier]] pour l'envoi du code, [[eveil]] pour l'état
réel avant d'agir.
