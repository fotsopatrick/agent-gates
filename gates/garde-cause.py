#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GARDE DE LA CAUSE — on repare la CAUSE, jamais le symptome tout seul.

POURQUOI CE GARDE EXISTE
Ne d'une faute reelle le 08/09/2026 : trois pannes en une matinee,
et a chaque fois la reparation visait la ou ca se voyait, pas la ou
c'etait casse.
Un symptome, c'est ce qui se voit : la page est blanche, le robot ne repond
plus, le chiffre est faux. La cause, c'est ce qui l'a produit. Reparer le
symptome sans la cause, c'est essuyer l'eau par terre sans fermer le
robinet : ca revient toujours, et souvent plus tard, plus loin, plus cher.

CE QUE LE GARDE EXIGE, ET RIEN D'AUTRE
Des que la reponse annonce une reparation (« repare », « corrige »,
« regle », « ca remarche »), elle doit contenir DEUX choses dans le meme
message :

  1. LA CAUSE, nommee. Pas « ca marche a nouveau » : « ca ne marchait pas
     PARCE QUE le fichier lu n'etait pas celui qui est servi ».

  2. LE TEST QUI A ETE ROUGE D'ABORD. C'est le lien avec les tests, et
     c'est le seul lien qui prouve quelque chose : un test ecrit APRES la
     reparation passe au vert meme si on a repare le mauvais endroit.
     Un test qui a d'abord echoue sur la cause, lui, ne peut pas mentir.
     Marques acceptees : « rouge d'abord », « vu rouge », « rouge puis
     vert », « le test echouait », « reproduit la panne ».

L'ORDRE, PARCE QUE C'EST LUI QUI COMPTE
     observer  ->  nommer la cause  ->  test qui reproduit (ROUGE)
     ->  reparer la cause  ->  le meme test (VERT)

QUAND IL SE TAIT
- La reponse ne repare rien (une question, un constat, une recherche).
- Le geste appartient a la personne : sa main, un bouton, un mot de passe.
  On n'exige pas la preuve de ce qu'on n'a pas fait.
- Le meme texte a deja ete juge (empreinte), donc on ne le juge pas deux
  fois : le journal met parfois un instant a livrer le message neuf.

Contrat du crochet Stop : on ecrit un refus en JSON sur la sortie standard,
ou rien du tout. Code 0 dans les deux cas.
"""
import hashlib
import json
import os
import re
import sys
import time

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
ETAT = os.environ.get("GARDE_CAUSE_ETAT",
                      os.path.join(MAISON, ".claude/portes/.dernier-juge-cause"))
ATTENTE_MAX = 2.0
PAS = 0.2

# 1. La reponse annonce-t-elle une REPARATION ?
REPARATION = re.compile(
    r"(\bj[’' ]ai (repare|reparee|corrige|corrigee|regle|reglee|resolu|resolue|"
    r"debloque|debloquee|remis en marche|remis d[’' ]aplomb)\b|"
    r"\bc[’' ]est (repare|reparee|corrige|corrigee|regle|reglee|resolu|resolue)\b|"
    r"\b(le|la|ce|cette) (probleme|panne|bogue|bug|erreur|souci)[^.\n]{0,60}"
    r"(est|sont) (repare|reparee|corrige|corrigee|regle|reglee|resolu|resolue)\b|"
    r"\bca (remarche|refonctionne|remarche maintenant)\b|"
    r"\b(remarche|refonctionne) (maintenant|de nouveau|a nouveau)\b|"
    r"\bplus de (bogue|bug|erreur|panne)\b)", re.I)

# 2. La CAUSE est-elle nommee ?
CAUSE = re.compile(
    r"(\bla cause\b|\bles causes\b|\bla vraie cause\b|\bcause racine\b|"
    r"\bl[’' ]origine\b|\ba l[’' ]origine\b|\bla racine\b|"
    r"\bparce que\b|\bcar le\b|\bcar la\b|\bcar il\b|\bcar elle\b|"
    r"\bvenait de\b|\bvenaient de\b|\bd[’' ]ou (venait|vient)\b|"
    r"\ble coupable\b|\bpourquoi (c[’' ]|ce|cela|ca )?(etait|est) arrive\b|"
    r"\ble vrai defaut\b|\bce qui l[’' ]a (produit|cause|provoque)\b)", re.I)

# 3. Le test a-t-il ete ROUGE D'ABORD ?
ROUGE_DABORD = re.compile(
    r"(\brouge d[’' ]abord\b|\bd[’' ]abord rouge\b|\bvu rouge\b|\bvue rouge\b|"
    r"\brouge,? puis vert\b|\brouge avant\b|\bil etait rouge\b|"
    r"\ble test (echouait|a echoue|tombait|refusait|disait non)\b|"
    r"\btest rouge\b|\breproduit la (panne|faute|erreur|cause)\b|"
    r"\breproduction de la (panne|faute)\b|"
    r"\ble test a bien refuse\b|\ba d[’' ]abord echoue\b)", re.I)

# 4. Le geste appartient-il a la personne ?
SA_MAIN = re.compile(
    r"(ta main|sa main|ton geste|c[’' ]est a toi|la decision est a toi|"
    r"mon harnais|refuse par (mon|le) (harnais|garde|classificateur)|"
    r"je ne peux pas le lancer moi-?meme|"
    r"\bbouton\b|\bclique\b|mot de passe|\bjeton\b)", re.I)


def dernier_message(chemin):
    """Le dernier texte que j'ai ecrit, lu dans le journal de la session."""
    if not chemin or not os.path.exists(chemin):
        return ""
    dernier = ""
    try:
        with open(chemin, encoding="utf-8", errors="replace") as f:
            for ligne in f:
                try:
                    o = json.loads(ligne)
                except Exception:
                    continue
                if o.get("type") != "assistant":
                    continue
                c = (o.get("message") or {}).get("content")
                if isinstance(c, str):
                    dernier = c
                elif isinstance(c, list):
                    bouts = [b.get("text", "") for b in c
                             if isinstance(b, dict) and b.get("type") == "text"]
                    if any(b.strip() for b in bouts):
                        dernier = " ".join(bouts)
    except OSError:
        return ""
    return dernier


def texte_juge(donnees):
    for cle in ("last_assistant_message", "assistant_message", "message"):
        v = donnees.get(cle)
        if isinstance(v, str) and v.strip():
            return v
    return dernier_message(donnees.get("transcript_path"))


def fautes(texte):
    """Rend la liste de ce qui manque, vide si la reponse passe."""
    if not REPARATION.search(texte):
        return []
    if SA_MAIN.search(texte):
        return []
    manque = []
    if not CAUSE.search(texte):
        manque.append("LA CAUSE N'EST PAS NOMMEE")
    if not ROUGE_DABORD.search(texte):
        manque.append("AUCUN TEST VU ROUGE AVANT LA REPARATION")
    return manque


def main():
    try:
        donnees = json.load(sys.stdin)
    except Exception:
        return 0
    texte = texte_juge(donnees)
    tp = donnees.get("transcript_path")

    vu = ""
    try:
        with open(ETAT, encoding="utf-8") as f:
            vu = f.read().strip()
    except OSError:
        pass

    empreinte = hashlib.sha1(texte.encode("utf-8")).hexdigest()
    fin = time.time() + ATTENTE_MAX
    while empreinte == vu and time.time() < fin and tp:
        time.sleep(PAS)
        texte = dernier_message(tp)
        empreinte = hashlib.sha1(texte.encode("utf-8")).hexdigest()
    if empreinte == vu or not texte.strip():
        return 0
    try:
        os.makedirs(os.path.dirname(ETAT), exist_ok=True)
        with open(ETAT, "w", encoding="utf-8") as f:
            f.write(empreinte)
    except OSError:
        pass

    f = fautes(texte)
    if not f:
        return 0
    print(json.dumps({
        "decision": "block",
        "reason": (
            "GARDE DE LA CAUSE — refuse. " + " | ".join(f) + ".\n\n"
            "Tu annonces une reparation. Reparer le symptome sans la cause, "
            "c'est essuyer l'eau par terre sans fermer le robinet : ca "
            "revient.\n\n"
            "Refais ta reponse dans cet ordre, et montre chaque etape :\n"
            "  1. Ce qui se voyait (le symptome).\n"
            "  2. POURQUOI c'est arrive — la cause, nommee en clair.\n"
            "  3. Le test qui reproduit cette cause, vu ROUGE avant de "
            "reparer. Un test ecrit apres la reparation passe au vert meme "
            "si tu as repare le mauvais endroit : il ne prouve rien.\n"
            "  4. La reparation de la CAUSE.\n"
            "  5. Le meme test, maintenant VERT, avec ses chiffres.\n\n"
            "Si tu ne connais pas encore la cause, dis-le : « je ne sais pas "
            "encore, voila ce qui trancherait ». C'est permis. Annoncer une "
            "reparation sans cause ne l'est pas."),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
