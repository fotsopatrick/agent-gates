---
name: intrusions
description: Voir qui est venu sur les sites de la personne et qui a essayé d'entrer — robots légaux (Google, Bing, IA, SEO) et illégaux (fouilleurs, scanners), nombre de visiteurs humains, appels illégaux, inondation type déluge (DDoS), force brute sur la porte ssh, techniques d'attaque reconnues. Contient l'inventaire des techniques de hacker qui sert à le gardien pour mener ses tests. À invoquer dès que la personne demande « qui vient sur mon site », « est-ce qu'on m'attaque », « combien de visiteurs », « les robots », « la sécurité de la tour ».
---

# Voir qui vient, et qui essaie d'entrer

Le défaut à éviter : regarder **un seul** journal, ne rien voir, et dire « tout
va bien ». Une attaque laisse des traces à **plusieurs endroits différents**.
Si on n'en ouvre qu'un, on rate le reste.

Deux mots à connaître avant de commencer :

- **Caddy** : le portier du serveur. Toutes les demandes du site passent par
  lui, et il écrit chaque demande dans un cahier (le « journal »).
- **fail2ban** : le videur. Il lit le cahier, et quand une adresse se trompe
  trop de fois, il lui ferme la porte tout seul.

## La commande, en une fois

```sh
~/.claude/skills/intrusions/rapport-intrusions.sh 24
```

- `rapport-intrusions.sh` = le programme qui va chercher tout et le met en forme.
- `24` = le nombre d'**heures** à regarder en arrière. `168` = sept jours.
- Deuxième mot facultatif = un seul site : `... 24 duelle`.

**Preuve que ça a marché** : un pavé qui commence par
`QUI EST VENU — du ... au ...` avec des heures **de chez la personne**, et qui
finit par `On ne bannit personne tout seul.`

Si ça répond `IMPOSSIBLE DE JOINDRE LA TOUR`, c'est le trousseau de clés :
lancer d'abord `~/connexion-tour.sh` (la personne tape sa phrase secrète).

Le programme ne fait que **lire**. Il ne bloque personne, ne change aucun
réglage. Il envoie aussi tout seul la dernière version de l'analyseur sur la
tour, dans `~/espaces/victor/analyseur-intrusions.py`.

## Les sept cases où chaque visite est rangée

| Case | Ce que c'est | Légal ? |
|---|---|---|
| **HUMAIN** | un vrai navigateur, une vraie personne | oui |
| **ROBOT MOTEUR** | Google, Bing, DuckDuckGo... ils rangent le site dans les moteurs de recherche | oui, et utile |
| **ROBOT IA** | GPTBot, ClaudeBot, PerplexityBot... ils aspirent le texte pour entraîner des modèles | oui, mais on peut refuser |
| **ROBOT SEO** | AhrefsBot, SemrushBot... des sociétés de référencement qui revendent l'analyse | oui, mais gourmand |
| **ROBOT RÉSEAU SOCIAL** | LinkedIn, Facebook... ils viennent chercher l'image d'un lien partagé | oui |
| **ROBOT OUTIL** | `curl`, `python`, `wget` — souvent **nos propres** scripts | à vérifier |
| **FOUILLEUR** | il demande des adresses qui **n'existent pas chez nous** (`/wp-login.php`, `/.env`) | **non** |
| **SCANNER** | outil d'attaque connu qui se présente sous son nom (sqlmap, nikto, masscan) | **non** |
| **FAUX ROBOT** | il écrit « je suis Googlebot », mais son adresse dit le contraire | **non** |

Le nom qu'un robot déclare est du **texte libre** : n'importe qui peut mentir.
L'analyseur ne le croit pas sur parole — pour les robots de moteurs de
recherche, il demande au bottin d'internet à qui appartient l'adresse, et
refait le chemin en sens inverse. Les menteurs sortent en partie 2bis du
rapport. Pour sauter cette vérification (plus rapide) : `--sans-verif`.

Règle de lecture : un FOUILLEUR ne « visite » pas. Il essaie des portes une par
une, en espérant en trouver une mal fermée.

## Les trois endroits qu'on ouvre, toujours les trois

1. **Le cahier du portier** —
   `/var/lib/docker/volumes/tour_caddy-data/_data/logs/access.log`
   (plus les anciens, compressés en `.log.gz`). Une ligne = une demande, avec
   le site, l'adresse demandée, l'adresse du visiteur, et son « nom » déclaré.
2. **Le carnet du videur** — `sudo fail2ban-client status <porte>`. Trois
   portes existent : `sshd`, `odoo-login`, `odoo-login-demo`.
3. **Le cahier de la porte de derrière** —
   `sudo journalctl -u ssh --since "24 hours ago"`. C'est là que se voit la
   **force brute** : essayer des milliers de mots de passe à la chaîne.

Piège déjà payé : sur la tour, on entre **uniquement avec une clé**, jamais
avec un mot de passe. Donc `Failed password` reste souvent à **zéro** même
quand on se fait marteler. Le vrai signe est `Invalid user` — « ce nom
d'utilisateur n'existe pas ». Compter les deux, sinon on conclut « personne
n'attaque » alors que si.

Autre piège : Caddy écrit aussi ses **propres** notes dans le cahier
(renouvellement de certificat). Ce ne sont pas des visites. L'analyseur ne
garde que les lignes `logger = http.log.access`.

## Ce qu'on ne fait JAMAIS tout seul

- **Bannir une adresse**, changer le pare-feu, toucher à fail2ban : c'est
  toucher à la production. On prépare la commande, on l'explique, **la personne
  décide**.
- **Dire « on est attaqué » sans le chiffre.** On donne l'adresse, le nombre
  d'appels, l'heure de début et de fin, en heure de Paris.
- **Confondre bruit de fond et attaque ciblée.** Tout serveur sur internet
  reçoit des fouilleurs en permanence, c'est la pluie. Ce qui compte :
  est-ce que quelqu'un vise **nous** (nos noms, nos chemins à nous), et
  est-ce qu'il a **réussi** quelque chose (un code 200 sur une adresse
  qu'il n'aurait jamais dû obtenir).

## Le signal qui doit réveiller tout le monde

Dans la partie « QUI EST VRAIMENT ENTRÉ PAR SSH », il ne doit y avoir que
`ubuntu` depuis l'adresse de la maison de la personne. **Une autre adresse ici
veut dire que quelqu'un est dedans.** On arrête tout et on le dit
immédiatement, avant de continuer quoi que ce soit d'autre.


## Le piège muet (niveau 1) — POSÉ ET QUI TOURNE

Un piège, c'est une adresse appât : `/.env`, `/wp-login.php`, `/.git/config`.
Elles n'existent pas chez nous. Un visiteur honnête ne les tape **jamais**.
Donc **tout ce qui les touche est suspect à 100 %**, zéro fausse alerte.

Le portier ne change pas d'un poil : il répond 404 comme avant. On se contente
de **recopier** ces tentatives dans un cahier à part.

```sh
ssh mon-serveur 'sudo python3 ~/espaces/victor/pieges-extraire.py'      # ramasser
ssh mon-serveur 'sudo python3 ~/espaces/victor/pieges-resume.py --heures 24'   # lire
```

Le cahier est `~/pieges/pieges.jsonl` sur la tour. Le résumé dit
qui est **nouveau** (jamais vu avant) — c'est ça qui compte — et si quelqu'un a
obtenu autre chose qu'un refus.

**La règle qui a déjà servi** : un `200` (« voilà, tiens ») sur un appât ne
prouve pas une fuite. On regarde la **taille** de ce qui est sorti. Si toutes
les réponses font la même taille, c'est la page d'accueil renvoyée à tout le
monde : rien n'a fuité. Des tailles très différentes = du vrai contenu, et là
on se lève.

Pour que ça tourne tout seul chaque matin : `piege/POSER-LE-MINUTEUR.md`.

## Le canari (niveau 2) — PRÊT, PAS ENCORE POSÉ

Un faux fichier de secrets, servi exprès, sur un sous-domaine **sacrifié**
(`piege.mon-site.example`). Dedans : de faux mots de passe, un faux compte
Odoo (`sauvegarde_auto`, vérifié inexistant sur les 4 bases le 22/08/2026), et
surtout une **adresse unique que personne ne peut deviner**. Le jour où cette
adresse est demandée, c'est la **preuve** que quelqu'un a lu le faux fichier.

Tout est dans `piege2/` : les faux fichiers, le bloc à coller chez le portier,
et `POSER.md` qui donne les gestes dans l'ordre avec la preuve à chaque étape.
Le jeton secret est dans `piege2/jeton-canari.txt` — il ne se teste **jamais**
« pour voir », sinon on déclenche notre propre alarme.

Pour demander au canari s'il a chanté :

```sh
~/.claude/skills/intrusions/piege2/canari-alerte.sh
```

## Pourquoi il n'y a AUCUN programme dans ces deux pièges

La question « il faut isoler, Docker ? » a une meilleure réponse : **ne rien
mettre à isoler**. Un piège qui n'est qu'un fichier posé et un portier qui le
tend ne contient aucun programme — donc rien à pirater, rien à faire sortir de
sa boîte, rien à mettre à jour.

Un conteneur Docker, lui, fait tourner du code, partage le **même noyau** que
la machine (le noyau est le cœur du système), et sur la tour deux comptes sont
dans le groupe `docker` : `ubuntu` et `codenominomi`. Or être dans ce groupe
revient à être chef de toute la machine, sans mot de passe. Un conteneur en
plus, c'est donc une surface en plus, pas un mur en plus.

Si un jour un piège a **vraiment** besoin de faire tourner du code, l'ordre de
préférence est : (1) pas de code du tout ; (2) un tout petit service tenu par
`systemd` avec les verrous `DynamicUser`, `ProtectSystem=strict`,
`NoNewPrivileges`, qui n'écoute que sur la machine elle-même ; (3) Docker en
dernier, jamais en `--privileged`, jamais avec `docker.sock` monté dedans.

## Pour le gardien : l'inventaire des techniques

le gardien, c'est Cyborg : la sécurité, contrôles déterministes, pas d'IA qui
devine. Pour qu'il teste bien, il lui faut la liste de **ce que les attaquants
essaient vraiment**, et la trace que chaque tentative laisse.

Cette liste est dans le fichier voisin :
`~/.claude/skills/intrusions/TECHNIQUES-HACKER.md`

Elle sert à deux choses : **reconnaître** une technique dans le journal, et
**vérifier** que la tour y résiste. Elle ne sert qu'à nos machines à nous.
