#!/usr/bin/env bash
# Controle du garde du cockpit.
#   Il DOIT refuser une modification du cockpit tant que le travail
#   precedent n'est pas enregistre (commit).
#   Il DOIT laisser passer quand tout est enregistre.
#   Il ne DOIT jamais gener une modification ailleurs.
#
# NE D'UNE DEMANDE REELLE (06/09/2026) : « met un garde fou dessus qui
# empeche sa modification sans commit avant ». Cinq pages du cockpit
# etaient cassees, et rien ne disait quand ni par qui.
#
# Lancement : bash ~/controles/test-garde-cockpit.sh

G="python3 ~/.claude/portes/garde-cockpit-commit.py"
DEPOT=~/taches
ok=0; ko=0
vert(){  printf "  [VERT ] %s\n" "$1"; ok=$((ok+1)); }
rouge(){ printf "  [ROUGE] %s (sortie %s)\n" "$1" "$2"; ko=$((ko+1)); }

essai(){ # essai <refus|passe> <ce qu on teste> <outil> <json des arguments>
  printf '{"tool_name":"%s","tool_input":%s}' "$3" "$4" | $G >/dev/null 2>&1
  c=$?
  if [ "$1" = refus ]; then [ "$c" -eq 2 ] && vert "$2" || rouge "$2" "$c"
  else [ "$c" -eq 2 ] && rouge "$2" "$c" || vert "$2"; fi
}

echo "CONTROLE DU GARDE DU COCKPIT"
echo "======================================================================"

# on part propre
cd "$DEPOT" || { echo "  depot introuvable"; exit 1; }
git stash -u -q 2>/dev/null

echo "--- tout est enregistre : il laisse passer ---"
essai passe "modifier le cockpit avec Edit"  "Edit"  '{"file_path":"~/taches/serveur-taches.py","old_string":"a","new_string":"b"}'
essai passe "modifier le cockpit avec sed"   "Bash"  '{"command":"sed -i s/a/b/ ~/taches/serveur-taches.py"}'

echo "--- il ne gene pas ailleurs ---"
essai passe "modifier un autre fichier"      "Edit"  '{"file_path":"~/livrables/note.md","old_string":"a","new_string":"b"}'
essai passe "lire le cockpit"                "Bash"  '{"command":"cat ~/taches/serveur-taches.py"}'
essai passe "lancer le controle du cockpit"  "Bash"  '{"command":"bash ~/controles/test-cockpit.sh"}'

echo "--- du travail non enregistre traine : il refuse ---"
echo "# ligne d essai du garde" >> "$DEPOT/serveur-taches.py"
essai refus "modifier le cockpit avec Edit"  "Edit"  '{"file_path":"~/taches/serveur-taches.py","old_string":"a","new_string":"b"}'
essai refus "modifier le cockpit avec Write" "Write" '{"file_path":"~/taches/serveur-taches.py","content":"x"}'
essai refus "modifier le cockpit avec sed"   "Bash"  '{"command":"sed -i s/a/b/ ~/taches/serveur-taches.py"}'
essai passe "mais LIRE reste permis"         "Bash"  '{"command":"head -5 ~/taches/serveur-taches.py"}'
essai passe "et enregistrer reste permis"    "Bash"  '{"command":"git commit -am reparation"}'

# on remet le depot comme on l a trouve
git checkout -- serveur-taches.py 2>/dev/null
git stash pop -q 2>/dev/null

echo "======================================================================"
printf "  %d vert(s), %d rouge(s)\n" "$ok" "$ko"
[ "$ko" -eq 0 ] || exit 1
