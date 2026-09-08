#!/usr/bin/env python3
"""Garde de l'existant — deterministe, aucune IA (doctrine le gardien).

CE QU'ELLE EMPECHE. Fabriquer une deuxieme fois une chose qui existe deja :
une page de la vitrine, un outil, une competence. Nee d'une faute reelle du
06/09/2026 : la personne a du demander « t'es alle creer de nouvelles etudes ? »
parce que rien ne verifiait l'existant avant d'ecrire.

CE QU'ELLE FAIT. Avant un Write (ou une commande qui pose un fichier sur la
tour), elle prend le nom du fichier et le cherche a trois endroits :
  1. la carte vivante   (~/outils/carte-tour.py)
  2. le poste local     (~/outils, ~/.claude/skills, ~/livrables)
  3. la tour            (la liste des pages de vitrine/prod, gardee en cache)
Si le meme nom existe DEJA AILLEURS, elle refuse et dit ou elle l'a vu.

CE QU'ELLE LAISSE PASSER. Ecrire au meme endroit (c'est une mise a jour), un
nom neuf, un fichier de travail (brouillon, sauvegarde, test), et tout ce qui
n'est ni une page, ni un outil, ni une competence.

Contrat du crochet PreToolUse : sortir 2 = BLOQUER, tout autre code = laisser
passer. Ce qui est ecrit sur la sortie d'erreur revient a l'agent.
"""
import json
import os
import re
import subprocess
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
CACHE = os.path.join(MAISON, ".claude/portes/cache-tour-vitrine.txt")
AGE_CACHE = 3600  # une heure

# Les trois familles surveillees. Tout le reste passe sans rien demander.
FAMILLES = (
    ("une page de la vitrine", re.compile(r"^(etude|article|page)-[a-z0-9-]+$")),
    ("un outil",               re.compile(r"^[a-z0-9-]+\.(py|sh|js)$")),
    ("une competence",         re.compile(r"^SKILL\.md$")),
)

# Ce qui n'est jamais un doublon : brouillons, sauvegardes, essais.
JAMAIS = re.compile(
    r"(\.avant|\.bak|\.tmp|\.orig|~$|/tmp/|scratchpad|"
    r"sauvegarde|brouillon|^test-|-test$|\.test\.)", re.I)


def nom_cherche(chemin):
    """Le nom a chercher : le fichier, sans extension ni suffixe de langue.

    Pour une competence, c'est le nom du DOSSIER (SKILL.md est toujours
    pareil) — ~/.claude/skills/navigateur/SKILL.md donne « navigateur »."""
    base = os.path.basename(chemin)
    if base == "SKILL.md":
        return os.path.basename(os.path.dirname(chemin)), "une competence"
    for quoi, motif in FAMILLES:
        if motif.match(base) or motif.match(os.path.splitext(base)[0]):
            # ON GARDE LE SUFFIXE DE LANGUE. Faute payee le 06/09/2026 : on
            # l'enlevait, et « etude-dogwof-en » etait pris pour un doublon de
            # « etude-dogwof ». Une traduction n'est pas un doublon : c'est une
            # AUTRE page, avec son adresse et son texte.
            return os.path.splitext(base)[0], quoi
    return None, None


def liste_tour():
    """Les noms de pages servies par la vitrine. Gardee en cache une heure :
    ouvrir la tour prend plusieurs secondes, un crochet doit etre rapide."""
    try:
        if os.path.exists(CACHE) and time.time() - os.path.getmtime(CACHE) < AGE_CACHE:
            return open(CACHE, encoding="utf-8").read().split("\n")
    except OSError:
        pass
    env = dict(os.environ, SSH_AUTH_SOCK=os.path.join(MAISON, ".ssh/agent.sock"))
    try:
        r = subprocess.run(
            ["ssh", "-o", "IdentityAgent=" + os.path.join(MAISON, ".ssh/agent.sock"),
             "-o", "ConnectTimeout=6", "mon-serveur",
             "ls ~/vitrine/prod | grep -vE '\\.avant|\\.bak'"],
            capture_output=True, text=True, timeout=20, env=env)
        if r.returncode == 0 and r.stdout.strip():
            os.makedirs(os.path.dirname(CACHE), exist_ok=True)
            open(CACHE, "w", encoding="utf-8").write(r.stdout)
            return r.stdout.split("\n")
    except Exception:
        pass
    # La tour ne repond pas : on ne bloque pas sur une absence de reponse.
    return []


def deja_vu(nom, chemin_vise):
    """Rend la liste des endroits ou ce nom existe deja, AILLEURS."""
    trouve = []
    vise = os.path.realpath(os.path.expanduser(chemin_vise))

    # 1. le poste local
    for dossier in ("outils", ".claude/skills", "livrables", "vitrine"):
        d = os.path.join(MAISON, dossier)
        if not os.path.isdir(d):
            continue
        for racine, dirs, fichiers in os.walk(d):
            dirs[:] = [x for x in dirs if not x.startswith(".") and x != "node_modules"]
            if os.path.basename(racine) == nom and racine != os.path.dirname(vise):
                trouve.append("sur ce poste : " + racine.replace(MAISON, "~"))
            for f in fichiers:
                if os.path.splitext(f)[0] == nom:
                    p = os.path.join(racine, f)
                    if os.path.realpath(p) != vise and not JAMAIS.search(p):
                        trouve.append("sur ce poste : " + p.replace(MAISON, "~"))
            if len(trouve) > 6:
                return trouve

    # 2. la tour
    for f in liste_tour():
        if f and os.path.splitext(f.strip())[0] == nom:
            trouve.append("sur la tour : vitrine/prod/" + f.strip())

    # 3. la carte vivante
    carte = os.path.join(MAISON, "outils", "carte-tour.py")
    if os.path.exists(carte):
        try:
            r = subprocess.run(["python3", carte, nom],
                               capture_output=True, text=True, timeout=25)
            for ligne in r.stdout.split("\n"):
                if ligne.strip().startswith("·") and nom.lower() in ligne.lower():
                    trouve.append("dans la carte vivante :" + ligne.split("]", 1)[-1][:90])
        except Exception:
            pass

    # on ne repete pas deux fois le meme endroit
    vus, propre = set(), []
    for t in trouve:
        if t not in vus:
            vus.add(t); propre.append(t)
    return propre


def chemins_vises(entree):
    outil = entree.get("tool_name", "")
    e = entree.get("tool_input", {}) or {}
    if outil == "Write":
        p = e.get("file_path", "")
        return [p] if p else []
    if outil == "Bash":
        cmd = e.get("command", "")
        # ON NE PREND QUE LA CIBLE D'UNE ECRITURE. Deux fautes payees le
        # 06/09/2026 : (1) le garde refusait une commande qui se contentait de
        # LIRE un outil, parce que son nom apparaissait dans la ligne ;
        # (2) « 2>/dev/null » etait pris pour une ecriture. On cherche donc les
        # cibles reelles : « cp X Y », « mv X Y », « install … Y », « > Y »,
        # « tee Y » — et jamais /dev/null.
        cibles = []
        for m in re.finditer(r"(?:^|[;&|]\s*)(?:cp|mv|install|scp)\s+(?:-\S+\s+)*"
                             r"\S+\s+(\S+)", cmd):
            cibles.append(m.group(1))
        for m in re.finditer(r"(?<![0-9&])>{1,2}\s*(\S+)", cmd):
            cibles.append(m.group(1))
        for m in re.finditer(r"\btee\s+(?:-\S+\s+)*(\S+)", cmd):
            cibles.append(m.group(1))
        garde = []
        for c in cibles:
            c = c.strip("\"'")
            if c.startswith("/dev/") or ":" in c:
                continue
            if re.search(r"/(vitrine/prod|\.claude/skills|outils)/", c):
                garde.append(c)
        return garde
    return []


def main():
    try:
        entree = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    for chemin in chemins_vises(entree):
        if JAMAIS.search(chemin):
            continue
        # ecrire au meme endroit = mise a jour, jamais un doublon
        if os.path.exists(os.path.expanduser(chemin)):
            continue
        nom, quoi = nom_cherche(chemin)
        if not nom:
            continue
        endroits = deja_vu(nom, chemin)
        if endroits:
            sys.stderr.write(
                "GARDE DE L'EXISTANT — REFUS.\n\n"
                "Tu vas creer " + quoi + " nommee « " + nom + " ».\n"
                "Elle existe DEJA ici :\n  - "
                + "\n  - ".join(endroits[:6]) + "\n\n"
                "Ne fabrique pas une deuxieme fois ce qui existe. Ouvre "
                "l'existant et modifie-le, ou choisis un autre nom si c'est "
                "vraiment une chose differente — et dis a la personne en quoi.\n")
            sys.exit(2)
    sys.exit(0)


main()
