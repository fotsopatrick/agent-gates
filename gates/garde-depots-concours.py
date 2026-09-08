#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GARDE DES DEPOTS DE CONCOURS — on ne touche pas a ce qui est deja rendu.

POURQUOI CE GARDE EXISTE
Ne d'une faute reelle le 08/09/2026 : le donjon rendu au concours
n'etait garde par rien, et le labo 3D non plus.
Un dossier rendu a un concours n'est plus un chantier. Les juges le lisent
peut-etre en ce moment. Une seule ligne changee peut :
  - faire mentir la video de demonstration, qui montre l'ancienne version ;
  - casser un lien que le jury a note ;
  - faire croire a une modification apres la date limite — et disqualifier.

la personne l'a dit le 08/09/2026, sans detour : « ne pas toucher au depot du
hackathon », puis « ni au labo 3d », puis « met le storage google dedans ».
Une regle ecrite n'est pas suivie ; une regle codee l'est.

CE QU'IL REFUSE
Toute ecriture — modifier, ecrire, effacer, deplacer, enregistrer, envoyer —
dans ce qui est rendu : les dossiers, les depots distants, et le seau de
stockage chez Google que le jury ouvre dans son navigateur.

CE QU'IL LAISSE PASSER
LIRE. Toujours. Ouvrir, chercher, compter, comparer, recopier ailleurs.
On ne peut simplement pas changer ce qui est parti.

DEUX FAUX POSITIFS DEJA PAYES, ET CE QU'ILS ONT APPRIS (08/09/2026)
  1. Il a refuse un simple « ls » parce que la commande finissait par
     « 2>/dev/null » — jeter les messages d'erreur. Une redirection ne compte
     donc que si SA CIBLE est dans un dossier rendu.
  2. Il a refuse la reparation de lui-meme, parce que le nom d'un dossier
     rendu apparaissait dans le TEXTE qu'on ecrivait ailleurs. Un garde qu'on
     ne peut plus reparer est une impasse : les gardes et leurs bancs d'essai
     sont donc exemptes, et eux seuls.

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

# CE QUI EST RENDU. Rien en dur ici : la liste vient de regles.json, le
# fichier « vos regles a vous ». Un garde public qui porterait les dossiers
# de son auteur parlerait de quelqu'un d'autre que de vous.
_R = charger_regles({
    "dossiers_rendus": [],
    "depots_rendus": [],
    "seaux_rendus": [],
})

def _chemin(x):
    return os.path.expanduser(x) if isinstance(x, str) else x

INTOUCHABLES = [(_chemin(d[0]), d[1] if len(d) > 1 else "un dossier rendu")
                for d in _R.get("dossiers_rendus", []) if d]
DEPOTS_DISTANTS = list(_R.get("depots_rendus", []))
SEAUX = list(_R.get("seaux_rendus", []))

# LES EXEMPTIONS : les gardes eux-memes et leurs bancs d'essai. Sans elles,
# on ne pourrait plus reparer un garde des qu'il cite un dossier rendu.
EXEMPTS = [
    os.path.join(MAISON, ".claude/portes"),
    os.path.join(MAISON, ".claude/hooks"),
    os.path.join(MAISON, "controles"),
]

# Les gestes qui CHANGENT quelque chose. Lire n'y est pas.
ECRITURE = re.compile(
    r"\b(rm|mv|cp|dd|truncate|shred|sed\s+-i|tee|chmod|chown|"
    r"git\s+(commit|add|push|rm|mv|reset|checkout|restore|clean|merge|rebase)|"
    r"mkdir|touch|ln)\b", re.I)

# Les gestes du stockage Google qui changent quelque chose. « ls » et « cat »
# n'y sont pas : lire reste libre.
GOOGLE_ECRIT = re.compile(
    r"\b(gsutil|gcloud\s+storage)\b.{0,90}?"
    r"\b(cp|mv|rm|rsync|setmeta|acl|iam|delete|upload|update)\b", re.I | re.S)

# Une redirection ne compte que par SA CIBLE. « 2>/dev/null » n'ecrit rien.
REDIRECTION = re.compile(r">>?\s*([~\w./-]+)")


def cibles_de_redirection(cmd):
    return [c for c in REDIRECTION.findall(cmd) if not c.startswith("/dev/")]


def _reel(chemin):
    try:
        return os.path.realpath(os.path.expanduser(chemin))
    except Exception:
        return None


def exempt(chemin):
    """Un garde ou un banc d'essai : on doit pouvoir les reparer."""
    v = _reel(chemin)
    if not v:
        return False
    for d in EXEMPTS:
        r = os.path.realpath(d)
        if v == r or v.startswith(r + os.sep):
            return True
    return False


def dedans(chemin):
    """Le chemin vise-t-il ce qui est rendu ? On compare des chemins reels,
    pour qu'un detour par .. ou par un lien ne passe pas."""
    v = _reel(chemin)
    if not v:
        return None
    for dossier, pourquoi in INTOUCHABLES:
        d = os.path.realpath(dossier)
        if v == d or v.startswith(d + os.sep):
            return (dossier, pourquoi)
    return None


def refus(quoi, pourquoi):
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "GARDE DES DEPOTS DE CONCOURS — REFUS.\n\n"
                "Tu vas ECRIRE dans %s.\n"
                "C'est %s.\n\n"
                "Un dossier rendu n'est plus un chantier : les juges le lisent "
                "peut-etre maintenant. Une ligne changee peut faire mentir la "
                "video, casser un lien note par le jury, ou ressembler a une "
                "modification apres la date limite.\n\n"
                "Ce qui reste permis, et suffit presque toujours :\n"
                "  - LIRE tout ce que tu veux dedans ;\n"
                "  - COPIER ailleurs et travailler sur la copie ;\n"
                "  - construire la suite dans un dossier neuf.\n\n"
                "Si la personne veut vraiment modifier le rendu, il le dira "
                "lui-meme, et c'est sa main qui le fera."
                % (quoi, pourquoi)),
        }
    }


def dis(v):
    print(json.dumps(refus(*v), ensure_ascii=False))
    return 0


def main():
    try:
        donnees = json.load(sys.stdin)
    except Exception:
        return 0
    outil = donnees.get("tool_name") or ""
    e = donnees.get("tool_input") or {}

    if outil in ("Write", "Edit", "NotebookEdit"):
        cible = e.get("file_path") or e.get("notebook_path") or ""
        if exempt(cible):
            return 0
        v = dedans(cible)
        if v:
            return dis(v)
        return 0

    if outil != "Bash":
        return 0

    cmd = e.get("command") or ""

    # a) le stockage Google : on ne change pas ce que le jury regarde.
    if GOOGLE_ECRIT.search(cmd):
        for seau in SEAUX:
            if seau in cmd:
                return dis(("le seau Google " + seau,
                            "le jeu rendu au WebMCP Challenge, celui que le "
                            "jury ouvre dans son navigateur"))

    # b) pousser vers un depot rendu.
    if re.search(r"\bgit\s+push\b", cmd):
        for depot in DEPOTS_DISTANTS:
            if depot in cmd:
                return dis((depot, "un depot rendu a un concours"))

    # c) une redirection ne compte que si SA CIBLE est dans ce qui est rendu.
    for c in cibles_de_redirection(cmd):
        if exempt(c):
            continue
        v = dedans(c)
        if v:
            return dis(v)

    # d) COPIER ET DEPLACER : seule la DESTINATION compte.
    # Troisieme faux positif paye le 08/09/2026 : le garde a refuse
    #   cp -r ~/labo-3d ~/labo-evolution
    # alors que c est une LECTURE du labo et une ecriture AILLEURS. Copier un
    # dossier rendu vers un chantier neuf est justement la sortie que ce garde
    # recommande dans son propre refus. Un garde qui interdit sa propre
    # solution est une impasse.
    # ON COUPE LA COMMANDE EN MORCEAUX. Quatrieme faux positif du meme jour :
    # le banc ne testait que des commandes simples, la vraie vie les enchaine
    # avec « && ». « cp A B && du -sh B » etait lu comme une seule commande,
    # et le dernier mot n etait plus la destination.
    morceaux = re.split(r"&&|\|\||;|\|", cmd)
    copie_vue = False
    for bout in morceaux:
        m = re.match(r"\s*(?:cp|mv|rsync)\b(.*)$", bout)
        if not m:
            continue
        copie_vue = True
        args = [a for a in m.group(1).split() if not a.startswith("-")]
        if len(args) >= 2:
            v = dedans(args[-1])          # le dernier mot : la destination
            if v:
                return dis(v)
    if copie_vue:
        # une copie dont la destination est libre : la source peut etre un
        # dossier rendu, c est justement la sortie qu on recommande.
        autres = [b for b in morceaux
                  if not re.match(r"\s*(?:cp|mv|rsync)\b", b)]
        if not any(ECRITURE.search(b) for b in autres):
            return 0

    # e) les autres gestes qui changent quelque chose.
    if not ECRITURE.search(cmd):
        return 0
    mots = re.findall(r"[~\w./-]{4,}", cmd)
    # Si la commande travaille dans un dossier exempte (un garde, un banc),
    # on ne refuse pas : le nom d'un dossier rendu peut y apparaitre comme
    # simple texte.
    if any(exempt(m) for m in mots):
        return 0
    for mot in mots:
        v = dedans(mot)
        if v:
            return dis(v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
