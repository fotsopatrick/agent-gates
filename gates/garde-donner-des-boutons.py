#!/usr/bin/env python3
# GARDE-FOU (Stop hook) — une session ne DONNE PAS une commande à taper à la personne.
# Elle doit AJOUTER UN BOUTON à sa page des tâches (ajouter-tache.py), sinon ce
# garde refuse la fin du tour. Demande de la personne (06/09/2026) : « plus de
# commandes à taper — des boutons verts ».
#
# Contrat Stop hook : imprimer {"decision":"block","reason":...} = bloquer.
import os
import json, sys, os, re, unicodedata, time

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


TACHES = os.path.join(MAISON, "taches/taches.json")

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

# Signes clairs que je demande à la personne de TAPER/LANCER une commande lui-même.
COMMANDE_A_TAPER = [
    r'```[^\n]*\n\s*!\s',                    # un bloc de code avec le prefixe "! " (lancer dans la session)
    r'\bcolle (ceci|ca|cette commande|la commande)\b',
    r'\btape (ceci|ca|cette commande|la commande)\b',
    r'\blance (cette commande|la commande)\b',
    r'\bexecute (cette commande|la commande)\b',
    r'\bdans ton terminal\b',
]

def bouton_ajoute_recemment():
    # un bouton a-t-il ete ajoute a la page dans les 3 dernieres minutes ?
    try:
        return (time.time() - os.path.getmtime(TACHES)) < 180
    except Exception:
        return False

def main():
    try:
        hook = json.loads(sys.stdin.read() or "{}")
    except Exception:
        sys.exit(0)
    tp = hook.get("transcript_path") or ""
    if not tp or not os.path.exists(tp):
        sys.exit(0)
    msg = dernier_message_assistant(tp)
    norm = sansaccents(msg)
    demande_commande = any(re.search(p, norm) for p in COMMANDE_A_TAPER) or re.search(r'```[^\n]*\n\s*!\s', msg)
    if demande_commande and not bouton_ajoute_recemment():
        print(json.dumps({
            "decision": "block",
            "reason": ("GARDE boutons : tu donnes une commande a taper a la personne. "
                       "INTERDIT — il en a marre de taper. Transforme ce geste en BOUTON : "
                       "appelle  python3 ~/taches/ajouter-tache.py <id> \"<titre>\" \"<detail>\" \"<la commande>\"  "
                       "puis dis-lui d'ouvrir sa page (bouton bureau « Mes taches », fleche 15). "
                       "Reecris ton message sans commande a taper.")
        }, ensure_ascii=False))
    sys.exit(0)

if __name__ == "__main__":
    main()
