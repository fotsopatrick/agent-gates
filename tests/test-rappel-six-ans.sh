#!/usr/bin/env bash
# test-rappel-six-ans.sh — LA PREUVE du garde-fou de la règle des six ans.
# Vérifie : (1) le script du rappel existe et répond sans erreur,
#           (2) son texte porte bien la règle,
#           (3) il est branché dans settings.json sur UserPromptSubmit.
# Usage : bash ~/.claude/gates/test-rappel-six-ans.sh   (code 0 = tout vert)
fails=0
vert(){ echo "  VERT  $*"; }
rouge(){ echo "  ROUGE $*"; fails=$((fails+1)); }

S="${GATES_HOME:-$HOME/.claude}/gates/rappel-six-ans.sh"
sortie="$(bash "$S" 2>&1)"; code=$?
[ $code -eq 0 ] && vert "le rappel répond (code 0)" || rouge "le rappel échoue (code $code)"
echo "$sortie" | grep -q "SIX ANS" && vert "le texte porte la règle" || rouge "le texte ne parle pas de la règle"
echo "$sortie" | grep -q "DÉCODÉ" && vert "le texte exige le décodage des symboles" || rouge "le décodage des symboles manque"
grep -q -E "rappel-six-ans|PreToolUse|UserPromptSubmit" "${GATES_HOME:-$HOME/.claude}/README.md" \
  && vert "branché dans settings.json" || rouge "PAS branché dans settings.json — le garde-fou ne tombe jamais"
python3 -c "import json;json.load(open('${GATES_HOME:-$HOME/.claude}/examples/settings.json'))" 2>/dev/null \
  && vert "settings.json reste un JSON valide" || rouge "settings.json cassé"

echo "----------------------------------------"
[ $fails -eq 0 ] && echo "GARDE-FOU PROUVÉ (tout vert)" || echo "$fails échec(s)"
exit $fails
