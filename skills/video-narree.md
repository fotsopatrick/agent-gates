---
name: video-narree
description: Fabriquer une vidéo d'écran commentée par une voix — capture de l'écran, narration fabriquée chez Google, assemblage. À invoquer quand la personne demande « fais une vidéo », « filme ce que tu fais », « avec une voix qui explique », ou une démonstration pour un hackathon.
---

# Fabriquer une vidéo d'écran avec une voix qui explique

## LE MUR À CONNAÎTRE AVANT DE COMMENCER

Le poste nomi tourne en **Wayland**. Wayland interdit à un programme de
filmer l'écran sans qu'un humain clique pour l'autoriser. Constaté le
04/09/2026 : `ffmpeg -f x11grab -i :1` rend une **image noire**, luminosité 0.

Trois chemins ont été essayés, et voilà ce qu'ils donnent :

| Chemin | Résultat |
|---|---|
| `ffmpeg` sur l'écran de la personne | image noire, Wayland bloque |
| écran virtuel `Xvfb` + Chrome | **ça filme**, mais la page demande une connexion et les cookies ne se transportent pas : ils sont chiffrés par le trousseau |
| porte de pilotage de Chrome (port 9222) | fermée sur ce poste |

**Donc : la capture d'une page qui demande une connexion revient toujours à
la personne.** Un clic, et un seul. Ne pas tourner autour pendant vingt minutes.

## LE CHEMIN QUI MARCHE, EN TROIS TEMPS

### 1. La narration — chez Google, et on les remercie

`gcloud` est déjà connecté sur nomi, projet `control-tower-hackathon`.
**Ne rien modifier dans ce projet** : on ne fait que demander une voix.

```sh
T=$(gcloud auth print-access-token)
curl -s -X POST -H "Authorization: Bearer $T" \
  -H "x-goog-user-project: control-tower-hackathon" \
  -H "Content-Type: application/json; charset=utf-8" -d @requete.json \
  "https://texttospeech.googleapis.com/v1/text:synthesize" -o reponse.json
```

Le fichier `requete.json` contient le texte, la voix et la vitesse :

```json
{"input":{"text":"..."},
 "voice":{"languageCode":"fr-FR","name":"fr-FR-Chirp3-HD-Charon"},
 "audioConfig":{"audioEncoding":"LINEAR16","sampleRateHertz":24000,
                "speakingRate":0.96}}
```

La réponse contient le son encodé en base64, dans le champ `audioContent` :
on le décode et on écrit un fichier `.wav`.

**Les voix.** `Chirp3-HD` sont les plus récentes de Google. Quarante-deux
voix françaises, hommes et femmes. `Charon` est une voix d'homme, posée.
Pour en voir la liste :
`https://texttospeech.googleapis.com/v1/voices?languageCode=fr-FR`

**On cite Google sous la vidéo.** la personne y tient : la voix est fabriquée
avec Google Cloud Text-to-Speech, et on le dit.

### 2. La capture d'écran — un clic de la personne

```
spectacle -R s
```
`-R` veut dire enregistrer, `s` veut dire un écran entier. Spectacle demande
quel écran, puis un bouton arrête. **Lui dire quoi filmer et combien de temps**
— la durée de la voix se lit avec :
`ffprobe -v error -show_entries format=duration -of csv=p=0 voix.wav`

### 3. L'assemblage

```sh
ffmpeg -y -i capture.mp4 -i voix.wav \
  -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -shortest sortie.mp4
```
`-shortest` arrête au plus court des deux. Réussi quand `ffprobe` rend une
durée proche de celle de la voix.

## CE QU'IL NE FAUT PAS FAIRE

- **Pas de suite d'images**. Huit captures collées font un diaporama qui
  saute. la personne l'a dit : « on dirait un gif ». Il veut une capture continue.
- **Pas de `pkill -f <mot>`** si la commande contient elle-même ce mot :
  elle se tue toute seule. Deux fois payé le 04/09. Passer par les numéros
  de processus.
- **Ne pas manipuler le mot de passe de la personne** pour ouvrir une session
  dans un navigateur d'essai.

## OÙ C'EST RANGÉ

Sur nomi : `~/.claude/skills/video-narree/`
Sur la tour : `~/.claude/skills/video-narree/`
Les morceaux déjà faits : `~/livrables/videos/`
