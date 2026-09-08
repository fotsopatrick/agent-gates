#!/usr/bin/env python3
"""Garde du navigateur — deterministe, aucune IA (doctrine le gardien).

INTERDIT D'OUVRIR UN NAVIGATEUR **CACHE** — c'est-a-dire une fenetre que
la personne ne voit pas a l'ecran.

NE DE DEUX FAUTES DU 06/09/2026, dans deux sessions differentes :
  - son navigateur s'ouvrait et se fermait en boucle. J'etais dans la cause :
    j'avais relance le navigateur partage trois fois dans la meme session ;
  - un Chrome sans fenetre dessinait de la 3D a fond et faisait ronfler le PC,
    sans que personne voie rien (le poste est deja monte a 91 degres).

Ses mots : « interdiction d'ouvrir des navigateurs caches », « tous les chrome
je dois les voir », « tu peux ouvrir chrome, juste pas cache », et la precision
qui tranche : « il doit refuser quand c'est cache uniquement ».

CE MUR EN REMPLACE DEUX. Deux sessions avaient ecrit le meme garde le meme
jour : celui-ci et « garde-chrome-cache.py ». Fusionnes ici le 06/09/2026 —
l'autre debranche, ce fichier garde ses trois trouvailles (les modes sans
fenetre --dump-dom, --screenshot, --print-to-pdf) et sa raison mesuree.

CE QUI EST REFUSE : sans ecran (--headless), les modes qui rendent la main
sans jamais montrer de fenetre (--dump-dom, --screenshot, --print-to-pdf), un
profil a part (--user-data-dir), un navigateur pilote de l'exterieur
(--remote-debugging-port), un faux ecran (Xvfb), le navigateur partage (le
script chrome-agents), ou un navigateur lance par playwright, puppeteer,
selenium.

CE QUI RESTE PERMIS : ouvrir une page A L'ECRAN chez lui (xdg-open, ou
google-chrome <adresse>) — c'est ce qui lui montre les choses ; parler au
navigateur DEJA ouvert (~/outils/nav.js, port 9333) ; lire une page avec curl ;
se BRANCHER sur un navigateur existant (« connect ») ; et ECRIRE ces mots dans
un fichier, ce qui ne lance rien.

Son controle : bash ~/.claude/portes/test-garde-navigateur.sh
Contrat du crochet PreToolUse : sortir 2 = BLOQUER, tout autre code = laisser
passer. Ce qui est ecrit sur la sortie d'erreur revient a l'agent.
"""
import json
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

# Les marques d'un navigateur qu'on ne voit pas.
CACHE = re.compile(
    r"--headless"                    # sans ecran du tout
    r"|--dump-dom|--screenshot|--print-to-pdf"   # rend la main sans montrer de fenetre
    r"|--user-data-dir"              # un profil a part : pas sa fenetre
    r"|--remote-debugging-port"      # un navigateur pilote de l'exterieur
    r"|\bxvfb-run\b|\bXvfb\b"        # un faux ecran
    r"|chrome-agents"                # le navigateur partage, separe du sien
    r"|CHROME_AGENTS_PORT",
    re.I)

# Les pilotes qui LANCENT leur propre navigateur, invisible par defaut.
# Se BRANCHER sur un navigateur deja ouvert reste permis (« connect »).
PILOTES = re.compile(r"\b(playwright|puppeteer|selenium)\b(?!.*\bconnect)", re.I)


def sans_les_textes(cmd):
    """Enleve les blocs de TEXTE de la commande, avant de la juger.

    Ecrire « --headless » dans un fichier n'est pas lancer un navigateur.
    Faute payee deux fois le 06/09/2026 : le garde refusait une commande qui
    ne faisait qu'ecrire ces mots dans un fichier de test.

    On enleve donc : les blocs colles (heredoc, « << FIN … FIN ») et les
    guillemets simples multi-lignes. Ce qui reste, c'est ce qui S'EXECUTE.
    """
    # les blocs colles : de « <<MARQUE » jusqu'a la ligne « MARQUE »
    for m in re.finditer(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?", cmd):
        marque = m.group(1)
        fin = re.search(r"^\s*" + re.escape(marque) + r"\s*$", cmd[m.end():], re.M)
        bout = cmd[m.end():m.end() + (fin.start() if fin else len(cmd))]
        cmd = cmd.replace(bout, " ")
    return cmd


def main():
    try:
        entree = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if entree.get("tool_name") != "Bash":
        sys.exit(0)
    cmd = sans_les_textes((entree.get("tool_input") or {}).get("command", ""))

    faute = CACHE.search(cmd) or PILOTES.search(cmd)
    if not faute:
        sys.exit(0)

    sys.stderr.write(
        "GARDE DU NAVIGATEUR — REFUS.\n\n"
        "Cette commande ouvre un navigateur CACHE — une fenetre que la personne ne\n"
        "verrait pas : « " + faute.group(0).strip() + " ».\n\n"
        "Deux raisons, toutes deux payees le 06/09/2026 : son navigateur s'est\n"
        "ouvert et ferme en boucle, et un Chrome sans fenetre a fait chauffer\n"
        "le PC en dessinant de la 3D a fond, sans que personne le voie.\n\n"
        "Ce qui reste permis :\n"
        "  - ouvrir une page A L'ECRAN chez lui : xdg-open <adresse>\n"
        "  - parler au navigateur DEJA ouvert : node ~/outils/nav.js …\n"
        "  - lire une page sans navigateur : curl -s <adresse>\n")
    sys.exit(2)


main()
