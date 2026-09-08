#!/usr/bin/env bash
# BANC D'ESSAI DU GARDE DES DEPOTS DE CONCOURS.
#
# Un garde qui n'a jamais dit non est une promesse, pas un garde.
# Un garde qui dit non a tout finit debranche, et alors il ne garde plus rien.
# Ce banc verifie les deux cotes.
set -u
G="${GARDE:-$HOME/.claude/portes/garde-depots-concours.py}"
VERT=0; ROUGE=0

essai() {          # essai <BLOQUE|PASSE> <titre> <json d entree>
  local attendu="$1" titre="$2" entree="$3" sortie obtenu
  sortie=$(printf '%s' "$entree" | python3 "$G" 2>/dev/null)
  obtenu="PASSE"
  case "$sortie" in *'"deny"'*) obtenu="BLOQUE";; esac
  if [ "$obtenu" = "$attendu" ]; then
    printf 'VERT   %s\n' "$titre"; VERT=$((VERT+1))
  else
    printf 'ROUGE  %s   (attendu %s, obtenu %s)\n' "$titre" "$attendu" "$obtenu"
    ROUGE=$((ROUGE+1))
  fi
}

j() { python3 -c '
import json,sys
print(json.dumps({"tool_name": sys.argv[1], "tool_input": json.loads(sys.argv[2])}))' "$1" "$2"; }

echo "--- ce qu il DOIT refuser ---"
essai BLOQUE "ecrire un fichier dans le donjon rendu" \
  "$(j Write '{"file_path": "'"$HOME"'/donjon-vr/index.html"}')"
essai BLOQUE "modifier un fichier du projet WebMCP" \
  "$(j Edit '{"file_path": "'"$HOME"'/donjon-vr/webmcp/webmcp.js"}')"
essai BLOQUE "ecrire dans le labo 3D" \
  "$(j Write '{"file_path": "'"$HOME"'/labo-3d/index.html"}')"
essai BLOQUE "effacer quelque chose dans le labo 3D" \
  "$(j Bash '{"command": "rm -rf '"$HOME"'/labo-3d/modeles"}')"
essai BLOQUE "enregistrer une modification (git commit)" \
  "$(j Bash '{"command": "cd '"$HOME"'/donjon-vr && git commit -am corrections"}')"
essai BLOQUE "ecrire par une redirection dans le donjon" \
  "$(j Bash '{"command": "echo bonjour > '"$HOME"'/donjon-vr/note.txt"}')"
essai BLOQUE "toucher la candidature SGRM" \
  "$(j Write '{"file_path": "'"$HOME"'/SGRM_PROJECT/readme.md"}')"
essai BLOQUE "pousser vers le depot distant du concours" \
  "$(j Bash '{"command": "git push https://github.com/fotsopatrick/control-tower main"}')"
essai BLOQUE "effacer dans le seau Google du jeu rendu" \
  "$(j Bash '{"command": "gsutil -m rm -r gs://kotoage-webmcp-20260901-133904/webmcp"}')"
essai BLOQUE "recopier par-dessus le seau Google" \
  "$(j Bash '{"command": "gsutil rsync -r -d ./web gs://kotoage-webmcp-20260901-133904"}')"
essai BLOQUE "televerser avec gcloud storage" \
  "$(j Bash '{"command": "gcloud storage cp index.html gs://kotoage-webmcp-20260901-133904/"}')"

echo "--- ce qu il DOIT laisser passer ---"
essai PASSE "LIRE un fichier du donjon" \
  "$(j Bash '{"command": "cat '"$HOME"'/donjon-vr/index.html"}')"
essai PASSE "chercher dedans" \
  "$(j Bash '{"command": "grep -rn webmcp '"$HOME"'/donjon-vr"}')"
essai PASSE "lister le seau Google (lire ne change rien)" \
  "$(j Bash '{"command": "gsutil ls gs://kotoage-webmcp-20260901-133904/"}')"
essai PASSE "copier le donjon AILLEURS pour travailler sur la copie" \
  "$(j Bash '{"command": "cp -r '"$HOME"'/donjon-vr-copie '"$HOME"'/chantier-victoria"}')"
# Troisieme faux positif paye le 08/09/2026 : le garde a refuse
#   cp -r ~/labo-3d ~/labo-evolution
# alors que c est une LECTURE du labo et une ecriture AILLEURS. Il ne
# distinguait pas d ou l on copie de vers ou. Pour cp et mv, seule la
# DESTINATION compte — c est le dernier mot de la commande.
essai PASSE "copier un dossier rendu VERS un dossier neuf" \
  "$(j Bash '{"command": "cp -r '"$HOME"'/labo-3d '"$HOME"'/labo-evolution"}')"
essai PASSE "copier le donjon rendu vers un chantier" \
  "$(j Bash '{"command": "cp -r '"$HOME"'/donjon-vr '"$HOME"'/chantier-victoria"}')"
# Le banc ne testait que des commandes SIMPLES. La vraie vie les enchaine
# avec « && ». Sans ce cas, le banc disait vert pendant que le garde refusait.
essai PASSE "copier ailleurs, dans une commande enchainee avec &&" \
  "$(j Bash '{"command": "cp -r '"$HOME"'/labo-3d '"$HOME"'/labo-evolution && du -sh '"$HOME"'/labo-evolution"}')"
essai PASSE "copier ailleurs puis lister, enchaine par point-virgule" \
  "$(j Bash '{"command": "cp -r '"$HOME"'/donjon-vr '"$HOME"'/chantier ; ls '"$HOME"'/chantier"}')"
essai BLOQUE "copier VERS le dossier rendu, meme enchaine" \
  "$(j Bash '{"command": "echo bonjour && cp -r '"$HOME"'/ailleurs '"$HOME"'/labo-3d/nouveau"}')"
essai BLOQUE "copier quelque chose VERS le dossier rendu" \
  "$(j Bash '{"command": "cp -r '"$HOME"'/ailleurs '"$HOME"'/labo-3d/nouveau"}')"
essai PASSE "ecrire dans un dossier qui n a rien a voir" \
  "$(j Write '{"file_path": "'"$HOME"'/livrables/note.md"}')"
# Ne d un faux positif reel (08/09/2026) : le garde a refuse un simple « ls »
# parce que la commande contenait « 2>/dev/null ». Une lecture bloquee, c est
# un garde qu on debranche.
essai PASSE "lister les dossiers en jetant les erreurs (2>/dev/null)" \
  "$(j Bash '{"command": "ls -d '"$HOME"'/labo-3d '"$HOME"'/donjon-vr 2>/dev/null"}')"
essai PASSE "compter des fichiers dedans en jetant les erreurs" \
  "$(j Bash '{"command": "find '"$HOME"'/donjon-vr -name *.js 2>/dev/null | wc -l"}')"
essai PASSE "ecrire dans un dossier au nom qui se ressemble" \
  "$(j Write '{"file_path": "'"$HOME"'/donjon-vr-bankingWorldOld/note.md"}')"
# Second faux positif paye le meme jour : on ne pouvait plus reparer le garde
# lui-meme, parce que le nom d un dossier rendu apparaissait dans son texte.
essai PASSE "reparer le garde lui-meme" \
  "$(j Write '{"file_path": "'"$HOME"'/.claude/portes/garde-depots-concours.py"}')"
essai PASSE "ecrire son banc d essai" \
  "$(j Bash '{"command": "sed -i s/x/y/ '"$HOME"'/controles/test-garde-depots-concours.sh"}')"

echo
if [ "$ROUGE" -eq 0 ]; then echo "$VERT / $((VERT+ROUGE)) verts"; exit 0
else echo "$VERT / $((VERT+ROUGE)) verts — $ROUGE ROUGE"; exit 1; fi
