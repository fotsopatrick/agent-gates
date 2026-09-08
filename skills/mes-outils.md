---
name: mes-outils
description: Présenter mes outils par FAMILLES, pas les 260 d'un coup. À invoquer quand la personne demande « tu as quoi comme outils ? », « qu'est-ce que tu peux lancer ? », ou après l'éveil. Je montre les grandes familles, puis je demande LAQUELLE il veut, et je ne détaille que celle-là. Sous-compétence de [[eveil]].
---

# Mes outils — par familles, puis on creuse UNE famille

Le défaut à éviter : déverser une liste de 260 outils. Personne ne lit ça.
On montre les **familles** (les grandes boîtes), on demande **laquelle**, et on
ne sort le détail que de la famille choisie. Court, puis précis.

## 1. Montrer les familles
Les familles viennent des **zones de la carte vivante** (le relevé de la tour).
Je les liste avec, pour chacune, un mot d'explication et le **nombre d'outils** :
- **Les webapps** — les petites applications du service.
- **Les façades** — ce qui est montré au public (dont la vitrine).
- **L'équipe** — les agents, chacun avec son rôle.
- **Le pilotage** — ce qui décide et surveille.
- **Les serveurs / conteneurs / volumes** — la machine, ses boîtes, ses disques.
- **Les outils** — les scripts prêts à lancer (~260).
- **Les circuits** — les épreuves à passer avant de publier.

Si la carte n'est pas encore lue, je fais d'abord [[eveil]] — je n'invente pas les nombres.

## 2. Demander la famille
Je pose **une** question simple : « Quelle famille tu veux ouvrir ? »
Je ne continue pas tant que je n'ai pas la réponse — sauf si la tâche en cours
désigne déjà clairement la famille (alors je le dis et j'ouvre celle-là).

## 3. Détailler UNE seule famille
Pour la famille choisie, je liste ses outils avec, pour chacun :
- son **nom**,
- ce qu'il **fait** en une phrase,
- la **preuve** que ça a marché quand on le lance.
Commande pour lire une famille sur la tour :
```sh
SSH_AUTH_SOCK=~/.ssh/agent.sock ssh mon-serveur 'python3 ~/outils/carte-tour.py <nom de la famille>'
```

## Clôture
Je finis par **une** prochaine action : lancer un outil de la famille, ou ouvrir une autre famille.
