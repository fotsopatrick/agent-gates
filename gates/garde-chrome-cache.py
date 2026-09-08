#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# GARDE-FOU (PreToolUse) — rend IMPOSSIBLE un Chrome CACHÉ sur nomi.
# Règle de la personne (06/09/2026) : « tous les chrome je dois les voir »,
# « rend impossible les chrome caché », « tu peux ouvrir chrome, juste pas caché ».
#
# Donc :
#   - Chrome NORMAL (une vraie fenêtre que la personne voit)  -> AUTORISÉ, ça passe.
#   - Chrome CACHÉ (sans fenêtre, ou un faux profil jetable, ou un robot)
#     -> INTERDIT, on bloque. C'est lui qui dessine de la 3D à fond et fait
#        ronfler le PC sans que la personne voie rien.
#
# Contrat : sortie 2 = BLOQUER l'outil ; tout autre code = laisser passer.
import json, sys, re

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

# ce qui trahit un Chrome CACHÉ (et seulement ça)
CACHE = [
    r'--headless',                       # sans fenêtre : le vrai caché
    r'--dump-dom', r'--screenshot', r'--print-to-pdf',   # modes sans fenêtre
    r'--user-data-dir[= ]\s*/tmp',       # faux profil jetable dans /tmp = fenêtre qu'on ne retrouve pas
    r'puppeteer', r'playwright',          # navigateur-robot (caché par défaut)
    r'\bchrome\b.*--remote-debugging-port',  # piloté en douce
]

def main():
    try:
        hook = json.loads(sys.stdin.read() or "{}")
    except Exception:
        sys.exit(0)
    if hook.get("tool_name") != "Bash":
        sys.exit(0)
    cmd = (hook.get("tool_input") or {}).get("command", "") or ""
    if any(re.search(p, cmd) for p in CACHE):
        sys.stderr.write(
            "GARDE chrome : un Chrome CACHE est INTERDIT sur nomi. la personne doit VOIR "
            "chaque fenetre Chrome. Le cache dessine de la 3D a fond et fait ronfler le PC. "
            "Tu peux ouvrir un Chrome NORMAL (google-chrome <adresse>, une vraie fenetre), "
            "PAS un chrome sans fenetre ni un faux profil jetable dans /tmp.")
        sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()

# ══════════════════════════════════════════════════════════════════
#  DEBRANCHE LE 06/09/2026 — ce mur a ete FUSIONNE.
#
#  Deux sessions Claude ont ecrit le meme garde le meme jour, sur le meme
#  sujet : celui-ci et « garde-navigateur.py ». Deux murs pour une regle.
#
#  Ce qu'il apportait de mieux, et qui a ete repris dans l'autre :
#    - les trois modes qui rendent la main sans montrer de fenetre :
#      --dump-dom, --screenshot, --print-to-pdf ;
#    - la raison mesuree : un Chrome sans fenetre dessine de la 3D a fond et
#      fait ronfler le PC, sans que personne le voie.
#
#  Ce qui lui manquait :
#    - aucun test a cote ;
#    - il ne voyait ni le faux ecran (Xvfb), ni le navigateur partage, ni
#      selenium ;
#    - il refusait meme quand on ECRIVAIT le mot dans un fichier, sans rien
#      lancer. Il a bloque deux commandes qui ne faisaient que rediger.
#
#  Le mur qui vaut, maintenant : ~/.claude/portes/garde-navigateur.py
#  Son controle :                bash ~/.claude/portes/test-garde-navigateur.sh
#  Ce fichier n'est plus declare dans ~/.claude/settings.json. On le garde
#  pour la trace, pas pour l'usage.
# ══════════════════════════════════════════════════════════════════
