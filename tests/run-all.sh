#!/usr/bin/env bash
# Lance le test de chaque garde. Un seul rouge fait echouer l'ensemble.
cd "$(dirname "$0")" || exit 1
export GATES_HOME="$(cd .. && pwd)"
vert=0; rouge=0
for t in test-*.sh; do
  [ -f "$t" ] || continue
  if bash "$t" >/dev/null 2>&1; then vert=$((vert+1)); echo "  VERT  $t"
  else rouge=$((rouge+1)); echo "  ROUGE $t"; fi
done
for t in test-*.py; do
  [ -f "$t" ] || continue
  if python3 "$t" >/dev/null 2>&1; then vert=$((vert+1)); echo "  VERT  $t"
  else rouge=$((rouge+1)); echo "  ROUGE $t"; fi
done
echo "----"
echo "RESULTAT : $vert vert / $rouge rouge"
[ "$rouge" -eq 0 ]
