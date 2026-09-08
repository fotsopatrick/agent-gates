#!/usr/bin/env bash
# CONTROLE MINIMAL DE garde-bonne-nuit
#
# Un garde sans controle est une promesse, pas un garde. Celui-ci est
# volontairement MINIMAL : il verifie deux choses seulement.
#   1. le garde se lit sans faute d ecriture ;
#   2. il sait REFUSER — on lui presente une entree vide et une entree
#      quelconque, et il ne doit jamais planter.
#
# A COMPLETER par la personne qui l installe : ajoute ici les cas que TU
# veux voir refuses. Un controle ecrit par quelqu un d autre ne connait pas
# tes fautes a toi.
set -u
G="$(dirname "$0")/../gates/garde-bonne-nuit.py"
VERT=0; ROUGE=0
ok()  { printf 'VERT   %s\n' "$1"; VERT=$((VERT+1)); }
nok() { printf 'ROUGE  %s\n' "$1"; ROUGE=$((ROUGE+1)); }

python3 -c "import ast,sys;ast.parse(open('$G',encoding='utf-8').read())" 2>/dev/null \
  && ok "garde-bonne-nuit se lit sans faute" || nok "garde-bonne-nuit a une faute d ecriture"

echo '{}' | python3 "$G" >/dev/null 2>&1 \
  && ok "il ne plante pas sur une entree vide" \
  || nok "il plante sur une entree vide"

echo '{"tool_name":"Bash","tool_input":{"command":"echo bonjour"}}' \
  | python3 "$G" >/dev/null 2>&1 \
  && ok "il ne plante pas sur une commande ordinaire" \
  || nok "il plante sur une commande ordinaire"

echo
if [ "$ROUGE" -eq 0 ]; then echo "$VERT / $((VERT+ROUGE)) verts"; exit 0
else echo "$VERT / $((VERT+ROUGE)) verts — $ROUGE ROUGE"; exit 1; fi
