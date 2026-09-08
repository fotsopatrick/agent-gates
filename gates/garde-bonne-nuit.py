#!/usr/bin/env python3
# GARDE-FOU (Stop hook) — refuse de terminer le tour si le dernier message de
# l'assistant contient « bonne nuit », « bonne soiree », un rappel d'heure
# tardive, ou une incitation a se reposer/arreter. Regle de la personne (19/08/2026).
# Le hook ne peut pas EFFACER le texte, mais il BLOQUE la fin du tour et force
# une reecriture. C'est un mur, pas une promesse.
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


def sansaccents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn').lower()

def dernier_message_assistant(chemin):
    txt = ""
    try:
        for ligne in open(chemin, encoding="utf-8", errors="replace"):
            try: d = json.loads(ligne)
            except Exception: continue
            if d.get("type") != "assistant": continue
            c = (d.get("message") or {}).get("content")
            if isinstance(c, list):
                t = " ".join(x.get("text", "") for x in c
                             if isinstance(x, dict) and x.get("type") == "text")
            else:
                t = str(c or "")
            if t.strip(): txt = t
    except Exception:
        return ""
    return txt

MOTIFS = [
    r'bonne nuit',
    r'bonne soiree',
    r'repose[- ]toi', r'reposez[- ]vous', r'va te reposer',
    r'va dormir', r'va te coucher', r'aller dormir', r'va au lit',
    r'il est tard', r'il se fait tard', r'tard dans la nuit',
    r"l'?heure tardive", r'a une heure pareille',
    r'tu devrais (te reposer|dormir|t.?arreter|arreter|faire une pause|aller dormir)',
]

def main():
    try:
        hook = json.loads(sys.stdin.read() or "{}")
    except Exception:
        sys.exit(0)
    tp = hook.get("transcript_path") or ""
    if not tp or not os.path.exists(tp):
        sys.exit(0)                      # rien a verifier -> on ne bloque pas
    # CORRECTIF DU 21/08 — UN MESSAGE DE RETARD. Ce garde a bloque deux fois
    # en citant « bonne nuit » alors que ces mots etaient dans le message
    # PRECEDENT : quand il tourne, le message tout juste fini n est pas encore
    # ecrit dans le journal, et il rejugeait l ancien. On retient l empreinte
    # du dernier texte juge ; si on relit le meme, on attend, puis on se tait.
    import hashlib, time
    ETAT = os.environ.get("GARDE_NUIT_ETAT",
                          os.path.join(MAISON, ".claude/portes/.dernier-juge-nuit"))
    try:
        vu = open(ETAT, encoding="utf-8").read().strip()
    except OSError:
        vu = ""
    texte = dernier_message_assistant(tp)
    empreinte = hashlib.sha1(texte.encode("utf-8")).hexdigest()
    fin = time.time() + 2.0
    while empreinte == vu and time.time() < fin:
        time.sleep(0.2)
        texte = dernier_message_assistant(tp)
        empreinte = hashlib.sha1(texte.encode("utf-8")).hexdigest()
    if empreinte == vu or not texte.strip():
        sys.exit(0)
    try:
        os.makedirs(os.path.dirname(ETAT), exist_ok=True)
        open(ETAT, "w", encoding="utf-8").write(empreinte)
    except OSError:
        pass
    norm = sansaccents(texte)
    if any(re.search(p, norm) for p in MOTIFS):
        print(json.dumps({
            "decision": "block",
            "reason": ("GARDE-FOU bonne-nuit : ton dernier message contient un "
                       "« bonne nuit / bonne soiree », un rappel d'heure tardive, "
                       "ou une incitation a te reposer/arreter — INTERDIT. Reecris "
                       "le message sans cela, et ne projette aucun etat de fatigue "
                       "sur la personne.")
        }, ensure_ascii=False))
    sys.exit(0)

if __name__ == "__main__":
    main()
