#!/usr/bin/env python3
# GARDE DES MISES A JOUR — demande de la personne, 21/08/2026.
#
# « Un garde-fou sur les mises a jour d'opencode et les tiennes ; il verifie
#   qu'aucun binaire ni communication reseau n'a ete ajoute. »
#
# POURQUOI. Une mise a jour est le moment ideal pour glisser quelque chose :
# le fichier change de toute facon, personne ne relit, et l'outil tourne deja
# avec toutes les permissions de la personne — ses clefs, ses fichiers, son reseau.
# Un outil qui se met a jour tout seul est une porte ouverte une fois par
# semaine.
#
# CE QU'IL FAIT. Il prend une EMPREINTE de l'installation :
#   - chaque fichier et sa somme de controle ;
#   - chaque PROGRAMME EXECUTABLE (un fichier compile, illisible pour un
#     humain — on ne peut pas savoir ce qu'il fait en le lisant) ;
#   - chaque ADRESSE INTERNET ecrite dans le code ;
#   - chaque MOYEN D'APPELER LE RESEAU (les mots du langage qui ouvrent une
#     connexion : fetch, http, net, WebSocket, dns, curl, wget...).
# A la fois suivante, il compare et CRIE sur ce qui est APPARU. Ce qui
# disparait ne l'interesse pas : on ne se fait pas attaquer par une soustraction.
#
# CE QU'IL N'EST PAS. Il ne dit pas « c'est un virus ». Il dit « ceci est
# nouveau, regarde ». La decision reste a la personne.
#
# Usage :
#   python3 garde-mises-a-jour.py                      # controle les deux outils
#   python3 garde-mises-a-jour.py --racine X --nom Y   # controle un dossier
#   python3 garde-mises-a-jour.py --accepter           # apres verification,
#                                                      # enregistre l'etat neuf
import argparse, hashlib, json, os, re, sys

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

# MAISON = le dossier personnel de celui qui lance le garde. On ne l'ecrit
# jamais en dur : ainsi le garde marche sur n'importe quelle machine.
MAISON = os.path.expanduser("~")
PORTES = os.path.join(MAISON, ".claude/portes")
EMPREINTES = os.path.join(PORTES, "empreintes-outils.json")

# Les deux outils surveilles par defaut.
# On surveille TOUT l'arbre, pas seulement le programme lance : une mise a
# jour ajoute ses affaires dans les dossiers voisins (node_modules), et c'est
# la qu'un paquet de trop passerait inapercu.
CANDIDATS = {
    "claude-code": ["/usr/local/lib/node_modules/@anthropic-ai/claude-code",
                    os.path.join(MAISON, ".local/share/claude"),
                    os.path.join(MAISON, ".claude/local")],
    "opencode": [os.path.join(MAISON, ".opencode"),
                 "/usr/local/lib/node_modules/opencode-ai",
                 os.path.join(MAISON, ".local/share/opencode/bin")],
}
OUTILS = {nom: next((c for c in chemins if os.path.isdir(c)), chemins[0])
          for nom, chemins in CANDIDATS.items()}

# Ce qui bouge a chaque seconde et n'a rien a voir avec une mise a jour :
# journaux, bases de travail, caches. Les surveiller ferait crier le garde
# tout le temps — et un garde qui crie toujours ne se lit plus.
IGNORES = re.compile(r"(^|/)(\.git|logs?|tmp|cache|\.cache|node_modules/\.cache)(/|$)"
                     r"|\.(log|db|db-wal|db-shm|sock|pid)$")

# Un fichier de code qu'on sait lire.
LISIBLES = (".js", ".mjs", ".cjs", ".ts", ".tsx", ".json", ".sh", ".py", ".md")
# Trop gros pour etre lu ligne a ligne sans tout ralentir.
TAILLE_LECTURE_MAX = 12 * 1024 * 1024

# Les mots qui ouvrent une connexion vers l'exterieur.
MOYENS_RESEAU = [
    "fetch(", "XMLHttpRequest", "WebSocket", "require('net')", 'require("net")',
    "require('http')", 'require("http")', "require('https')", 'require("https")',
    "require('dgram')", 'require("dgram")', "require('dns')", 'require("dns")',
    "node:net", "node:http", "node:dgram", "node:dns", "child_process",
    "curl ", "wget ", "nc -", "socket.connect", "urllib", "requests.get",
    "requests.post",
]
ADRESSE = re.compile(r"https?://([A-Za-z0-9.-]+\.[A-Za-z]{2,})", re.I)
# Un programme execute commence par ces quelques octets, ou porte le droit
# d'etre lance.
SIGNATURES = (b"\x7fELF", b"MZ", b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xce")


def est_programme(chemin):
    try:
        with open(chemin, "rb") as f:
            tete = f.read(4)
    except OSError:
        return False
    if tete[:4] in SIGNATURES or tete[:2] == b"MZ":
        return True
    return os.access(chemin, os.X_OK) and not chemin.endswith(LISIBLES)


def relever(racine):
    """Rend l'empreinte d'une installation."""
    fichiers, programmes, adresses, moyens = {}, [], set(), set()
    for dossier, _, noms in os.walk(racine):
        for nom in sorted(noms):
            chemin = os.path.join(dossier, nom)
            if os.path.islink(chemin) or not os.path.isfile(chemin):
                continue
            court = os.path.relpath(chemin, racine)
            if IGNORES.search(court):
                continue
            try:
                taille = os.path.getsize(chemin)
                with open(chemin, "rb") as f:
                    somme = hashlib.sha256()
                    for bloc in iter(lambda: f.read(1 << 20), b""):
                        somme.update(bloc)
                fichiers[court] = somme.hexdigest()[:16]
            except OSError:
                continue
            if est_programme(chemin):
                programmes.append(court)
            if taille <= TAILLE_LECTURE_MAX:
                try:
                    texte = open(chemin, "r", encoding="utf-8",
                                 errors="ignore").read()
                except OSError:
                    continue
                for m in ADRESSE.finditer(texte):
                    adresses.add(m.group(1).lower())
                for mot in MOYENS_RESEAU:
                    if mot in texte:
                        moyens.add(mot)
    return {"fichiers": fichiers, "programmes": sorted(programmes),
            "adresses": sorted(adresses), "moyens": sorted(moyens)}


def comparer(nom, avant, apres):
    """Rend la liste des choses APPARUES. Ce qui disparait n'alerte pas."""
    cris = []
    neufs = [p for p in apres["programmes"] if p not in avant["programmes"]]
    if neufs:
        cris.append("PROGRAMME AJOUTE (%d) : %s" % (len(neufs), ", ".join(neufs[:12])))
    na = [a for a in apres["adresses"] if a not in avant["adresses"]]
    if na:
        cris.append("ADRESSE AJOUTEE (%d) : %s" % (len(na), ", ".join(na[:12])))
    nm = [m for m in apres["moyens"] if m not in avant["moyens"]]
    if nm:
        cris.append("MOYEN RESEAU AJOUTE (%d) : %s" % (len(nm), ", ".join(nm[:12])))
    changes = [f for f, s in apres["fichiers"].items()
               if f in avant["fichiers"] and avant["fichiers"][f] != s]
    ajoutes = [f for f in apres["fichiers"] if f not in avant["fichiers"]]
    if changes or ajoutes:
        cris.append("FICHIERS : %d modifie(s), %d ajoute(s)"
                    % (len(changes), len(ajoutes)))
    return cris


def charger():
    try:
        return json.load(open(EMPREINTES, encoding="utf-8"))
    except Exception:
        return {}


def ranger(d):
    os.makedirs(os.path.dirname(EMPREINTES), exist_ok=True)
    json.dump(d, open(EMPREINTES, "w", encoding="utf-8"), ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--racine")
    ap.add_argument("--nom")
    ap.add_argument("--empreintes")
    ap.add_argument("--accepter", action="store_true")
    a = ap.parse_args()
    global EMPREINTES
    if a.empreintes:
        EMPREINTES = a.empreintes
    cibles = {a.nom or "cible": a.racine} if a.racine else OUTILS

    memoire = charger()
    alerte = False
    for nom, racine in cibles.items():
        if not racine or not os.path.isdir(racine):
            print("[%s] INTROUVABLE : %s" % (nom, racine))
            continue
        apres = relever(racine)
        avant = memoire.get(nom)
        if not avant:
            memoire[nom] = apres
            print("[%s] EMPREINTE POSEE : %d fichier(s), %d programme(s), "
                  "%d adresse(s) internet." % (nom, len(apres["fichiers"]),
                                               len(apres["programmes"]),
                                               len(apres["adresses"])))
            continue
        cris = comparer(nom, avant, apres)
        if not cris:
            print("[%s] AUCUN CHANGEMENT." % nom)
            continue
        alerte = True
        print("[%s] CHANGEMENTS DEPUIS LA DERNIERE FOIS :" % nom)
        for c in cris:
            print("   " + c)
        if a.accepter:
            memoire[nom] = apres
            print("   -> accepte : la nouvelle empreinte devient la reference.")
    ranger(memoire)
    if alerte and not a.accepter:
        print("\nRegarde ces ajouts. S'ils sont normaux, relance avec "
              "--accepter pour que le garde s'en souvienne.")
    sys.exit(0)


main()
