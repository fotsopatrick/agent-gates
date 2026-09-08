---
name: portiers
description: Dire QUI est venu sur les sites et CE QU'IL A FAIT — robots de moteurs de recherche, outils automatiques, et fouineurs qui essaient des portes (/.env, /wp-login.php). Un robot par ligne, ses actions en colonnes. Version locale : l'outil tourne sur la tour, on passe par SSH. À invoquer sur « portiers », « qui est venu sur mon site », « les robots », « qui a frappé à la porte », « qui m'a scanné ».
---

# Portiers — qui est passé devant la porte

Un portier ne retient pas les visages : il note qui est venu, à quelle heure, et
ce qu'il a essayé d'ouvrir. Ici on est sur nomi, l'outil vit sur la tour : tout
passe par le canal SSH de confiance (agent chargé, `mon-serveur`).

## Ce que tu fais

1. **Lance l'outil, ne recompte rien à la main.**

   ```bash
   ssh mon-serveur 'python3 ~/tour/deploy/recettes/securite/robots-visiteurs.py'            # depuis 06:00
   ssh mon-serveur 'python3 ~/tour/deploy/recettes/securite/robots-visiteurs.py --heures 2' # 2 dernières heures
   ssh mon-serveur 'python3 ~/tour/deploy/recettes/securite/robots-visiteurs.py --depuis 14'
   ssh mon-serveur 'python3 ~/tour/deploy/recettes/securite/robots-visiteurs.py --tout'
   ssh mon-serveur 'python3 ~/tour/deploy/recettes/securite/robots-visiteurs.py --fouineurs'
   ```

   Il lit les journaux d'accès de Caddy dans le conteneur `tour-caddy-1`.
   **Attention** : ces journaux tournent. Ils ne remontent souvent qu'à minuit,
   parfois moins. Le dire quand la période demandée dépasse ce qui existe —
   ne jamais laisser croire qu'un silence est une absence de visite.

2. **Rends le tableau tel quel.** Une ligne par robot, ses actions en colonnes.
   Ne pas le reformuler en prose : c'est un tableau qu'il veut.

3. **Puis dis les trois choses qui comptent**, dans cet ordre :
   - combien de portes ont été essayées ;
   - combien de réponses ont vraiment livré quelque chose ;
   - si c'est zéro, le dire clairement — c'est la bonne nouvelle du jour.

## Les trois familles, et pourquoi la distinction compte

- **MOTEUR** — se déclare (Google, Bing, Ahrefs, OpenAI…). Il indexe. On le
  laisse. Utile à savoir : s'il ne vient jamais, le site n'est pas référencé.
- **OUTIL** — programme automatique sans identité (curl, python). Depuis notre
  serveur, c'est nous. Depuis ailleurs, c'est à regarder.
- **FOUINEUR** — demande des adresses qui n'existent que chez les sites mal
  fermés : `/.env`, `/wp-login.php`, `/backup.sql`. Il n'explore pas : il essaie
  des poignées de porte.

## Le piège qui fait crier l'alerte pour rien

Plusieurs de nos sites rendent **la même page à toutes les adresses** : les
applications d'une seule page, et les panneaux « bientôt de retour ». Un
fouineur qui demande `/wp-login.php` reçoit donc un code 200 — et rien n'est
sorti.

L'outil le sait : une taille de réponse rendue pour **trois adresses
différentes ou plus** est une page de repli, pas une fuite. Il l'écrit quand
c'est le cas.

Une première version comptait ces 200 comme des fuites. Elle a crié à
l'intrusion pour une page de repli de 490 octets. **Ne jamais annoncer une fuite
sans avoir regardé ce qui est réellement sorti.**

## Ce que tu ne fais pas

- Ne pas transformer un scan de robot en alarme. Des dizaines de fouineurs
  passent chaque jour sur tout site public : c'est le bruit de fond d'internet.
  Ce qui compte n'est pas qu'ils essaient, c'est qu'ils **réussissent**.
- Ne pas bannir une adresse IP de sa propre initiative. Le proposer, et laisser
  la personne décider.
- Ne pas confondre « aucune trace » et « personne n'est venu ».