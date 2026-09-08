---
name: voie-lactee
description: Rejouer ce qui s'est passé à un endroit — lire un journal (Caddy, session Claude, spans, journal daté) et en rejouer la chronologie, filtrée par acteur, en heure de Paris. Elle lit et raconte, elle ne réexécute JAMAIS. À invoquer quand la personne demande « rejoue ce qui s'est passé », « qu'a fait cette adresse », « le film de sa visite », ou qu'on veut la chronologie d'un journal ou d'une session.
---

# Voie Lactée — rejouer ce qui s'est passé à un endroit

Comme la magie de Wendy aux Grands Jeux Magiques : se poster quelque part
et entendre les voix du passé. On donne un LIEU (un fichier de journal) et
éventuellement un ACTEUR (une adresse IP, un nom) — la compétence REJOUE
ce qui s'y est passé, dans l'ordre, en heure de Paris.

## La règle fondatrice

**Elle lit et raconte. Elle ne réexécute JAMAIS.** Un écho n'est pas une
résurrection : aucune commande du passé n'est relancée, aucun état changé.
Rejouer-exécuter serait une AUTRE compétence, et elle n'existe pas.

## L'outil

```sh
python3 ~/.claude/skills/voie-lactee/rejouer.py <journal> [--acteur IP-ou-nom] [--depuis "AAAA-MM-JJ HH:MM"] [--jusqua "..."] [--max N]
```

- `<journal>` : le fichier à rejouer. Formats reconnus tout seuls :
  - cahier du portier Caddy (lignes JSON avec `ts` et `request`) ;
  - historique de session Claude (`*.jsonl` des projets) ;
  - journal de spans (`{"span":...}`) ;
  - journal daté simple (`[AAAA-MM-JJ HH:MM:SS] message`).
- `--acteur` : ne rejouer QUE cet acteur (une adresse IP, un bout de nom).
- Les silences entre deux événements sont annoncés (« … 2 h 14 plus tard »).
- Toute heure est rendue en **Europe/Paris** (règle de la maison).

## Le scénario type (admin réseau / enquêteur)

« Cette adresse a fouillé mon site. Rejoue-moi sa visite. » →
le film complet : première apparition, chaque porte essayée, la réponse du
serveur à chaque fois, le rythme (rafale ou patience), la dernière trace.
C'est la reconstruction de chronologie d'un dossier d'intrusion — en une
commande.

## Preuve de réussite

Le film s'affiche : un en-tête (lieu, période, acteurs), puis une ligne
par événement, horodatée, avec les silences marqués. Code de sortie 0.

## S'emboîte avec

- `kotodama` : extraire les demandes d'un film de session ;
- `intrusions` : le film d'une IP complète le rapport ;
- l'ingesteur d'Alice : avaler un film comme connaissance.
