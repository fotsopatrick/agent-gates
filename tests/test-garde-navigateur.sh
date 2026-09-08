#!/usr/bin/env bash
# Contrôle du garde du navigateur.
#   Il DOIT refuser un navigateur CACHÉ — une fenêtre que Patrick ne voit pas.
#   Il DOIT laisser passer une page ouverte À L'ÉCRAN chez lui.
G="python3 ${GATES_HOME:-$HOME/.claude}/gates/garde-navigateur.py"
ok=0; ko=0
vert(){ printf "  \033[32mOK\033[0m   %s\n" "$1"; ok=$((ok+1)); }
rouge(){ printf "  \033[31mRATÉ\033[0m %s (sortie %s)\n" "$1" "$2"; ko=$((ko+1)); }

essai(){ # essai <refus|passe> <ce qu on teste> <la commande>
  printf '{"tool_name":"Bash","tool_input":{"command":%s}}' \
    "$(printf '%s' "$3" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')" \
    | $G >/dev/null 2>&1
  c=$?
  if [ "$1" = refus ]; then
    [ "$c" -eq 2 ] && vert "$2" || rouge "$2" "$c"
  else
    [ "$c" -eq 2 ] && rouge "$2" "$c" || vert "$2"
  fi
}

echo "=== IL REFUSE CE QUI EST CACHÉ ==="
essai refus "sans écran du tout"              "google-chrome --headless https://exemple.fr"
essai refus "un mode qui ne montre rien"      "google-chrome --dump-dom https://exemple.fr"
essai refus "une capture sans fenêtre"        "google-chrome --screenshot=/tmp/a.png https://exemple.fr"
essai refus "une impression sans fenêtre"     "google-chrome --print-to-pdf=/tmp/a.pdf https://exemple.fr"
essai refus "un profil à part"                "google-chrome --user-data-dir=/tmp/x https://exemple.fr"
essai refus "piloté de l'extérieur"           "chromium --remote-debugging-port=9333"
essai refus "un faux écran"                   "xvfb-run google-chrome https://exemple.fr"
essai refus "le navigateur partagé"           "setsid ~/outils/chrome-agents/chrome-agents.sh"
essai refus "un pilote qui lance le sien"     "node -e \"require('playwright').chromium.launch()\""

echo "=== IL LAISSE PASSER CE QUI EST VISIBLE ==="
essai passe "ouvrir une page à l'écran"       "setsid xdg-open https://example.com/endroit-sur &"
essai passe "ouvrir Chrome en vraie fenêtre"  "google-chrome https://example.com"
essai passe "parler au navigateur déjà ouvert" "node ~/outils/nav.js photo pippit page.png"
essai passe "lire une page sans navigateur"   "curl -s https://exemple.fr"
essai passe "se brancher sur un existant"     "node -e \"playwright.chromium.connect('ws://x')\""

echo "=== IL LAISSE PASSER CE QUI NE FAIT QU'ÉCRIRE ==="
essai passe "écrire --headless dans un fichier" "cat > /tmp/note.txt <<'FIN'
on parle de --headless et de chrome-agents ici, sans rien lancer
FIN"
essai passe "un script qui contient le mot"   "python3 - <<'PY'
s = 'google-chrome --dump-dom'
open('/tmp/x.py','w').write(s)
PY"

echo
echo "──────────────────────────────"
printf "  %d contrôles verts, %d ratés\n" "$ok" "$ko"
[ "$ko" -eq 0 ] || exit 1
