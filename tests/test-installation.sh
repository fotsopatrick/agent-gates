#!/usr/bin/env bash
# BANC D'ESSAI DE L'INSTALLATION EN UNE COMMANDE.
#
# Ce qu'on prouve, et pourquoi chaque point existe :
#   1. l'installation marche sur une machine VIERGE, pas seulement la mienne ;
#   2. apres elle, un garde REFUSE vraiment quelque chose (sinon on a livre
#      une promesse, pas un garde) ;
#   3. rien de personnel n'est copie chez la personne ;
#   4. relancer l'installation ne casse pas des reglages deja en place.
#
# Le banc fabrique une fausse maison (un dossier temporaire qui joue le role
# du dossier personnel) : la vraie machine n'est jamais touchee.
set -u
ICI="$(cd "$(dirname "$0")/.." && pwd)"
MAISON="$(mktemp -d)"
trap 'rm -rf "$MAISON"' EXIT
vert=0; rouge=0
v(){ vert=$((vert+1)); echo "  VERT  $1"; }
r(){ rouge=$((rouge+1)); echo "  ROUGE $1"; [ -n "${2:-}" ] && echo "        $2"; }

echo "BANC D'ESSAI — l'installation en une commande"
echo "  maison d'essai : $MAISON"

# 0. LE SCRIPT EXISTE
[ -x "$ICI/install.sh" ] && v "install.sh existe et est lancable" \
  || { r "install.sh manque ou n est pas lancable"; echo "RESULTAT : $vert vert / $((rouge)) rouge"; exit 1; }

# 1. IL TOURNE SUR UNE MACHINE VIERGE
sortie="$(HOME="$MAISON" bash "$ICI/install.sh" 2>&1)"; code=$?
[ "$code" -eq 0 ] && v "l installation finit sans erreur" \
  || r "l installation echoue (code $code)" "$(echo "$sortie" | tail -3)"

# 2. LES REGLAGES EXISTENT ET SONT LISIBLES PAR UNE MACHINE
REG="$MAISON/.claude/settings.json"
[ -s "$REG" ] && v "le fichier de reglages est ecrit" || r "aucun reglage ecrit"
python3 -c "import json,sys; json.load(open('$REG'))" 2>/dev/null \
  && v "les reglages sont un JSON valide" || r "les reglages sont casses"

# 3. LE POINT QUI COMPTE : UN GARDE REFUSE POUR DE VRAI
FAUX="ghp_$(printf 'A%.0s' {1..30})"
echo "{\"tool_input\":{\"command\":\"git push https://x:$FAUX@github.com/a/b\"}}" \
  | python3 "$MAISON/.claude/gates/porte-secrets.py" >/dev/null 2>&1
[ $? -eq 2 ] && v "un garde installe REFUSE un secret en clair" \
  || r "le garde installe ne refuse rien" "un garde qui n a jamais dit non ne garde rien"

# 4. ET IL LAISSE PASSER L ORDINAIRE
echo '{"tool_input":{"command":"ls -la"}}' \
  | python3 "$MAISON/.claude/gates/porte-secrets.py" >/dev/null 2>&1
[ $? -eq 0 ] && v "il laisse passer une commande ordinaire" \
  || r "il refuse tout" "un garde qui refuse tout ne garde rien non plus"

# 5. RIEN DE PERSONNEL N EST PARTI CHEZ LA PERSONNE
sale=0
for mot in "matourdecontrole" "192.168.1" "145.239.77" "/home/orel" "/home/ubuntu" "Patrick" "tour-vps"; do
  if grep -rqi -- "$mot" "$MAISON/.claude/gates" "$MAISON/.claude/skills" 2>/dev/null; then
    r "« $mot » est parti chez la personne" "un cockpit generique ne porte pas mes donnees"; sale=1
  fi
done
[ "$sale" -eq 0 ] && v "aucune trace personnelle installee (7 mots cherches)"

# 6. RELANCER NE CASSE RIEN
python3 - "$REG" <<'PY'
import json,sys
d=json.load(open(sys.argv[1])); d["env"]={"MON_REGLAGE":"a-moi"}
json.dump(d,open(sys.argv[1],"w"),indent=2)
PY
HOME="$MAISON" bash "$ICI/install.sh" >/dev/null 2>&1
python3 - "$REG" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
sys.exit(0 if d.get("env",{}).get("MON_REGLAGE")=="a-moi" else 1)
PY
[ $? -eq 0 ] && v "relancer garde les reglages deja en place" \
  || r "relancer efface les reglages de la personne" "on ne pietine pas chez les gens"

echo "----"
echo "RESULTAT : $vert vert / $rouge rouge"
[ "$rouge" -eq 0 ] || exit 1
