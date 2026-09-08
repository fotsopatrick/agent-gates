#!/usr/bin/env bash
# Banc de la porte a secrets. Aucune vraie valeur ici : que des faux
# manifestes (des A repetes), pour que le banc lui-meme ne soit pas une fuite.
PORTE="$(dirname "$0")/../gates/porte-secrets.py"
FAUX_GH="ghp_$(printf 'A%.0s' {1..30})"
FAUX_ANT="sk-ant-$(printf 'B%.0s' {1..30})"
vert=0; rouge=0

essai() { # nom, json, code attendu
  echo "$2" | python3 "$PORTE" >/dev/null 2>&1
  obtenu=$?
  if [ "$obtenu" = "$3" ]; then vert=$((vert+1)); printf "  OK   %s\n" "$1"
  else rouge=$((rouge+1)); printf "  RATE %s (attendu %s, obtenu %s)\n" "$1" "$3" "$obtenu"; fi
}

echo "Banc de la porte a secrets"
essai "P1 jeton GitHub dans une commande -> REFUS" \
  "{\"tool_input\":{\"command\":\"git remote add o https://x:$FAUX_GH@github.com/a/b\"}}" 2
essai "P2 cle Anthropic dans un fichier ecrit -> REFUS" \
  "{\"tool_input\":{\"content\":\"CLE=$FAUX_ANT\",\"file_path\":\"/tmp/a.py\"}}" 2
essai "P3 mot de passe dans une URL -> REFUS" \
  "{\"tool_input\":{\"command\":\"curl https://jean:motdepasse123@exemple.fr\"}}" 2
essai "P4 commande ordinaire -> PASSE" \
  "{\"tool_input\":{\"command\":\"ls -la /tmp/demo-home\"}}" 0
essai "P5 le magasin git a le DROIT d en contenir -> PASSE" \
  "{\"tool_input\":{\"content\":\"https://x:$FAUX_GH@github.com\",\"file_path\":\"/tmp/demo-home/.git-credentials\"}}" 0
essai "P6 entree illisible -> PASSE (une porte cassee ne bloque pas le travail)" \
  "pas du json" 0
essai "P7 rien a examiner -> PASSE" \
  "{\"tool_input\":{}}" 0
essai "P8 le mot jeton sans valeur -> PASSE (pas de refus au mot-cle)" \
  "{\"tool_input\":{\"command\":\"echo il faut revoquer le jeton github\"}}" 0

echo "-> $vert vert(s), $rouge rouge(s)"
[ "$rouge" = 0 ]
