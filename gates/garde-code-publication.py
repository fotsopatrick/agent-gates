#!/usr/bin/env python3
# GARDE-FOU (PreToolUse) — la publication en PRODUCTION est refusee SAUF si la
# commande porte le CODE de la personne. Concu le 06/09/2026 a sa demande.
# Contrat PreToolUse (comme porte-secrets.py) : sortie 2 = BLOQUER, sinon passer.
import os
import json, sys, os, re, hashlib

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

EMPREINTE = os.path.join(MAISON, ".claude/portes/.code-publication.sha256")
PUBLICATION = [r'publier-vitrine\.sh', r'circuit\.sh\s+approuver',
               r'publier-statique\.sh', r'push-public\.sh', r'promouvoir\.sh']
def main():
    try: hook = json.loads(sys.stdin.read() or "{}")
    except Exception: sys.exit(0)
    if hook.get("tool_name") != "Bash": sys.exit(0)
    cmd = (hook.get("tool_input") or {}).get("command", "") or ""
    # LIRE N EST PAS LANCER (07/09). Avant, cette porte refusait des que le
    # NOM d un script apparaissait dans la commande — meme dans un « grep »,
    # meme dans un texte ecrit dans un fichier. Elle bloquait la lecture.
    # Une porte doit refuser ce qui est MAUVAIS, jamais ce qu elle n a pas
    # compris. Le juge « lancement.py » repond a la seule bonne question :
    # ce script est-il LANCE ? Banc : ~/controles/banc-lire-ou-lancer.py
    sys.path.insert(0, os.path.join(MAISON, ".claude/portes"))
    try:
        from lancement import est_lance
    except Exception:
        # Si le juge manque, on garde l ancien comportement : trop severe
        # vaut mieux que pas de garde du tout. Mais on le DIT.
        sys.stderr.write("GARDE code-publication : juge lancement.py introuvable, "
                         "je refuse largement.\n")
        if not any(re.search(p, cmd) for p in PUBLICATION): sys.exit(0)
    else:
        if not est_lance(cmd, PUBLICATION): sys.exit(0)
    m = re.search(r'CODE_PUBLICATION=([^\s\'"]+)', cmd)
    if not os.path.exists(EMPREINTE):
        sys.stderr.write("GARDE code-publication : aucun code defini. la personne doit le poser avant toute publication.")
        sys.exit(2)
    attendue = open(EMPREINTE, encoding="utf-8").read().strip()
    if not m:
        sys.stderr.write("GARDE code-publication : REFUS. Publier exige le CODE de la personne. Demande-le, puis prefixe la commande de CODE_PUBLICATION=<le code>.")
        sys.exit(2)
    if hashlib.sha256(m.group(1).encode()).hexdigest() != attendue:
        sys.stderr.write("GARDE code-publication : REFUS. Code FAUX. Redemande le bon code a la personne, ne devine pas.")
        sys.exit(2)
    sys.exit(0)
if __name__ == "__main__": main()
