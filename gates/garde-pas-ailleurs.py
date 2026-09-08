#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GARDE « NE M'ENVOIE PAS AILLEURS » — le texte se lit ICI.

NE D'UNE COLERE REELLE (07/09/2026). J'avais mis les champs corriges d'un
formulaire dans un fichier sur son bureau, avec un bouton pour l'ouvrir.
la personne : « non mais dans un fichier je vais rien lire tu met ici », puis
« tu m'enerve a m'envoyer ailleurs pour rien, cree un garde fou qui t'evite
de faire ca ».

LA REGLE : un texte que j'ai ecrit se LIT dans ma reponse. Le fichier sert a
le garder, pas a l'aller chercher. Le nom du fichier vient APRES le contenu,
jamais a la place.

CE GARDE REFUSE une reponse qui l'envoie ouvrir ou lire quelque chose SANS
montrer le contenu dans le message. Il laisse passer :
  - une reponse qui montre le texte (un bloc de code, ou une image) ET nomme
    le fichier ensuite ;
  - un BOUTON pour une ACTION (lancer, publier, deployer) : ca, c'est sa
    regle a lui, et une action ne se lit pas ;
  - le mot de passe, s'il est pose.

Contrat du crochet Stop : 0 = laisse finir, 2 = refuse, motif sur stderr.
"""
import hashlib
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
EMPREINTE = os.environ.get("AILLEURS_EMPREINTE") or os.path.join(
    MAISON, ".claude/portes/.ailleurs-empreinte")

# --- je l'envoie ailleurs pour LIRE -------------------------------------
AILLEURS = re.compile(
    r"(ouvre[- ](le|la|les)\b|ouvre le (fichier|document|texte|bloc)|"
    r"va (le |la |les )?(lire|voir|chercher)|tu (le |la )?trouveras dans|"
    r"(c est|c'est|il est|ils sont|elle est) (dans|sur) (le fichier|ton bureau)|"
    # « le fichier de … » etait trop large : il attrapait « le fichier de dons
    # du hackathon », qui ne renvoie personne nulle part. Un garde qui refuse
    # ce qu il n a pas compris ne garde rien. On exige maintenant une
    # intention de LECTURE juste a cote.
    r"dans un fichier|"
    r"(?:le fichier|le document)[^.]{0,30}(?:a lire|se lit|contient le texte|"
    r"est sur ton bureau|est dans)|"
    r"j[’' ]ai (mis|ecrit|range) (le |la |les |ca |cela )?(texte|champs|contenu|"
    r"reponses|lettre)[^.]{0,40}(dans|sur)|"
    r"lis[- ]le\b|a lire dans|le detail est dans|tout est dans)", re.I)

# --- je MONTRE le contenu ------------------------------------------------
def montre(texte):
    if texte.count("```") >= 2:
        return True                       # un bloc de code : le texte est la
    if re.search(r"!\[[^\]]*\]\([^)]+\)", texte):
        return True                       # une image montree
    if re.search(r"^\s*>", texte, re.M):
        return True                       # une citation du contenu
    return False

# --- un BOUTON pour une ACTION : autorise, c'est sa regle ---------------
ACTION = re.compile(
    r"\bbouton\b[^.]{0,80}\b(lance|lancer|publie|publier|deploie|deployer|"
    r"met(tre)? en ligne|relance|demarre|envoie|revoque)", re.I)


def empreinte_posee():
    try:
        v = open(EMPREINTE, encoding="utf-8").read().strip().lower()
        return v if len(v) == 64 else None
    except OSError:
        return None


def mot_de_passe_donne(brut, attendue):
    mots = [m.strip(".,;:!?()[]\"'«»") for m in brut.split()]
    mots = [m for m in mots if m]
    for taille in (1, 2, 3):
        for i in range(len(mots) - taille + 1):
            bout = " ".join(mots[i:i + taille])
            if hashlib.sha256(bout.encode("utf-8")).hexdigest() == attendue:
                return True
    return False


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
    if not AILLEURS.search(texte):
        return 0                       # je ne l'envoie nulle part
    if montre(texte):
        return 0                       # le contenu est sous ses yeux
    if ACTION.search(texte):
        return 0                       # un bouton pour agir, pas pour lire

    att = empreinte_posee()
    if att and mot_de_passe_donne(texte, att):
        return 0                       # passage autorise, mot de passe donne

    print(
        "GARDE « NE M'ENVOIE PAS AILLEURS » — refuse.\n\n"
        "Tu l'envoies ouvrir ou lire quelque chose, et le contenu n'est PAS\n"
        "dans ton message. Il ne le lira pas. Il l'a dit : « dans un fichier\n"
        "je vais rien lire tu met ici ».\n\n"
        "Un texte que tu as ecrit se LIT dans ta reponse. Le fichier sert a le\n"
        "garder, pas a l'aller chercher. Le nom du fichier vient APRES le\n"
        "contenu, en une ligne, jamais a la place.\n\n"
        "Trois sorties, une seule est interdite :\n"
        "  1. Colle le contenu ici, dans un bloc de code, puis nomme le\n"
        "     fichier en une ligne.\n"
        "  2. Si c'est trop long pour etre lu d'un trait, montre LE MORCEAU\n"
        "     QUI COMPTE et dis pourquoi tu ne montres pas le reste.\n"
        "  3. Si c'est une ACTION et non un texte, propose un bouton : une\n"
        "     action ne se lit pas, elle se clique.\n"
        "Reecris ta reponse.",
        file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
