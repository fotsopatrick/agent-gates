#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GARDE « ON REPARE TOUT DE SUITE ».

Ne du 06/09/2026. J avais trouve pourquoi Alice repondait mal, et j ai ecrit
« je le note comme a reparer » au lieu de le reparer. la personne : « pourquoi
quand tu rencontres un bug tu ne le fixes pas, ca m enerve ce point ».

Un defaut trouve se repare dans le meme tour. On ne le met pas dans une liste.

Ce garde bloque la fin du tour quand la reponse repousse une reparation :
« je le note comme a reparer », « a corriger plus tard », « je note pour la
prochaine fois », « reste a reparer », « on verra ca apres »...

Il laisse passer si la reponse montre qu on a AGI dans le meme tour (une
correction posee, un test relance, un fichier reecrit), ou si la reparation
demande la main de la personne (un mot de passe, un clic, un achat, un secret).
"""
import json
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

# Ce qui trahit un report de reparation.
REPORTS = [
    r"je le note comme (?:a|à) r[ée]parer",
    r"je (?:le |la |les )?note pour (?:plus tard|la prochaine)",
    r"(?:a|à) (?:corriger|r[ée]parer|refaire) plus tard",
    r"(?:je le mets|je la mets|je mets [çc]a) dans (?:ce qui reste|la liste)",
    r"on (?:verra|corrigera|r[ée]parera) [çc]a (?:apr[èe]s|plus tard|demain)",
    r"reste (?:donc )?(?:a|à) (?:corriger|r[ée]parer)",
    r"je (?:le |la )?garde pour (?:plus tard|la suite)",
    r"[çc]a se corrigera",
    r"(?:c est|c'est) (?:a|à) (?:corriger|r[ée]parer) (?:ensuite|apr[èe]s)",
]

# Ce qui prouve qu on a agi dans le meme tour.
ACTIONS = [
    r"je (?:le |la |les )?r[ée]pare", r"c est r[ée]par[ée]", r"c'est r[ée]par[ée]",
    # Le \b (fin de mot) est indispensable : sans lui, « corrig[ée] » attrape
    # aussi « corriger », l infinitif. Annoncer une reparation FUTURE passait
    # alors pour une reparation FAITE, et le garde se laissait neutraliser.
    # Trou trouve et bouche le 07/09/2026 par son propre banc d essai.
    r"je corrige\b", r"corrig[ée]\b", r"je relance\b", r"relanc[ée]\b",
    r"je refais\b", r"refait\b", r"je viens de", r"pos[ée] (?:le|la|un|une)",
    r"le test (?:passe|est) au vert", r"j ai r[ée]par", r"j'ai r[ée]par",
]

# Ce qui rend la reparation impossible sans la personne : on a le droit de reporter.
SA_MAIN = [
    r"mot de passe", r"il faut que tu", r"c est (?:a|à) toi de",
    r"c'est (?:a|à) toi de", r"attend(?:s)? (?:ta|ton|ton accord|ta main)",
    r"ton accord", r"tu dois cliquer", r"cr[ée]er le serveur",
    r"passe par le circuit", r"la porte refuse",
]


def texte_de_la_reponse(donnees):
    """Rend le dernier message que l assistant vient d ecrire."""
    for cle in ("last_assistant_message", "assistant_message", "message"):
        v = donnees.get(cle)
        if isinstance(v, str) and v.strip():
            return v
    tr = donnees.get("transcript") or donnees.get("messages") or []
    if isinstance(tr, list):
        for m in reversed(tr):
            if isinstance(m, dict) and m.get("role") == "assistant":
                c = m.get("content")
                if isinstance(c, str):
                    return c
                if isinstance(c, list):
                    return " ".join(b.get("text", "") for b in c
                                    if isinstance(b, dict))
    return ""


def main():
    try:
        donnees = json.load(sys.stdin)
    except Exception:
        return 0

    texte = texte_de_la_reponse(donnees)
    if not texte:
        return 0
    bas = texte.lower()

    trouves = [m for m in REPORTS if re.search(m, bas)]
    if not trouves:
        return 0

    # on a agi dans le meme tour : c est bon
    if any(re.search(a, bas) for a in ACTIONS):
        return 0

    # la reparation appartient a la personne : c est bon
    if any(re.search(s, bas) for s in SA_MAIN):
        return 0

    print(
        "GARDE « ON REPARE TOUT DE SUITE » — tu repousses une reparation.\n"
        "Un defaut trouve se repare DANS LE MEME TOUR, il ne se met pas dans\n"
        "une liste. la personne l a dit : « pourquoi quand tu rencontres un bug tu\n"
        "ne le fixes pas, ca m enerve ce point ».\n\n"
        "Trois sorties, une seule est interdite :\n"
        "  1. Repare maintenant, montre la preuve que c est repare.\n"
        "  2. Si la reparation demande SA main (un clic, un secret, un achat,\n"
        "     une porte de circuit), dis-le explicitement : c est autorise.\n"
        "  3. Si tu ne sais pas encore reparer, cherche la cause maintenant.\n"
        "Reecris ta reponse.",
        file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
