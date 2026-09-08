#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GARDE DES TESTS — on ne dit pas « c'est fait » sans avoir teste.

NE D'UNE FAUTE REELLE (07/09/2026). J'avais fabrique une page entiere, je
l'avais verifiee a l'oeil, et je l'avais livree. Un bloc de programme
n'etait pas referme : toute l'interactivite etait morte. la personne, sans
detour : « pourquoi tu n'as pas ecris les test ???? ».

Un oeil se trompe. Un test ne se trompe pas deux fois.

Ce garde tombe a la fin du tour. Il regarde deux choses dans ma reponse :
  1. est-ce que j'ANNONCE quelque chose de fait, pose, repare, livre ?
  2. est-ce que je MONTRE une preuve de test dans le meme message ?
Si la premiere est vraie et la seconde fausse, il refuse.

Il se tait quand la reponse ne promet rien (une question, un constat), et
quand le geste appartient a la personne (sa main, un bouton, un mot de passe) :
on n'exige pas la preuve de ce qu'on n'a pas fait.

Contrat du crochet Stop : 0 = laisse finir, 2 = refuse, motif sur stderr.
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

ANNONCE = re.compile(
    r"\b(c[’' ]est (fait|pose|posee|pret|prete|repare|reparee|corrige|corrigee|"
    r"en place|en ligne|branche|branchee)|"
    r"j[’' ]ai (ecrit|pose|fabrique|construit|repare|corrige|branche|livre|"
    r"ajoute|termine|mis en place)|"
    r"je (l[’' ]|la |les )?ai (pose|posee|repare|reparee|corrige|branche|livre)|"
    r"(est|sont) (maintenant )?(pose|posee|posees|poses|repare|reparee|"
    r"branche|branchee|livre|livree|en place|en ligne|pret|prete)|"
    r"\bfonctionne\b|\bca marche\b|\bmarche maintenant\b)", re.I)

PREUVE = re.compile(
    r"(\d+\s*vert|vert\s*/\s*\d|0\s*rouge|\d+\s*rouge|banc d'essai|"
    r"RESULTAT\s*:|tout vert|passe au vert|repasse au vert|"
    r"\bPASS\b|exit code|code de sortie|code renvoye|"
    r"test (passe|repasse|vert|rouge|dit)|tests? (verts?|rouges?)|"
    r"\d+\s*/\s*\d+\s*(controles|verifications|tests|verts))", re.I)

SA_MAIN = re.compile(
    r"(ta main|sa main|ton geste|c'est a toi|la decision est a toi|"
    r"mon harnais|refuse par (mon|le) (harnais|garde)|"
    r"je ne peux pas le lancer moi-?meme|"
    r"\bbouton\b|\bclique\b|mot de passe|\bjeton\b)", re.I)


def texte_de_la_reponse(donnees):
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
    if not ANNONCE.search(texte):
        return 0
    if PREUVE.search(texte):
        return 0
    if SA_MAIN.search(texte):
        return 0
    print(
        "GARDE DES TESTS — refuse.\n\n"
        "Tu annonces quelque chose de fait, sans aucune preuve de test dans\n"
        "le meme message. Un oeil se trompe ; un test ne se trompe pas deux\n"
        "fois. Le 07/09/2026 j'ai livre une page dont tout le programme etait\n"
        "mort, parce que je l'avais verifiee a l'oeil.\n\n"
        "Trois sorties, une seule est interdite :\n"
        "  1. Lance le test et COLLE son resultat : combien de vert, combien\n"
        "     de rouge. Le chiffre, pas le sentiment.\n"
        "  2. Si aucun test n'existe, ECRIS-LE, vois-le rouge, repare.\n"
        "  3. Si le geste appartient a la personne, dis-le explicitement.\n"
        "Reecris ta reponse.",
        file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
