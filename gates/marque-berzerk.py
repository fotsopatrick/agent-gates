#!/usr/bin/env python3
"""LA MARQUE BERZERK (UserPromptSubmit hook) — allume ou eteint le mode.

Quand la personne ecrit « berzerk » (ou « berzek », « bersek »), il dit :
« agis, ne me demande plus rien ». Ce fichier pose un drapeau. Le garde
`garde-berzerk.py` s'en sert ensuite pour refuser toute demande.

NE D'UNE COLERE REELLE (06/09/2026) : « me demande plus jamais de faire une
action ca me saoule », « surtout quand je dis berzek ». Dans la meme soiree
je lui avais rendu quatre choses a faire.

Le mode s'eteint quand il ecrit « stop berzerk », « fin berzerk »,
« arrete berzerk », ou apres 6 heures sans qu'il le redise.

Contrat du crochet UserPromptSubmit : on ne bloque jamais ici, on marque
seulement. Sortie 0 toujours.
"""
import hashlib
import json
import os
import re
import sys
import time
import unicodedata

MAISON = os.path.expanduser("~")
DRAPEAU = os.environ.get("BERZERK_DRAPEAU") or os.path.join(
    MAISON, ".claude/portes/.berzerk-actif")
# L'EMPREINTE DU MOT DE PASSE. Une empreinte est un long code calcule a partir
# du mot : on va du mot vers le code, jamais du code vers le mot. Le mot lui
# meme n'est ecrit nulle part. Fichier pose par ~/outils/mot-de-passe-berzerk.sh
EMPREINTE = os.environ.get("BERZERK_EMPREINTE") or os.path.join(
    MAISON, ".claude/portes/.berzerk-empreinte")
DUREE = 6 * 3600           # au bout de 6 heures sans rappel, le mode s'eteint

# le mot, ecrit de toutes les facons vues dans ses messages
ALLUME = re.compile(r"\bber[sz]e?r?[ck]+\b|\bmode\s+auto\b", re.I)
ETEINT = re.compile(r"\b(stop|fin|arrete|arreter|sors\s+du|quitte)\s+"
                    r"(le\s+)?(mode\s+)?ber[sz]e?r?[ck]+\b", re.I)


def empreinte_attendue():
    """Le code du mot de passe, ou None s'il n'a jamais ete pose."""
    try:
        v = open(EMPREINTE, encoding="utf-8").read().strip().lower()
        return v if len(v) == 64 else None
    except OSError:
        return None


def mot_de_passe_donne(brut, attendue):
    """Vrai si un morceau du message a exactement l'empreinte attendue.

    On regarde les mots un par un, puis par deux, puis par trois : le mot de
    passe de la personne peut etre « ouvre-toi » comme « la porte du lion ».
    On travaille sur le texte BRUT : un mot de passe garde ses accents.
    """
    mots = [m.strip(".,;:!?()[]\"'«»") for m in brut.split()]
    mots = [m for m in mots if m]
    for taille in (1, 2, 3):
        for i in range(len(mots) - taille + 1):
            bout = " ".join(mots[i:i + taille])
            if hashlib.sha256(bout.encode("utf-8")).hexdigest() == attendue:
                return True
    return False


def sans_accent(t):
    return "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn")


def main():
    try:
        hook = json.loads(sys.stdin.read() or "{}")
    except Exception:
        sys.exit(0)
    texte = sans_accent(hook.get("prompt") or "")

    if ETEINT.search(texte):
        try:
            os.remove(DRAPEAU)
        except OSError:
            pass
        sys.exit(0)

    if ALLUME.search(texte):
        attendue = empreinte_attendue()
        if attendue is None:
            print("BERZERK REFUSE : aucun mot de passe n'est pose. la personne le"
                  " pose en lancant  bash ~/outils/mot-de-passe-berzerk.sh"
                  "  — le mot ne s'affiche pas et n'est jamais enregistre,"
                  " seule son empreinte l'est. Sans lui, je reste dans le"
                  " circuit normal : je remplis les conditions et je demande"
                  " ce qui doit etre demande.")
            sys.exit(0)
        if not mot_de_passe_donne(hook.get("prompt") or "", attendue):
            print("BERZERK REFUSE : le mot de passe manque ou ne correspond"
                  " pas. Le mode n'est PAS allume. Je continue par le circuit"
                  " normal. Vous, ecrivez berzerk ET ton mot de passe dans le"
                  " meme message.")
            sys.exit(0)
        os.makedirs(os.path.dirname(DRAPEAU), exist_ok=True)
        with open(DRAPEAU, "w", encoding="utf-8") as f:
            f.write(str(int(time.time())))
        sys.exit(0)

    # ni allumage ni extinction : on regarde juste si le drapeau a expire
    if os.path.exists(DRAPEAU):
        try:
            pose = int(open(DRAPEAU, encoding="utf-8").read().strip() or 0)
            if time.time() - pose > DUREE:
                os.remove(DRAPEAU)
        except Exception:
            pass
    sys.exit(0)


main()
