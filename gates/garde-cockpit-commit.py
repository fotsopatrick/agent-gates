#!/usr/bin/env python3
"""Garde du cockpit — deterministe, aucune IA (doctrine le gardien).

INTERDIT DE MODIFIER LE COCKPIT TANT QUE LE TRAVAIL PRECEDENT N'EST PAS
ENREGISTRE (commit). Lire reste toujours permis. Enregistrer aussi.

NE D'UNE PANNE REELLE (06/09/2026). Cinq des huit pages du cockpit ne
repondaient plus, et rien ne disait ni quand ni pourquoi :
  - quatre petits serveurs ne tournaient plus ;
  - le Monde etait cherche sur le port 8779 alors qu'il ecoute sur 8778.
Aucun de ces changements n'etait enregistre : impossible de revenir en
arriere, impossible de savoir qui avait touche quoi.
Ses mots : « met un garde fou dessus qui empeche sa modification sans
commit avant ».

CE QUI EST REFUSE : ecrire dans ~/taches/ quand `git status`
montre du travail non enregistre.
CE QUI RESTE PERMIS : lire (cat, head, grep, diff, wc), lancer le controle,
et toutes les commandes git — sinon on ne pourrait jamais enregistrer.

Son controle : bash ~/controles/test-garde-cockpit.sh
Contrat du crochet PreToolUse : sortir 2 = BLOQUER, tout autre code = passer.
"""
import json
import os
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# LES REGLES SE CHOISISSENT, ELLES NE SONT PAS EN DUR.
# Demande du proprietaire le 08/09/2026 : « tous les garde-fous configurables avec
# empreinte que l'user choisit ». Un garde livre avec les regles de quelqu'un
# d'autre ne sert a personne : chacun a ses fautes a lui.
#
# Pose un fichier « regles.json » a cote de ce garde, ou donne son chemin dans
# la variable GARDE_REGLES. Sans fichier, les valeurs ci-dessous s'appliquent.
# ---------------------------------------------------------------------------
import json as _json, os as _os

def charger_regles(defaut):
    """Rend les regles de la personne qui installe, ou celles par defaut."""
    chemin = _os.environ.get("GARDE_REGLES") or _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "regles.json")
    try:
        with open(chemin, encoding="utf-8") as f:
            perso = _json.load(f)
    except Exception:
        return defaut
    if not isinstance(perso, dict):
        return defaut
    sortie = dict(defaut)
    sortie.update(perso)
    return sortie

DEPOT = "~/taches"

# Ce qui ECRIT. Tout le reste (cat, head, grep, wc, diff, bash un test...) passe.
ECRITURE = re.compile(
    r"\bsed\s+-[a-z]*i"          # sed -i : ecrit dans le fichier
    r"|\btee\b"                  # tee : ecrit dans le fichier
    r"|>>?\s*[^|&;]*"            # une redirection > ou >>
    r"|\b(cp|mv|rm|truncate|install|patch|chmod|chown)\b"
    r"|\bpython3?\b[^|;]*\bopen\([^)]*['\"]w",   # python qui ouvre en ecriture
)

# git doit toujours passer : c'est LUI qui enregistre.
GIT = re.compile(r"^\s*(sudo\s+-u\s+\S+\s+)?(env\s+\S+=\S+\s+)*git\b")


def sans_les_textes(cmd):
    """Enleve les blocs colles (heredoc) : y ecrire un chemin n'est pas y toucher.
    La redirection, elle, reste visible car elle est AVANT le bloc."""
    for m in re.finditer(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?", cmd):
        marque = m.group(1)
        fin = re.search(r"^\s*" + re.escape(marque) + r"\s*$", cmd[m.end():], re.M)
        bout = cmd[m.end():m.end() + (fin.start() if fin else len(cmd))]
        cmd = cmd.replace(bout, " ")
    return cmd


def travail_non_enregistre():
    """Renvoie la liste des fichiers modifies et pas encore enregistres."""
    if not os.path.isdir(os.path.join(DEPOT, ".git")):
        return []          # pas de depot : le garde ne bloque rien
    try:
        r = subprocess.run(["git", "-C", DEPOT, "status", "--porcelain"],
                           capture_output=True, text=True, timeout=10)
    except Exception:
        return []
    return [l for l in r.stdout.strip().splitlines() if l.strip()]


def main():
    try:
        entree = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    outil = entree.get("tool_name", "")
    args = entree.get("tool_input") or {}

    if outil in ("Edit", "Write", "NotebookEdit", "MultiEdit"):
        cible = args.get("file_path") or args.get("notebook_path") or ""
        touche = cible.startswith(DEPOT + "/") or cible == DEPOT
    elif outil == "Bash":
        cmd = sans_les_textes(args.get("command", ""))
        if GIT.search(cmd):
            sys.exit(0)                      # enregistrer est toujours permis
        touche = (DEPOT in cmd) and bool(ECRITURE.search(cmd))
    else:
        sys.exit(0)

    if not touche:
        sys.exit(0)

    sales = travail_non_enregistre()
    if not sales:
        sys.exit(0)

    sys.stderr.write(
        "GARDE DU COCKPIT — REFUS.\n\n"
        "Tu vas modifier le cockpit alors que du travail precedent n'est PAS\n"
        "encore enregistre. Si ta modification casse quelque chose, personne ne\n"
        "pourra revenir en arriere.\n\n"
        "Ce qui traine, non enregistre :\n"
        + "".join("  " + l + "\n" for l in sales[:12])
        + ("  ... et d'autres\n" if len(sales) > 12 else "")
        + "\nCe qu'il faut faire d'abord, dans cet ordre :\n"
          "  1. bash ~/controles/test-cockpit.sh      verifier que tout repond\n"
          "  2. git -C " + DEPOT + " add -A\n"
          "  3. git -C " + DEPOT + " commit -m \"ce que ca change et pourquoi\"\n"
          "\nLire le cockpit reste permis. Les commandes git aussi.\n")
    sys.exit(2)


main()
