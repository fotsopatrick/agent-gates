---
name: navigateur
description: >
  Piloter le vrai navigateur de la personne — ouvrir une page, la photographier,
  lire son texte, cliquer, taper. À invoquer dès qu'il faut VOIR une page web,
  vérifier un affichage, remplir un site, ou quand la personne dit « ouvre »,
  « montre-moi la page », « pilote le navigateur », « clique ». Contient aussi
  ce qui reste TOUJOURS la main de la personne : mots de passe, achats, envois.
---

# Piloter le navigateur

## D'abord : le navigateur partagé doit tourner

Le pilotage passe par une **porte de commande** ouverte sur le port **9333**
(un numéro de porte sur la machine). Le contrôle :

```sh
curl -s -m 3 http://127.0.0.1:9333/json/version
```

Si ça écrit `"Browser": "Chrome/…"`, la porte est ouverte. Si ça n'écrit rien,
la porte est fermée : lancer `~/outils/chrome-agents/chrome-agents.sh`.

**Ne jamais utiliser le port 9222** : il est pris par le jeu.

## L'outil : `nav.js`

`~/outils/nav.js` parle à Chrome sans rien installer. Il se lance avec `node`.

| Ce que je veux | La commande |
|---|---|
| voir les onglets ouverts | `node ~/outils/nav.js liste` |
| ouvrir une page | `node ~/outils/nav.js ouvre "https://…"` |
| photographier un onglet | `node ~/outils/nav.js photo <bout-d-adresse> <nom.png>` |
| lire le texte d'un onglet | `node ~/outils/nav.js texte <bout-d-adresse>` |
| cliquer à un endroit | `node ~/outils/nav.js clic <bout-d-adresse> <x> <y>` |
| écrire du texte | `node ~/outils/nav.js tape <bout-d-adresse> <texte>` |
| fermer un onglet | `node ~/outils/nav.js ferme <bout-d-adresse>` |

`<bout-d-adresse>` = quelques lettres qui se trouvent dans l'adresse ou le
titre de l'onglet. Exemple : `pippit`. **Attention** : un bout trop court
attrape le mauvais onglet. `short-drama` attrape aussi `short-dramas`.

Les photos vont dans `~/livrables/captures/` — Mes travaux, flèche 1.

## L'ordre à respecter

1. **Ouvrir**, puis **attendre** que la page charge (`sleep 6`), puis
   **photographier**. Sans l'attente, la photo est blanche.
2. **Toujours regarder la photo avant de cliquer.** Les coordonnées d'un clic
   se lisent SUR la photo : x compté depuis la gauche, y depuis le haut.
3. **Montrer la photo à la personne** avec l'outil d'envoi de fichier. Une adresse
   toute seule ne dit ni si c'est beau, ni si c'est cassé — voir
   [[montrer-pas-nommer]].
4. **Refermer** les onglets que j'ai ouverts quand j'ai fini.

## Les bandeaux de cookies

Un site qui demande les cookies : je choisis **« Tout refuser »**, jamais
« Tout accepter ». Refuser ne signe rien. Accepter, si.

## Ce que je ne fais JAMAIS seul

- **Taper un mot de passe.** Jamais, même si la personne me le donne.
- **Créer un compte.**
- **Cliquer « Acheter », « Payer », « Envoyer », « Publier », « Supprimer ».**
  Je prépare, je montre la photo, et la personne clique.
- **Accepter des conditions.**

Quand un site demande une connexion : j'ouvre la page, je le dis à la personne,
il se connecte lui-même dans la fenêtre, puis je reprends la suite.

## Pourquoi cette compétence existe

Le 6 septembre 2026, le module officiel qui reliait Chrome à moi ne répondait
pas, et `~/outils/navigateur.py` réclamait un morceau absent de la machine
(playwright). J'ai perdu du temps à croire que je ne pouvais pas voir les
pages. `nav.js` n'a besoin de rien d'autre que `node`, déjà installé.

Compétence sœur : [[recherche]] pour trouver, [[jimmy]] pour la preuve.
