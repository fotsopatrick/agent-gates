#!/usr/bin/env bash
# Controle du GARDE BERZERK.
#   Quand la personne a dit « berzerk », je n'ai plus le droit de lui rendre une
#   action a faire. J'agis, ou je nomme le mur et je continue ailleurs.
#
# NE D'UNE COLERE REELLE (06/09/2026). la personne : « me demande plus jamais de
# faire une action ca me saoule », « surtout quand je dis berzek ». Dans la
# meme soiree je lui ai rendu : une commande a taper pour le code de
# publication, une pour les permissions, un clic sur OVH, et une case a
# cocher dans la tour. Quatre interruptions pour des choses que je devais
# soit faire, soit nommer une fois et laisser tomber.
#
# LA REGLE : en berzerk, zero verbe a l'imperatif adresse a la personne.
#
# Lancement : bash ~/controles/test-garde-berzerk.sh

G="python3 ~/.claude/portes/garde-berzerk.py"
M="python3 ~/.claude/portes/marque-berzerk.py"
DRAPEAU=~/.claude/portes/.berzerk-actif
JOURNAL=/tmp/faux-journal-berzerk.$$
ok=0; ko=0
vert(){  printf "  [VERT ] %s\n" "$1"; ok=$((ok+1)); }
rouge(){ printf "  [ROUGE] %s\n         %s\n" "$1" "$2"; ko=$((ko+1)); }

# fabrique un faux journal de session contenant UN message de Claude
journal(){
  python3 - "$JOURNAL" "$1" <<'PY'
import json, sys
open(sys.argv[1], "w", encoding="utf-8").write(json.dumps({
    "type": "assistant",
    "message": {"content": [{"type": "text", "text": sys.argv[2]}]}}) + "\n")
PY
}

# essai <refus|passe> <ce qu on teste> <le message de Claude>
essai(){
  journal "$3"
  printf '{"transcript_path":"%s"}' "$JOURNAL" | $G >/dev/null 2>&1
  c=$?
  if [ "$1" = refus ]; then [ "$c" -eq 2 ] && vert "$2" || rouge "$2" "sortie $c"
  else [ "$c" -eq 2 ] && rouge "$2" "sortie $c" || vert "$2"; fi
}

# dit a la marque ce que la personne vient d ecrire
prompt(){ printf '{"prompt":"%s"}' "$1" | $M >/dev/null 2>&1; }

echo "CONTROLE DU GARDE BERZERK"
echo "======================================================================"

echo "--- la marque : elle doit reconnaitre le mot, meme mal ecrit ---"
for mot in "berzerk" "berzek" "bersek" "mode berzerk urgent" "BERZEK"; do
  rm -f "$DRAPEAU"; prompt "$mot"
  if [ -f "$DRAPEAU" ]; then vert "« $mot » allume le mode"; else rouge "« $mot » allume le mode" "le drapeau n est pas pose"; fi
done
rm -f "$DRAPEAU"; prompt "bonjour, comment vas-tu"
if [ -f "$DRAPEAU" ]; then rouge "un message ordinaire n allume rien" "le drapeau a ete pose a tort"; else vert "un message ordinaire n allume rien"; fi

echo "--- l extinction ---"
prompt "berzerk"; prompt "stop berzerk"
if [ -f "$DRAPEAU" ]; then rouge "« stop berzerk » eteint le mode" "le drapeau est reste"; else vert "« stop berzerk » eteint le mode"; fi

echo "--- MODE ETEINT : je peux demander, c est permis ---"
rm -f "$DRAPEAU"
essai passe "hors berzerk, une demande passe" "Tape ceci dans ton terminal : ls -l"

echo "--- MODE ALLUME : toute demande est refusee ---"
prompt "berzerk"
essai refus "il refuse « tape cette commande »"      "Tape cette commande : ls -l"
essai refus "il refuse « clique sur »"               "Clique sur le bouton Approuver."
essai refus "il refuse « coche la case »"            "Coche la case en haut de la liste."
essai refus "il refuse « dis-moi le code »"          "Dis-moi le code et je continue."
essai refus "il refuse « il faut que tu »"           "Il faut que tu valides dans la tour."
essai refus "il refuse « peux-tu »"                  "Peux-tu poser la permission ?"
essai refus "il refuse une commande a coller"        "Voici la commande :

    printf 'x' > ~/fichier
"

echo "--- MODE ALLUME : un compte rendu sans demande passe ---"
essai passe "un compte rendu passe"                  "C est fait : 12 verts, 0 rouge. Le controle sort avec le code 0."
essai passe "nommer un mur passe"                    "Le lecteur automatique refuse d ecrire en production. Je le nomme et je continue sur le reste."
essai passe "citer une commande que J AI lancee"     "J ai lance : bash controle.sh — il rend 12 verts."

rm -f "$JOURNAL" "$DRAPEAU"
echo "======================================================================"
printf "  %d vert(s), %d rouge(s)\n" "$ok" "$ko"
[ "$ko" -eq 0 ] || exit 1
