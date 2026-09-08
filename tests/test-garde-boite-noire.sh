#!/usr/bin/env bash
# BANC D'ESSAI DU GARDE DE LA BOITE NOIRE.
# Un garde qui n'a jamais dit non est une promesse. Un garde qui dit non a
# tout finit debranche. On verifie les deux cotes.
set -u
G="${GARDE:-$HOME/.claude/portes/garde-boite-noire.py}"
VERT=0; ROUGE=0
essai() {          # essai <BLOQUE|PASSE> <titre> <chemin> <contenu>
  local attendu="$1" titre="$2" chemin="$3" contenu="$4" sortie obtenu
  sortie=$(python3 -c '
import json,sys
print(json.dumps({"tool_name":"Write","tool_input":{"file_path":sys.argv[1],"content":sys.argv[2]}}))' \
    "$chemin" "$contenu" | python3 "$G" 2>/dev/null)
  obtenu="PASSE"; case "$sortie" in *'"deny"'*) obtenu="BLOQUE";; esac
  if [ "$obtenu" = "$attendu" ]; then printf 'VERT   %s\n' "$titre"; VERT=$((VERT+1))
  else printf 'ROUGE  %s   (attendu %s, obtenu %s)\n' "$titre" "$attendu" "$obtenu"; ROUGE=$((ROUGE+1)); fi
}

LONG=$(python3 -c "print('Une phrase de fond sur les agents et la tour. ' * 45)")

echo "--- ce qu il DOIT refuser ---"
essai BLOQUE "un long article sans rien a regarder" \
  "$HOME/livrables/article-essai-vide.md" "# Titre

$LONG"
essai BLOQUE "un long article anglais sans rien a regarder" \
  "$HOME/livrables/en/article-essai-vide-en.md" "# Title

$LONG"

echo "--- ce qu il DOIT laisser passer ---"
essai PASSE "un article avec une capture d ecran" \
  "$HOME/livrables/article-essai-image.md" "# Titre

![la salle](captures/salle.png)

$LONG"
essai PASSE "un article avec un bloc de resultat reel" \
  "$HOME/livrables/article-essai-resultat.md" "# Titre

\`\`\`
16 verts sur 16
\`\`\`

$LONG"
essai PASSE "un article avec une video en ligne" \
  "$HOME/livrables/article-essai-video.md" "# Titre

https://youtu.be/abc123

$LONG"
essai PASSE "un article court (moins de 1500 signes)" \
  "$HOME/livrables/article-essai-court.md" "# Titre

Trois lignes, pas plus."
essai PASSE "une note interne, qui n est pas un article" \
  "$HOME/livrables/note-interne.md" "# Note

$LONG"
essai PASSE "un fichier qui n a rien a voir" \
  "$HOME/outils/machin.py" "$LONG"

echo
if [ "$ROUGE" -eq 0 ]; then echo "$VERT / $((VERT+ROUGE)) verts"; exit 0
else echo "$VERT / $((VERT+ROUGE)) verts — $ROUGE ROUGE"; exit 1; fi
