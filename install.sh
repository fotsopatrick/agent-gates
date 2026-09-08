#!/usr/bin/env bash
# INSTALLATION EN UNE COMMANDE — agent-gates.
#
# Ce qu'elle fait, en une phrase : elle pose les gardes chez vous et les
# branche autour de votre agent, sans jamais ecraser vos reglages a vous.
#
# LA REGLE QUI COMPTE : un garde dont le test est ROUGE n'est PAS installe.
# On ne pose pas chez les gens une promesse non prouvee. La liste des gardes
# ecartes s'affiche a la fin, avec la raison.
#
# Elle ne demande aucun droit d'administrateur, ne telecharge rien, et
# n'envoie rien nulle part.
set -u
SOURCE="$(cd "$(dirname "$0")" && pwd)"
MAISON="${HOME:?}"
CIBLE="$MAISON/.claude"
vert=0; ecartes=""

echo "AGENT-GATES — installation"
echo "  chez        : $CIBLE"
echo "  depuis      : $SOURCE"

command -v python3 >/dev/null || { echo "ARRET : python3 manque."; exit 1; }
mkdir -p "$CIBLE/gates" "$CIBLE/skills" || exit 1

# --- 1. QUELS GARDES SONT PROUVES ? -----------------------------------------
# Chaque garde n'entre que si son test passe. Le test tourne ici, chez vous,
# sur votre machine — pas sur la mienne.
echo
echo "Les tests, avant de poser quoi que ce soit :"
for g in "$SOURCE"/gates/*.py "$SOURCE"/gates/*.sh; do
  [ -f "$g" ] || continue
  nom="$(basename "$g")"
  case "$nom" in *.avant-*) continue;; esac
  base="${nom%.*}"
  t=""
  for essai in "$SOURCE/tests/test-$base.sh" "$SOURCE/tests/test-${base#garde-}.sh" \
               "$SOURCE/tests/test-$base.py"; do
    [ -f "$essai" ] && { t="$essai"; break; }
  done
  if [ -z "$t" ]; then
    ecartes="$ecartes\n  $nom — aucun test : un garde sans preuve ne s'installe pas"
    continue
  fi
  if GATES_HOME="$SOURCE" bash "$t" >/dev/null 2>&1 || \
     GATES_HOME="$SOURCE" python3 "$t" >/dev/null 2>&1; then
    cp "$g" "$CIBLE/gates/$nom"; chmod +x "$CIBLE/gates/$nom"
    vert=$((vert+1)); echo "  VERT  $nom"
  else
    ecartes="$ecartes\n  $nom — son test est rouge : il reste dehors"
  fi
done

# les regles a vous, et les competences : elles ne refusent rien, elles guident
[ -f "$SOURCE/gates/regles.json" ] && cp -n "$SOURCE/gates/regles.json" "$CIBLE/gates/" 2>/dev/null
cp -n "$SOURCE"/skills/*.md "$CIBLE/skills/" 2>/dev/null

# --- 2. LE BRANCHEMENT, SANS PIETINER CE QUI EXISTE -------------------------
python3 - "$CIBLE" "$SOURCE/gates/branchements.json" <<'PY'
import json, os, sys
cible, carte = sys.argv[1], sys.argv[2]
reg = os.path.join(cible, "settings.json")
d = {}
if os.path.exists(reg):
    try: d = json.load(open(reg, encoding="utf-8"))
    except Exception:
        os.replace(reg, reg + ".illisible")   # on garde l'ancien, on ne jette rien
        d = {}
plan = json.load(open(carte, encoding="utf-8"))["branchements"]
hooks = d.setdefault("hooks", {})
pose = 0
for fichier, ou in plan.items():
    chemin = os.path.join(cible, "gates", fichier)
    if not os.path.exists(chemin):        # ecarte par les tests : on ne branche pas
        continue
    cmd = ("bash " if fichier.endswith(".sh") else "python3 ") + chemin
    lst = hooks.setdefault(ou["evenement"], [])
    if any(fichier in h.get("command", "") for e in lst for h in e.get("hooks", [])):
        continue                          # deja branche : on n'ajoute pas deux fois
    e = {"hooks": [{"type": "command", "command": cmd}]}
    if ou["outils"]: e["matcher"] = ou["outils"]
    lst.append(e); pose += 1
json.dump(d, open(reg, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"\n  {pose} garde(s) branche(s) dans {reg}")
print("  vos reglages a vous n'ont pas ete touches")
PY

# --- 3. LA PREUVE, TOUT DE SUITE --------------------------------------------
echo
echo "La preuve, maintenant : on essaie de faire passer une cle en clair."
FAUX="ghp_$(printf 'A%.0s' {1..30})"
if [ -f "$CIBLE/gates/porte-secrets.py" ]; then
  echo "{\"tool_input\":{\"command\":\"git push https://x:$FAUX@github.com/a/b\"}}" \
    | python3 "$CIBLE/gates/porte-secrets.py" >/dev/null 2>&1
  [ $? -eq 2 ] && echo "  REFUSE — le garde marche." \
                || { echo "  ARRET : le garde n'a pas refuse."; exit 1; }
else
  echo "  (la porte a secrets n'a pas passe ses tests, rien a prouver ici)"
fi

echo
echo "$vert garde(s) installe(s)."
[ -n "$ecartes" ] && { echo "Ecartes, et pourquoi :"; printf "$ecartes\n"; }
echo
echo "Vos regles a vous : $CIBLE/gates/regles.json"
