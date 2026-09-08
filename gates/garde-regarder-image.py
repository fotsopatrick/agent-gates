#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GARDE « REGARDE L'IMAGE » (Stop hook) — on ne dit pas qu'une image est bonne
sans l'avoir REGARDEE.

POURQUOI CE FICHIER EXISTE (05/09/2026).
Le studio a fabrique un fichier appele « fontaine_013_v1.glb ». J'ai lu le NOM
du fichier et j'ai annonce a la personne : « il fabrique bien une fontaine ».
la personne a demande : « tu l'as regardee ? ». Non. Quand je l'ai enfin ouverte,
ce n'etait pas une fontaine : quatre murs ecartes, un cube qui flotte, trois
sapins tombes a cote.

Un nom de fichier n'est pas une preuve. Une taille en octets n'est pas une
preuve. La SEULE preuve qu'une image est bonne, c'est de l'avoir affichee.

CE QUE FAIT CE GARDE.
Pendant le tour qui vient de finir, il cherche :
  1. les IMAGES FABRIQUEES — un rendu Blender, un montage ffmpeg, une capture ;
  2. les IMAGES REGARDEES — un appel a l'outil Read sur un fichier image, ou
     une capture d'ecran du navigateur (elle s'affiche toute seule).

Si une image a ete fabriquee, que rien n'a ete regarde, et que le message
final PARLE de ce qu'on voit (« regarde », « c'est joli », « voila la
fontaine »), il BLOQUE la fin du tour.

Il ne bloque PAS quand :
  - aucune image n'a ete fabriquee dans le tour ;
  - au moins une image a ete regardee ;
  - le message final ne pretend rien sur l'aspect (il dit juste « le fichier
    est ecrit », ce qui est vrai et verifiable autrement).
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

IMAGE = re.compile(r"[\w./~-]+\.(?:png|jpe?g|webp|gif|bmp)\b", re.I)

# UNE PAGE AUSSI SE REGARDE (07/09/2026).
# Meme faute que la fontaine, sous une autre forme : j'ai fabrique une page
# pour la personne, puis je la lui ai RECOPIEE en texte au lieu de la lui ouvrir.
# La cause, sans nom propre : je choisis la forme de ma reponse d'apres ce que
# j'ai fabrique (du texte), au lieu de ce que la chose EST pour celui qui la
# recoit (une page). Une page se regarde ; la recopier ne dit ni si c'est
# beau, ni si c'est casse.
PAGE_LIVREE = re.compile(r"/livrables/[\w./~ -]+\.html?\b", re.I)

# Un chemin de page CITE dans un banc de tests ou dans une porte n'est pas une
# page fabriquee : c'est un exemple. Une porte doit refuser ce qui est mauvais,
# jamais ce qu'elle n'a pas compris.
EXEMPLE = re.compile(r"/controles/|\.claude/portes/|"
                     r"\b(?:banc|test|garde)-[\w-]*\.(?:py|sh)\b", re.I)

# On l'a MONTREE : ouverte a son ecran, ou envoyee, ou photographiee.
MONTREE = re.compile(r"\bxdg-open\b|\bnav\.py\s+ouvre|\bnav\.js\b|"
                     r"SendUserFile|oeil\.py\s+(?:photo|regarde)", re.I)

# On a fabrique une image : ces traces le disent. On exige un OUTIL qui
# dessine — pas un simple mot. « apercu » et « capture » sont sortis de la
# liste : ils apparaissent dans des noms de fichiers et des phrases, sans
# qu'aucune image ne soit nee.
FABRIQUE = re.compile(
    r"\bblender\b|\bffmpeg\b|\bconvert\b|\bmagick\b|"
    r"render\.render|write_still|screencapture", re.I)

# Ces chemins parlent DU garde, pas d'un travail d'image. On les ignore :
# sinon le garde se declenche sur lui-meme et sur ses propres essais.
SOI_MEME = re.compile(r"\.claude/portes/|garde-regarder-image|"
                      r"test-garde-regarder-image", re.I)

# Le message final PRETEND quelque chose sur l'aspect.
PRETEND = [
    "regarde l image", "regarde la", "regarde l", "voila la", "voila le",
    "voici la", "voici le", "c est joli", "c est beau", "le rendu est",
    "les couleurs", "on voit", "tu verras", "l image montre", "sur l image",
    "elle ressemble", "il ressemble", "ca ressemble", "le resultat est",
    "c est reussi", "bien fabrique", "correctement fabrique",
    "l objet est bon", "il fabrique bien", "elle fabrique bien",
    "planche", "apercu", "capture d ecran",
]


def sans_accents(s):
    plat = "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn").lower()
    return plat.replace("’", " ").replace("'", " ")


def lire_tour(chemin):
    """Rend (a_fabrique, a_regarde, dernier_texte) pour le tour qui finit.

    Le tour = tout ce qui suit le dernier message de la personne.
    """
    lignes = []
    try:
        for ligne in open(chemin, encoding="utf-8", errors="replace"):
            try:
                lignes.append(json.loads(ligne))
            except Exception:
                continue
    except Exception:
        return False, True, "", False, True   # journal illisible : on ne bloque pas

    # on remonte jusqu'au dernier tour de la personne
    debut = 0
    for i in range(len(lignes) - 1, -1, -1):
        if lignes[i].get("type") == "user":
            m = lignes[i].get("message") or {}
            c = m.get("content")
            # un vrai message de la personne, pas un resultat d'outil
            if isinstance(c, str) and c.strip():
                debut = i
                break
            if isinstance(c, list) and any(
                    isinstance(x, dict) and x.get("type") == "text" for x in c):
                debut = i
                break

    fabrique = False
    regarde = False
    page_faite = False       # une page a-t-elle ete ecrite dans les livrables ?
    page_montree = False     # l'a-t-on ouverte / envoyee / photographiee ?
    dernier = ""
    for d in lignes[debut:]:
        t = d.get("type")
        m = d.get("message") or {}
        c = m.get("content")

        if t == "assistant" and isinstance(c, list):
            for x in c:
                if not isinstance(x, dict):
                    continue
                if x.get("type") == "text" and x.get("text", "").strip():
                    dernier = x["text"]
                if x.get("type") != "tool_use":
                    continue
                nom = x.get("name", "")
                e = json.dumps(x.get("input") or {}, ensure_ascii=False)
                # a-t-on REGARDE une image ?
                if nom == "Read" and IMAGE.search(e):
                    regarde = True
                if nom.startswith("mcp__claude-in-chrome__") and "screenshot" in e:
                    regarde = True     # une capture s'affiche toute seule
                if nom == "SendUserFile" and IMAGE.search(e):
                    regarde = True     # elle part sous les yeux de la personne
                # a-t-on FABRIQUE une image ?
                if (nom in ("Bash", "Write", "Edit")
                        and PAGE_LIVREE.search(e)
                        and not EXEMPLE.search(e)):
                    page_faite = True
                if nom == "Bash" and MONTREE.search(e):
                    page_montree = True
                if nom in ("SendUserFile",) and PAGE_LIVREE.search(e):
                    page_montree = True
                if nom.startswith("mcp__claude-in-chrome__"):
                    page_montree = True     # on parle au vrai navigateur
                if (nom in ("Bash", "Write") and not SOI_MEME.search(e)
                        and FABRIQUE.search(e)):
                    # un outil qui fabrique des images suffit : « blender -b -P
                    # planche.py » ne nomme aucun .png, et fabrique pourtant
                    # six images. Attendre un nom de fichier laissait passer
                    # le cas le plus frequent.
                    fabrique = True

        if t == "user" and isinstance(c, list):
            for x in c:
                if isinstance(x, dict) and x.get("type") == "tool_result":
                    s = json.dumps(x.get("content"), ensure_ascii=False)
                    # une image renvoyee par un outil s'affiche : c'est regarde
                    if '"image"' in s or '"source"' in s and "base64" in s:
                        regarde = True
                    if (not SOI_MEME.search(s) and IMAGE.search(s)
                            and FABRIQUE.search(s)):
                        fabrique = True
    return fabrique, regarde, dernier, page_faite, page_montree


def main():
    try:
        entree = json.load(sys.stdin)
    except Exception:
        return 0
    if entree.get("stop_hook_active"):
        return 0                      # on ne boucle pas sur soi-meme
    chemin = entree.get("transcript_path") or ""
    if not chemin or not os.path.exists(chemin):
        return 0

    fabrique, regarde, dernier, page_faite, page_montree = lire_tour(chemin)

    # UNE PAGE FABRIQUEE DOIT ETRE MONTREE, JAMAIS RECOPIEE.
    if page_faite and not page_montree:
        print(
            "GARDE « MONTRE LA PAGE » — tu as ecrit une page dans les "
            "livrables et tu ne l'as pas ouverte.\n"
            "Une page se REGARDE. La recopier en texte ne dit ni si elle est "
            "belle, ni si elle est cassee.\n"
            "  1. ouvre-la a son ecran :\n"
            "       setsid xdg-open <la page> >/dev/null 2>&1 &\n"
            "     (setsid = elle reste ouverte quand la commande finit)\n"
            "  2. si l'oeil repond, donnes-en une image ; s'il est ferme, "
            "DIS que tu n'as rien vu.\n"
            "  3. nomme-la par sa fleche de Mes travaux, APRES l'avoir montree.\n"
            "Puis refais ta reponse.",
            file=sys.stderr)
        return 2

    if not fabrique or regarde:
        return 0

    plat = sans_accents(dernier)
    if not any(p in plat for p in PRETEND):
        return 0                      # on n'affirme rien sur l'aspect : ok

    print(
        "GARDE « REGARDE L'IMAGE » — tu as fabrique une image dans ce tour, tu "
        "n'en as ouvert AUCUNE, et tu parles pourtant de ce qu'on voit.\n"
        "Un nom de fichier n'est pas une preuve. Une taille en octets non plus.\n"
        "OUVRE l'image avec l'outil Read (elle s'affiche), REGARDE-la, et dis "
        "ce que tu vois vraiment — meme si c'est rate. Puis refais ta reponse.",
        file=sys.stderr)
    return 2                          # 2 = bloque et renvoie le texte a Claude


if __name__ == "__main__":
    sys.exit(main())
