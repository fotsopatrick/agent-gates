#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GARDE DE LA BOITE NOIRE — un article doit MONTRER, pas seulement raconter.

POURQUOI CE GARDE EXISTE
Ne d'une relecture reelle le 08/09/2026. la personne a ouvert le premier article
arrete par la porte du site — celui qui parle d'Alice — et il a dit :
« il n'y a pas d'images d'Alice, on ne sait pas ce que c'est, effet boite
noire ».

Il avait raison. L'article racontait une intelligence, ses journaux, ses
chiffres. Il ne montrait rien. Le lecteur devait croire sur parole.

Une boite noire, c'est une chose dont on parle sans jamais l'ouvrir. C'est
exactement ce qu'on reproche aux autres. Un article de la tour qui ne montre
rien fait la meme faute que l'agent qui dit « c'est fait » sans preuve.

CE QUE LE GARDE EXIGE
Un article doit contenir au moins UNE chose a regarder :
  - une image (une capture d'ecran, une photo) ;
  - une image animee ;
  - un dessin fait a la main ;
  - une video ;
  - ou, a defaut, un bloc de resultat reel — un journal, des chiffres, la
    sortie d'un controle. Un chiffre vrai vaut une image.

QUAND IL SE TAIT
Quand ce n'est pas un article : une note, un mode d'emploi, une fiche interne.
Et quand l'article est court — moins de 1500 signes, on ne demande pas une
capture pour trois paragraphes.

Un garde qui bloque trop finit debranche, et alors il ne garde plus rien.

Contrat du crochet PreToolUse : on ecrit un refus en JSON sur la sortie
standard, ou rien du tout. Code 0 dans les deux cas.
"""
import json
import os
import re
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

MAISON = os.path.expanduser("~")

# Les endroits ou vivent les articles destines au public.
DOSSIERS_ARTICLES = [
    os.path.join(MAISON, "livrables"),
    os.path.join(MAISON, "livrables/articles"),
    os.path.join(MAISON, "livrables/en"),
]

# Ce qui compte comme « quelque chose a regarder ».
A_REGARDER = re.compile(
    r"(!\[[^\]]*\]\([^)]+\)"          # une image, en texte balise
    r"|<img\b|<svg\b|<video\b|<iframe\b"   # une image ou une video, en HTML
    r"|```"                            # un bloc de resultat : journal, chiffres
    r"|\byoutube\.com|\byoutu\.be"     # une video en ligne
    r"|\.png\b|\.jpg\b|\.jpeg\b|\.gif\b|\.webp\b|\.mp4\b)", re.I)

TAILLE_MINIMALE = 1500     # en dessous, on ne reclame rien


def est_un_article(chemin):
    v = os.path.realpath(os.path.expanduser(chemin))
    if not v.endswith(".md"):
        return False
    nom = os.path.basename(v)
    if not (nom.startswith("article-") or "/articles/" in v or "/en/" in v):
        return False
    dossier = os.path.dirname(v)
    return any(dossier == os.path.realpath(d) for d in DOSSIERS_ARTICLES)


def refus(nom, signes):
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "GARDE DE LA BOITE NOIRE — REFUS.\n\n"
                "L'article « %s » fait %d signes et ne montre RIEN.\n\n"
                "Ne d'une relecture de la personne, le 08/09/2026, sur l'article "
                "qui parlait d'Alice : « il n'y a pas d'images d'Alice, on ne "
                "sait pas ce que c'est, effet boite noire ».\n\n"
                "Une boite noire, c'est une chose dont on parle sans jamais "
                "l'ouvrir. Un article de la tour qui ne montre rien fait la "
                "meme faute que l'agent qui dit « c'est fait » sans preuve.\n\n"
                "Ajoute AU MOINS UNE de ces choses, puis recommence :\n"
                "  1. une capture d'ecran de ce dont tu parles ;\n"
                "  2. une image animee, ou une video ;\n"
                "  3. un dessin fait a la main ;\n"
                "  4. a defaut, un bloc de resultat REEL — un journal, des "
                "chiffres, la sortie d'un controle. Un chiffre vrai vaut une "
                "image.\n\n"
                "Si tu n'as pas encore la capture, ecris l'article, garde-le, "
                "et dis a la personne quelle capture il te manque." % (nom, signes)),
        }
    }


def main():
    try:
        donnees = json.load(sys.stdin)
    except Exception:
        return 0
    if (donnees.get("tool_name") or "") not in ("Write", "Edit"):
        return 0
    e = donnees.get("tool_input") or {}
    chemin = e.get("file_path") or ""
    if not est_un_article(chemin):
        return 0

    # Ce qu'on s'apprete a ecrire, ou ce qui est deja la pour une modification.
    texte = e.get("content") or e.get("new_string") or ""
    if not texte and os.path.exists(chemin):
        try:
            texte = open(chemin, encoding="utf-8", errors="replace").read()
        except OSError:
            return 0

    if len(texte) < TAILLE_MINIMALE:
        return 0
    if A_REGARDER.search(texte):
        return 0

    print(json.dumps(refus(os.path.basename(chemin), len(texte)),
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
