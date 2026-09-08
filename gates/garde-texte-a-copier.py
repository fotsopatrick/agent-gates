#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GARDE « LE TEXTE A COPIER SE DONNE NU ».

Ne d'une faute reelle (07/09/2026). J'avais ecrit a la personne un message a
envoyer sur LinkedIn, et je l'avais mis dans une citation : chaque ligne
commencait par un chevron « > », et il y avait des etoiles autour des mots
importants. Quand il copie ce bloc, les chevrons et les etoiles partent avec.
Il a tranche : « enleve le markdown, la fleche a gauche, et fait toi un garde
pour ca ».

« markdown » = les petits symboles qui font la mise en forme dans un
terminal : ** pour le gras, ` pour le code, > pour la citation. A l'ecran
c'est joli. Dans un presse-papier, c'est de la salete.

Donc : des que ma reponse dit « voici le texte, copie-le », le texte doit
etre dans un bloc de code (trois accents graves), qui se copie tel quel.
Jamais dans une citation, jamais avec des etoiles dedans.

Contrat du crochet Stop : sortie 0 = je laisse finir, sortie 2 = je refuse
et le motif part sur la sortie d'erreur.
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

# « voici le texte, tu n'as qu'a le copier », dans toutes ses formes
INTENTION = re.compile(
    r"(copie[rz]?\b|copie-le|copier-coller|\bcolle[rz]?\b|"
    r"(?:a|à) coller|tu n'as qu'(?:a|à)|prêt (?:a|à) coller|"
    r"pret (?:a|à) coller|texte (?:exact )?(?:a|à) (?:copier|coller))", re.I)


def texte_de_la_reponse(donnees):
    """Rend le dernier message que l'assistant vient d'ecrire."""
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


def hors_bloc_de_code(texte):
    """Les lignes qui ne sont PAS dans un bloc de code.

    Un bloc de code se copie proprement : on ne le juge pas. On ne regarde
    que ce qui est dehors.
    """
    dedans = False
    for ligne in texte.split("\n"):
        if ligne.strip().startswith("```"):
            dedans = not dedans
            continue
        if not dedans:
            yield ligne


def main():
    try:
        donnees = json.load(sys.stdin)
    except Exception:
        return 0

    texte = texte_de_la_reponse(donnees)
    if not texte or not INTENTION.search(texte):
        return 0

    citations = [l for l in hors_bloc_de_code(texte)
                 if l.lstrip().startswith(">")]
    if not citations:
        return 0

    sale = [l for l in citations if "**" in l or "`" in l or "__" in l]

    print(
        "GARDE « LE TEXTE A COPIER SE DONNE NU » — refuse.\n\n"
        "Tu annonces un texte a copier, et tu l'as mis dans une citation :\n"
        + "\n".join("  " + l[:70] for l in citations[:3]) + "\n\n"
        "Chaque ligne commence par un chevron « > ». Quand la personne copie ce\n"
        "bloc, les chevrons partent avec, et il doit les enlever a la main."
        + ("\nPire : il y a des etoiles ou des accents graves DEDANS, qui\n"
           "partiront aussi.\n" if sale else "\n")
        + "\nRefais-le : mets le texte dans un bloc de code, c'est-a-dire\n"
        "entre deux lignes de trois accents graves. Un bloc de code se copie\n"
        "tel quel, sans un symbole en trop. Et dedans, pas d'etoiles, pas\n"
        "d'accents graves : du texte nu, exactement ce qu'il va envoyer.",
        file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
