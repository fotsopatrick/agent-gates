# -*- coding: utf-8 -*-
"""LE GARDE DE LA PAGE MONTRÉE.

Il empêche une faute précise, qui revient : fabriquer une page pour la personne,
puis la lui RECOPIER en texte au lieu de la lui OUVRIR sous les yeux.

La cause, sans nom propre : je choisis la forme de ma réponse d'après ce que
j'ai fabriqué (du texte), au lieu de ce que la chose EST pour celui qui la
reçoit (une page). Une page se regarde. Elle ne se recopie pas.

Comment il marche : le harnais appelle ce garde chaque fois qu'un fichier est
écrit. Si le fichier est une page (.html) posée dans les livrables, le garde
répond une consigne qui remonte dans la conversation. Ce n'est pas un conseil
rangé quelque part : ça arrive au moment exact où la faute allait se produire.

Il lit ce que le harnais lui donne sur son entrée, au format JSON (une façon
d'écrire des données que les programmes se passent entre eux).
"""
import json
import os
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

DOSSIERS_LIVRABLES = ("~/livrables",)


def chemin_ecrit(donnees):
    """Retrouve le fichier que l'outil vient d'écrire."""
    import re
    entree = donnees.get("tool_input") or {}
    for cle in ("file_path", "path", "filePath", "notebook_path"):
        if entree.get(cle):
            return str(entree[cle])
    # une commande du terminal cache le chemin dans son texte
    commande = str(entree.get("command") or "")
    trouves = re.findall(r"[\w./~-]*/livrables/[\w./~-]+\.html?\b", commande)
    return trouves[-1] if trouves else ""


def main():
    try:
        donnees = json.load(sys.stdin)
    except Exception:
        return 0

    chemin = chemin_ecrit(donnees)
    if not chemin.lower().endswith((".html", ".htm")):
        return 0
    reel = os.path.realpath(chemin)
    if not any(reel.startswith(os.path.realpath(d)) for d in DOSSIERS_LIVRABLES):
        return 0

    nom = os.path.basename(chemin)
    print(
        "GARDE DE LA PAGE MONTREE — « %s » est une PAGE, pas un texte.\n"
        "\n"
        "  A FAIRE MAINTENANT, dans cet ordre :\n"
        "    1. l'ouvrir a l'ecran de la personne :\n"
        "         setsid xdg-open %s >/dev/null 2>&1 &\n"
        "       (setsid = la laisse ouverte meme quand la commande finit)\n"
        "    2. en donner une image si l'oeil est ouvert :\n"
        "         python3 ~/controles/oeil.py dispo\n"
        "       si l'oeil est ferme, le DIRE, ne pas faire semblant d'avoir vu.\n"
        "    3. la nommer par sa fleche de Mes travaux, apres l'avoir montree.\n"
        "\n"
        "  INTERDIT : recopier le contenu de la page dans la reponse.\n"
        "  Une page se regarde. La recopier ne dit ni si c'est beau,\n"
        "  ni si c'est casse."
        % (nom, chemin),
        file=sys.stderr)
    return 2   # 2 = le harnais fait remonter ce message dans la conversation


if __name__ == "__main__":
    sys.exit(main())
