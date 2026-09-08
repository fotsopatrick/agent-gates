#!/usr/bin/env bash
# BANC D'ESSAI DU GARDE DE LA CAUSE.
#
# Un garde qui n'a jamais dit non est une promesse, pas un garde. Ce banc
# lui presente donc d'abord des reponses qu'il DOIT refuser (le rouge),
# puis des reponses qu'il DOIT laisser passer (le vert). Si un seul cas
# tombe du mauvais cote, le banc s'arrete en rouge.
#
# Usage :  bash ~/controles/test-garde-cause.sh
# Preuve :  la derniere ligne dit « N / N verts ».
set -u
GARDE="${GARDE_CAUSE:-$HOME/.claude/portes/garde-cause.py}"
VERT=0
ROUGE=0

# Chaque appel utilise une empreinte neuve, sinon le garde se tait parce
# qu'il croit relire le meme message.
essai() {           # essai <ce qu'on attend: BLOQUE|PASSE> <titre> <texte>
  local attendu="$1" titre="$2" texte="$3"
  local etat; etat=$(mktemp)
  rm -f "$etat"
  local sortie
  sortie=$(printf '%s' "$(python3 - "$texte" <<'PY'
import json, sys
print(json.dumps({"last_assistant_message": sys.argv[1]}))
PY
)" | GARDE_CAUSE_ETAT="$etat" python3 "$GARDE" 2>/dev/null)
  rm -f "$etat"
  local obtenu="PASSE"
  case "$sortie" in *'"decision": "block"'*|*'"decision":"block"'*) obtenu="BLOQUE";; esac
  if [ "$obtenu" = "$attendu" ]; then
    printf 'VERT   %s\n' "$titre"
    VERT=$((VERT+1))
  else
    printf 'ROUGE  %s   (attendu %s, obtenu %s)\n' "$titre" "$attendu" "$obtenu"
    ROUGE=$((ROUGE+1))
  fi
}

echo "--- ce que le garde DOIT refuser ---"
essai BLOQUE "repare sans cause et sans test rouge" \
  "J'ai repare la page. Elle s'affiche de nouveau."
essai BLOQUE "repare, cause nommee, mais aucun test vu rouge" \
  "J'ai corrige le probleme : ca ne marchait pas parce que le fichier lu n'etait pas celui qui est servi. Le test est vert."
essai BLOQUE "repare, test rouge montre, mais aucune cause nommee" \
  "J'ai repare. Le test etait rouge d'abord, il est vert maintenant : 9 verts, 0 rouge."
essai BLOQUE "ca remarche, rien d'autre" \
  "Ca remarche maintenant, le robot repond."
essai BLOQUE "le probleme est regle, sans rien montrer" \
  "Le probleme est resolu."

echo "--- ce que le garde DOIT laisser passer ---"
essai PASSE "cause nommee ET test vu rouge avant" \
  "J'ai repare. La cause : le programme lisait vitrine.txt alors que le portier sert erreurs/regles/vitrine.txt. J'ai ecrit le test sur ce chemin, il etait rouge d'abord ; apres la correction : 8 verts, 0 rouge."
essai PASSE "aucune reparation annoncee" \
  "Voici ce que j'ai trouve : la page repond 200 et la carte contient 461 elements."
essai PASSE "le geste appartient a la personne" \
  "Le probleme est resolu du cote du programme, mais la mise en ligne demande ta main : le bouton est pret dans ton cockpit."
essai PASSE "je ne sais pas encore" \
  "Je ne sais pas encore pourquoi la page tombe. Ce qui trancherait : lire le journal du portier au moment exact de la panne."
essai PASSE "reparation avec reproduction de la panne" \
  "Corrige. L'origine etait un port deja pris par le jeu. Le test reproduit la panne et il a d'abord echoue ; il rend maintenant 12 / 12."

echo "--- le garde est-il POSE aux deux endroits ? ---"
verifie() {         # verifie <titre> <commande qui doit reussir>
  local titre="$1"; shift
  if "$@" >/dev/null 2>&1; then
    printf 'VERT   %s\n' "$titre"; VERT=$((VERT+1))
  else
    printf 'ROUGE  %s\n' "$titre"; ROUGE=$((ROUGE+1))
  fi
}
verifie "le garde Claude existe et se lit" python3 -c "import ast,sys;ast.parse(open('$GARDE',encoding='utf-8').read())"
verifie "il est branche a la fin du tour de Claude" \
  grep -q "garde-cause.py" "$HOME/.claude/settings.json"
verifie "le garde opencode existe" \
  test -s "$HOME/.config/opencode/plugin/garde-cause.ts"
verifie "il porte bien la regle de la cause" \
  grep -q "GARDE DE LA CAUSE" "$HOME/.config/opencode/plugin/garde-cause.ts"
verifie "il exige le test vu ROUGE d'abord" \
  grep -q "ROUGE D'ABORD" "$HOME/.config/opencode/plugin/garde-cause.ts"
verifie "il s'accroche comme les autres gardes opencode" \
  grep -q "experimental.chat.system.transform" "$HOME/.config/opencode/plugin/garde-cause.ts"

echo
if [ "$ROUGE" -eq 0 ]; then
  echo "$VERT / $((VERT+ROUGE)) verts"
  exit 0
else
  echo "$VERT / $((VERT+ROUGE)) verts — $ROUGE ROUGE"
  exit 1
fi
