#!/usr/bin/env bash
# BANC D'ESSAI du mot de passe de berzerk.
#
# La regle de Patrick (07/09/2026) : « mot de passe utilise dans le cas ou on
# utilise la competence berzerk » et « si on passe par le circuit normal pas
# besoin, on doit juste remplir les conditions ».
#
# Donc on verifie SURTOUT le refus : le mot « berzerk » seul ne doit PLUS
# allumer le mode. Un garde qui n'a jamais dit non est une promesse.
set -u
PORTE="${GATES_HOME:-$HOME/.claude}/gates/marque-berzerk.py"
BAC=$(mktemp -d)
export BERZERK_DRAPEAU="$BAC/drapeau"
export BERZERK_EMPREINTE="$BAC/empreinte"
# le mot de passe du banc d'essai : « ouvre-toi ». On ne range que l'empreinte.
printf '%s' "ouvre-toi" | sha256sum | cut -d' ' -f1 > "$BERZERK_EMPREINTE"
ok=0; ko=0

envoie() {
  printf '{"prompt": %s}' "$(python3 -c 'import json,sys;print(json.dumps(sys.argv[1]))' "$1")" \
    | python3 "$PORTE" >/dev/null 2>&1
}

essai() { # $1 = message, $2 = "allume" ou "eteint"
  rm -f "$BERZERK_DRAPEAU"
  [ "$3" = "deja" ] && echo 0 > "$BERZERK_DRAPEAU"
  envoie "$1"
  if [ -f "$BERZERK_DRAPEAU" ]; then etat=allume; else etat=eteint; fi
  if [ "$etat" = "$2" ]; then ok=$((ok+1)); echo "  VERT  $2 comme prevu : $1"
  else ko=$((ko+1)); echo "  ROUGE attendu $2, obtenu $etat : $1"; fi
}

echo "BANC D'ESSAI — le mot de passe de berzerk"
essai "berzerk"                          eteint  neuf
essai "vas y berzek fonce"               eteint  neuf
essai "berzerk avec-le-mauvais-mot"      eteint  neuf
essai "berzerk ouvre-toi"                allume  neuf
essai "ouvre-toi passe en berzek"        allume  neuf
essai "ouvre-toi"                        eteint  neuf
essai "stop berzerk"                     eteint  deja
essai "montre moi la carte"              eteint  neuf
echo "----"
echo "RESULTAT : $ok vert / $ko rouge"
rm -rf "$BAC"
[ "$ko" -eq 0 ] || exit 1
