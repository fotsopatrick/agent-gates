#!/usr/bin/env bash
# BANC D'ESSAI DU GARDE DES LIENS MORTS.
#
# NE D'UNE FAUTE REELLE (08/09/2026). J'ai publie une page qui annoncait
# « github.com/…/agent-gates ». L'adresse rendait 404 — introuvable. Ni le
# Sage (qui ne lit que le disque) ni mon banc d'essai ne l'ont vu. C'est
# la personne qui l'a trouve, en cliquant.
#
# Ce que le garde doit faire : quand on ECRIT un fichier qui annonce une
# adresse web, il verifie que l'adresse repond. Si elle est morte, il refuse.
# Ce qu'il ne doit PAS faire : refuser quand le reseau est coupe (sinon on
# ne peut plus travailler dans le train), ni ralentir chaque ecriture.
GARDE="${GATES_HOME:-$(cd "$(dirname "$0")/.." && pwd)}/gates/garde-lien-mort.py"
vert=0; rouge=0
essai(){ # nom, json, code attendu
  obtenu=$(echo "$2" | timeout 25 python3 "$GARDE" >/dev/null 2>&1; echo $?)
  if [ "$obtenu" = "$3" ]; then vert=$((vert+1)); printf "  VERT  %s\n" "$1"
  else rouge=$((rouge+1)); printf "  ROUGE %s (attendu %s, obtenu %s)\n" "$1" "$3" "$obtenu"; fi
}

echo "BANC D'ESSAI — le garde des liens morts"

essai "L1 une adresse morte dans une page -> REFUS" \
  '{"tool_name":"Write","tool_input":{"file_path":"/tmp/p.html","content":"<a href=\"https://github.com/fotsopatrick/ce-depot-nexiste-pas-du-tout\">code</a>"}}' 2

essai "L2 une adresse vivante -> PASSE" \
  '{"tool_name":"Write","tool_input":{"file_path":"/tmp/p.html","content":"<a href=\"https://github.com/fotsopatrick/agent-tracer\">code</a>"}}' 0

essai "L3 aucune adresse -> PASSE" \
  '{"tool_name":"Write","tool_input":{"file_path":"/tmp/p.py","content":"print(1)"}}' 0

essai "L4 une adresse d exemple -> PASSE (on ne verifie pas les exemples)" \
  '{"tool_name":"Write","tool_input":{"file_path":"/tmp/p.md","content":"ex : https://example.com/mon-projet"}}' 0

essai "L5 une adresse locale -> PASSE (elle n est pas publique)" \
  '{"tool_name":"Write","tool_input":{"file_path":"/tmp/p.md","content":"http://127.0.0.1:8000/"}}' 0

essai "L6 entree illisible -> PASSE (un garde casse ne bloque pas le travail)" \
  'ceci n est pas du json' 0

echo "----"
echo "RESULTAT : $vert vert / $rouge rouge"
[ "$rouge" -eq 0 ] || exit 1
