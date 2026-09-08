#!/usr/bin/env python3
# GARDE-FOU (Stop hook) — si la personne a demandé un RAPPORT DE SESSION et qu'aucun
# rapport n'a été écrit dans ~/rapports-sessions/, refuse de finir le tour.
# C'est un mur : la session est OBLIGÉE d'écrire son rapport quand la personne le
# demande. Créé le 06/09/2026 à la demande de la personne.
import os
import json, sys, os, re, unicodedata

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

# LA MAISON EST FIXE (06/09/2026). Une session peut tourner sous root :
# expanduser("~") rendait alors /root, et ce garde ne trouvait plus ses
# fichiers — il repondait "aucun code defini" alors que le code etait pose.
# Un garde qui ne trouve pas ses fichiers ne garde rien.
MAISON = os.path.expanduser("~")


DOSSIER = os.path.join(MAISON, "rapports-sessions")

def sansaccents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn').lower()

# la personne DEMANDE un rapport : un verbe d'écriture + « rapport », ou « ton
# rapport », ou « rapport de session/fin ». On évite les faux positifs (parler
# de la compétence rapport, du dossier rapport, sans demander de l'écrire).
DEMANDES = [
    r'\b(fais|fait|ecris|ecrit|redige|rediges|faites|donne|donne moi|fais moi)\b[^.?!]{0,25}\brapport\b',
    r'\bton rapport\b', r'\bvotre rapport\b',
    r'\brapport de (session|fin|la session)\b',
    r'\brapporte (ta|ton|la) session\b',
]
EXCLUS = [r'competence rapport', r'skill rapport', r'dossier rapport',
          r'garde[- ]fou', r'ou (les|mettent)', r'article']

def messages_utilisateur(chemin):
    out = []
    try:
        for ligne in open(chemin, encoding="utf-8", errors="replace"):
            try: d = json.loads(ligne)
            except Exception: continue
            if d.get("type") != "user": continue
            c = (d.get("message") or {}).get("content")
            if isinstance(c, list):
                t = " ".join(x.get("text", "") for x in c
                             if isinstance(x, dict) and x.get("type") == "text")
            else:
                t = str(c or "")
            if t.strip(): out.append(t)
    except Exception:
        pass
    return out

def rapport_demande(chemin):
    for t in messages_utilisateur(chemin):
        n = sansaccents(t)
        if any(re.search(x, n) for x in EXCLUS):
            continue
        if any(re.search(p, n) for p in DEMANDES):
            return True
    return False

def rapport_ecrit(chemin):
    # preuve dans la transcription : un fichier RAPPORT écrit dans le dossier
    try:
        brut = open(chemin, encoding="utf-8", errors="replace").read()
    except Exception:
        return True                      # illisible -> on ne bloque pas
    if re.search(r'rapports-sessions/RAPPORT', brut):
        return True
    # ou un fichier RAPPORT-*.md récent (moins de 2h) dans le dossier
    try:
        import time
        for f in os.listdir(DOSSIER):
            if f.startswith("RAPPORT") and f.endswith(".md"):
                p = os.path.join(DOSSIER, f)
                if time.time() - os.path.getmtime(p) < 7200:
                    return True
    except Exception:
        pass
    return False

def main():
    try:
        hook = json.loads(sys.stdin.read() or "{}")
    except Exception:
        sys.exit(0)
    tp = hook.get("transcript_path") or ""
    if not tp or not os.path.exists(tp):
        sys.exit(0)
    if rapport_demande(tp) and not rapport_ecrit(tp):
        print(json.dumps({
            "decision": "block",
            "reason": ("GARDE-FOU rapport : la personne a demandé un rapport de session "
                       "et tu ne l'as pas encore écrit. Invoque la compétence "
                       "« rapport » et écris ton rapport dans "
                       "~/rapports-sessions/RAPPORT-AAAA-MM-JJ-sujet.md (ce qui a "
                       "été fait, montré, ce qui reste, ce qui attend la personne), "
                       "AVANT de finir le tour.")
        }, ensure_ascii=False))
    sys.exit(0)

if __name__ == "__main__":
    main()
