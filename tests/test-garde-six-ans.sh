#!/usr/bin/env bash
# test-garde-six-ans.sh — LA PREUVE du garde de sortie « règle des six ans ».
#
# Le rappel posé le 21/08 ne faisait que PARLER à Claude à chaque message ; il
# ne regardait jamais ce qu'il écrivait. Patrick l'a constaté : « le garde-fou
# des 6 ans ne semble pas fonctionner ». Un garde qui ne contrôle rien ne garde
# rien. Ce banc prouve le vrai garde : celui qui LIT le message final et
# REFUSE de finir le tour quand il est illisible.
#
# Usage : bash ~/.claude/gates/test-garde-six-ans.sh   (code 0 = tout vert)
set -u
GARDE="${GATES_HOME:-$HOME/.claude}/gates/garde-six-ans.py"
fails=0
vert(){ echo "  VERT  $*"; }
rouge(){ echo "  ROUGE $*"; fails=$((fails+1)); }

if [ ! -f "$GARDE" ]; then
  echo "ROUGE TOTAL : $GARDE n'existe pas encore — le garde n'est pas posé."
  exit 99
fi

BAC="$(mktemp -d -t bac-six-ans.XXXXXXXX)"
trap 'rm -rf "$BAC"' EXIT

# fabrique un faux journal de conversation dont le dernier message est $1
journal(){
  python3 - "$1" "$BAC/transcript.jsonl" <<'PY'
import json, sys
texte = sys.argv[1]
with open(sys.argv[2], "w", encoding="utf-8") as f:
    f.write(json.dumps({"type": "user", "message": {"content": "salut"}}) + "\n")
    f.write(json.dumps({"type": "assistant",
                        "message": {"content": [{"type": "text", "text": texte}]}}) + "\n")
PY
}

# lance le garde sur ce journal ; rend "BLOQUE" ou "PASSE"
juge(){
  local sortie
  sortie="$(printf '{"transcript_path":"%s","stop_hook_active":false}' "$BAC/transcript.jsonl" \
            | python3 "$GARDE" 2>/dev/null)"
  case "$sortie" in (*'"block"'*) echo BLOQUE;; (*) echo PASSE;; esac
}

essai(){ # essai <attendu BLOQUE|PASSE> <libelle> <texte>
  journal "$3"
  local obtenu; obtenu="$(juge)"
  if [ "$obtenu" = "$1" ]; then vert "$2 -> $obtenu"; else rouge "$2 : attendu $1, obtenu $obtenu"; fi
}

echo "=== 1. un message clair et court doit PASSER ==="
essai PASSE "reponse simple" \
"L'etude est prete mais pas encore sur le site. Il manque une signature, et c'est toi qui la donnes. Dis-moi le numero affiche."

echo "=== 2. un pave doit etre BLOQUE ==="
PAVE="$(python3 -c "print('La porte de confidentialite a ete ouverte et le circuit repris. ' * 45)")"
essai BLOQUE "message trop long" "$PAVE"

echo "=== 3. du jargon non decode doit etre BLOQUE ==="
essai BLOQUE "jargon nu (cron)" \
"J'ai mis le cron en place et tout est vert de mon cote, tu peux regarder."
essai PASSE "jargon decode juste apres" \
"J'ai mis en place un cron (une minuterie qui lance une commande toute seule) et il tourne."

echo "=== 4. une commande sans preuve de reussite doit etre BLOQUE ==="
essai BLOQUE "commande sans preuve" \
"Colle ceci :
! ssh remote-host 'bash deploy/publier.sh'
Voila, ce sera fait."
essai PASSE "commande avec preuve" \
"Colle ceci :
! ssh remote-host 'bash deploy/publier.sh'
C'est reussi quand elle affiche PUBLIE, tout vert."

echo "=== 7. LA LECON A LA PLACE DE LA REPARATION (05/09/2026) ==="
# Ce qui est arrive : sept epreuves de la tour dormaient depuis un mois. J'ai
# trouve la cause — une mission jamais deposee — et au lieu de la corriger,
# j'ai ecrit « ce qu'il faut retenir : c'est un trou dans la tour ». Patrick :
# « faut pas retenir, faut fixer ». Un defaut trouve se repare ; le raconter
# n'est pas le reparer. Un texte qui nomme un defaut ET en fait une lecon SANS
# annoncer la reparation est donc refuse.
essai BLOQUE "lecon sans reparation" \
"Ce qu'il faut retenir : quand la mission n'est pas deposee, rien ne repasse derriere. C'est un trou dans la tour, pas une panne d'agent."
essai PASSE "meme defaut, mais je le repare" \
"Quand la mission n'est pas deposee, rien ne repasse derriere : c'est un trou dans la tour. Je le bouche tout de suite, le controle est deja ecrit."
essai PASSE "une lecon sans defaut nomme" \
"Ce qu'il faut retenir : ta tour refuse de dire qu'une page privee existe. C'est voulu, et c'est bien."

echo "=== 5. le garde ne doit jamais boucler ==="
journal "$PAVE"
SORTIE="$(printf '{"transcript_path":"%s","stop_hook_active":true}' "$BAC/transcript.jsonl" | python3 "$GARDE" 2>/dev/null)"
case "$SORTIE" in (*'"block"'*) rouge "il bloque encore alors qu'il vient de bloquer : boucle infinie";;
                  (*) vert "deuxieme passage : ne bloque plus (pas de boucle)";; esac

echo "=== 6. UN MESSAGE DE RETARD : le defaut du 21/08 ==="
# Le garde « bonne nuit » a bloque deux fois en citant un message DEJA
# juge : quand il tourne, le message tout juste fini n'est pas encore
# ecrit dans le journal. Il condamnait donc le precedent. Un garde qui
# juge le mauvais texte accuse a tort — il doit se taire plutot.
export GARDE_SIX_ANS_ETAT="$BAC/etat"
journal "J'ai mis le cron en place et tout est vert."
[ "$(juge)" = BLOQUE ] && vert "premier passage : le texte neuf est juge" || rouge "premier passage : aurait du bloquer"
[ "$(juge)" = PASSE ] && vert "meme texte re-presente : ne juge pas deux fois" || rouge "il rejuge un texte deja juge (un message de retard)"
unset GARDE_SIX_ANS_ETAT

echo "=== 7. journal illisible : ne bloque pas ==="
SORTIE="$(printf '{"transcript_path":"/inexistant/nulle-part.jsonl"}' | python3 "$GARDE" 2>/dev/null)"
case "$SORTIE" in (*'"block"'*) rouge "il bloque sur un journal absent";;
                  (*) vert "journal absent : laisse passer";; esac

echo "----------------------------------------"
[ $fails -eq 0 ] && echo "GARDE DES SIX ANS PROUVE (tout vert)" || echo "$fails echec(s)"
exit $fails
