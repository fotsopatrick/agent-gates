#!/usr/bin/env bash
# BANC D'ESSAI du garde « on repare tout de suite ».
# Un garde qui n a jamais dit non est une promesse. On verifie donc d abord
# qu il REFUSE, puis qu il se tait quand il doit se taire.
GARDE="python3 ${GATES_HOME:-$HOME/.claude}/gates/garde-reparer-tout-de-suite.py"
ok=0; ko=0

essai() { # $1 = refus|passe, $2 = ce qu on teste, $3 = la reponse de l agent
  printf '{"last_assistant_message": %s}' \
    "$(python3 -c 'import json,sys;print(json.dumps(sys.argv[1]))' "$3")" \
    | $GARDE >/dev/null 2>&1
  c=$?
  if [ "$1" = refus ]; then
    if [ "$c" -eq 2 ]; then ok=$((ok+1)); echo "  VERT  refuse bien : $2"
    else ko=$((ko+1)); echo "  ROUGE laisse passer (sortie $c) : $2"; fi
  else
    if [ "$c" -eq 0 ]; then ok=$((ok+1)); echo "  VERT  laisse passer : $2"
    else ko=$((ko+1)); echo "  ROUGE refuse pour rien (sortie $c) : $2"; fi
  fi
}

echo "=== IL REFUSE QU ON REPOUSSE UNE REPARATION ==="
essai refus "il note au lieu de reparer" \
  "J ai trouve la cause. Je le note comme a reparer."
essai refus "il remet a plus tard" \
  "Le compteur est faux, a corriger plus tard."
essai refus "il met dans la liste" \
  "Deux tests sont rouges. Je mets ca dans ce qui reste."

echo "=== IL LAISSE PASSER QUAND ON A AGI ==="
essai passe "il a repare et relance le test" \
  "Le compteur etait faux. J ai corrige la ligne et relance le test : 11 vert / 0 rouge."
essai passe "la reparation demande la main de Patrick" \
  "Je le note comme a reparer : il faut ton mot de passe, c est ta main qui manque."
essai passe "une reponse ordinaire" \
  "La carte du PC repond, 534 elements dans 9 zones."
echo "----"
echo "RESULTAT : $ok vert / $ko rouge"
[ "$ko" -eq 0 ] || exit 1
