#!/usr/bin/env python3
"""LE GARDE BERZERK (Stop hook) — en mode berzerk, je n'ai plus le droit de
rendre une action a la personne.

NE D'UNE COLERE REELLE (06/09/2026). Ses mots : « me demande plus jamais de
faire une action ca me saoule », « surtout quand je dis berzek », « cree un
garde fou qui t'empeche de me demander des choses quand j'ai dit bersek ».

Dans la meme soiree je lui avais rendu QUATRE choses a faire : taper une
commande pour le code de publication, taper une commande pour les
permissions, cliquer sur une page OVH, cocher une case dans la tour.
Chacune etait une interruption. En berzerk, il n'en veut aucune.

CE QUI EST REFUSE quand le mode est allume :
  - un verbe d'ordre adresse a lui (tape, clique, coche, valide, ouvre,
    lance, ajoute, colle, remplace, mets, va dans...) ;
  - une demande deguisee (dis-moi, donne-moi, peux-tu, il faut que tu,
    j'ai besoin que tu, tu dois) ;
  - un bloc de commande presente comme etant a coller par lui.

CE QUI RESTE PERMIS :
  - dire ce que J'AI fait, avec ses preuves ;
  - NOMMER un mur qui m'a bloque, une fois, sans lui demander de l'ouvrir ;
  - citer une commande que j'ai lancee moi-meme ;
  - une question de choix quand deux routes changent vraiment le travail —
    mais pas une corvee a executer.

Contrat du crochet Stop : sortie 2 = BLOQUER la fin du tour et forcer la
reecriture. Tout autre code = laisser passer.
"""
import json
import os
import re
import sys
import unicodedata

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
DRAPEAU = os.path.join(MAISON, ".claude/portes/.berzerk-actif")

# Les ordres donnes a la personne. On exige le verbe EN DEBUT de phrase ou apres
# « tu » : « je clique » ne doit pas etre pris pour « clique ».
ORDRES = re.compile(
    r"(?:^|[.!?:\n]\s*|\*\*)\s*"
    r"(tape|tapes|clique|cliques|coche|coches|valide|valides|ouvre|ouvres|"
    r"colle|colles|remplace|remplaces|ajoute|ajoutes|mets|met|va\s+dans|"
    r"connecte-toi|rends-toi|selectionne|choisis|pose|poses|lance|lances|"
    r"exec[uy]te|saisis|entre|inscris|verifie|verifies)\b",
    re.I | re.M)

DEMANDES = re.compile(
    r"\b(dis-moi|dis\s+moi|donne-moi|donne\s+moi|peux-tu|pourrais-tu|"
    r"il\s+faut\s+que\s+tu|j'ai\s+besoin\s+que\s+tu|tu\s+dois\s+|"
    r"a\s+toi\s+de\s+|c'est\s+a\s+toi\s+de\s+|de\s+ta\s+main|"
    r"ta\s+main\s+est\s+|attend\s+ton\s+clic|attend\s+ta\s+validation)",
    re.I)

# Un bloc de commande annonce comme etant pour lui.
BLOC_POUR_LUI = re.compile(
    r"(la\s+commande\s+a\s+taper|commande\s+a\s+coller|a\s+taper\s+toi-meme|"
    r"tape\s+ces?\s+commandes?|voici\s+la\s+commande|une\s+seule\s+commande)",
    re.I)

# Ce qui INNOCENTE une phrase : je parle de ce que MOI j'ai fait.
JE_LAI_FAIT = re.compile(r"\b(j'ai|je\s+viens\s+de|j'ai\s+lance|je\s+lance|"
                         r"je\s+l'ai|j'avais|je\s+n'ai\s+pas)\b", re.I)


def sans_accent(t):
    return "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn")


def dernier_message(chemin):
    txt = ""
    try:
        for ligne in open(chemin, encoding="utf-8", errors="replace"):
            try:
                d = json.loads(ligne)
            except Exception:
                continue
            if d.get("type") != "assistant":
                continue
            c = (d.get("message") or {}).get("content")
            if isinstance(c, list):
                t = " ".join(x.get("text", "") for x in c
                             if isinstance(x, dict) and x.get("type") == "text")
            else:
                t = str(c or "")
            if t.strip():
                txt = t
    except Exception:
        return ""
    return txt


def fautes(texte):
    """Rend la liste des demandes trouvees. Vide = le message est propre."""
    trouvees = []
    nu = sans_accent(texte)

    # on juge phrase par phrase : une phrase ou je raconte ce que J'AI fait
    # ne peut pas etre un ordre.
    for phrase in re.split(r"(?<=[.!?\n])\s+", nu):
        if not phrase.strip():
            continue
        if JE_LAI_FAIT.search(phrase):
            continue
        m = ORDRES.search(phrase)
        if m:
            trouvees.append("ordre « %s » dans : %s" % (m.group(1), phrase.strip()[:70]))
            continue
        m = DEMANDES.search(phrase)
        if m:
            trouvees.append("demande « %s » dans : %s" % (m.group(1).strip(), phrase.strip()[:70]))

    m = BLOC_POUR_LUI.search(nu)
    if m:
        trouvees.append("bloc de commande annonce pour lui : « %s »" % m.group(1))
    return trouvees


def main():
    if not os.path.exists(DRAPEAU):
        sys.exit(0)                     # mode eteint : rien a garder

    try:
        hook = json.loads(sys.stdin.read() or "{}")
    except Exception:
        sys.exit(0)
    chemin = hook.get("transcript_path") or ""
    if not chemin or not os.path.exists(chemin):
        sys.exit(0)

    texte = dernier_message(chemin)
    if not texte.strip():
        sys.exit(0)

    trouvees = fautes(texte)
    if not trouvees:
        sys.exit(0)

    sys.stderr.write(
        "GARDE BERZERK — ton message ne passe pas.\n\n"
        "la personne a dit « berzerk ». Il ne veut AUCUNE action a faire.\n"
        "Ce que tu lui demandes :\n"
        + "".join("  - " + t + "\n" for t in trouvees[:6])
        + ("  ... et d'autres\n" if len(trouvees) > 6 else "")
        + "\nCe que tu fais a la place :\n"
          "  1. tu le FAIS toi-meme — cherche une autre route avant d'abandonner ;\n"
          "  2. si un mur mecanique bloque, tu le NOMMES en une ligne, tu dis ce\n"
          "     qu'il protege, et tu CONTINUES sur tout le reste ;\n"
          "  3. tu ne lui rends jamais une commande a taper ni un bouton a cliquer.\n"
          "\nReecris ton message : uniquement ce que tu as fait, ce que tu as\n"
          "mesure, et la prochaine chose que TU vas faire.\n")
    sys.exit(2)


main()
