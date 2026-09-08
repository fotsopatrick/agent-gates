#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GARDE DES LIENS MORTS — on ne promet pas une adresse qui n'existe pas.

NE D'UNE FAUTE REELLE (08/09/2026). J'ai ecrit une page qui annoncait un
depot public. L'adresse rendait 404 — introuvable. Le Sage n'a rien vu :
il fait lire cinq endroits, tous sur le DISQUE, aucun ne regarde dehors.
Mon propre banc d'essai ne verifiait pas non plus. C'est la personne qui
l'a trouve, en cliquant.

Une page peut etre vraie ligne par ligne et fausse dans sa promesse.

CE QU'IL FAIT : quand on ECRIT un fichier qui se lit (page, mode d'emploi,
note), il releve les adresses web annoncees et verifie qu'elles repondent.
Une adresse morte = refus.

CE QU'IL NE FAIT PAS, ET C'EST VOULU :
  - il ne touche pas au code (.py, .js, .sh) : une adresse dans du code est
    souvent un exemple ou une chaine construite ;
  - il laisse passer les adresses d'exemple et les adresses locales : elles
    ne promettent rien a personne ;
  - si le RESEAU est coupe, il se tait. Un garde qui empeche de travailler
    dans le train est un garde rate ;
  - il s'arrete vite (3 secondes par adresse, 5 adresses au plus).
"""
import json, re, sys, os

# LES REGLES SE CHOISISSENT. Posez un « regles.json » a cote de ce garde,
# ou donnez son chemin dans GARDE_REGLES.
def charger_regles(defaut):
    chemin = os.environ.get("GARDE_REGLES") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "regles.json")
    try:
        perso = json.load(open(chemin, encoding="utf-8"))
    except Exception:
        return defaut
    if not isinstance(perso, dict):
        return defaut
    sortie = dict(defaut); sortie.update(perso); return sortie

R = charger_regles({
    "liens_extensions_verifiees": [".html", ".htm", ".md", ".txt", ".rst"],
    "liens_hotes_ignores": ["example.com", "example.org", "localhost",
                            "127.0.0.1", "0.0.0.0", "monsite.fr", "mon-site.fr"],
    "liens_maximum": 5,
    "liens_delai_secondes": 3,
})

ADRESSE = re.compile(r'https?://[^\s"\'<>)\]}\\]+')
PRIVEE = re.compile(r'^https?://(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)')

def texte_ecrit(ev):
    ti = ev.get("tool_input") or {}
    return " ".join(str(ti.get(k, "")) for k in ("content", "new_string", "command"))

def chemin_ecrit(ev):
    return str((ev.get("tool_input") or {}).get("file_path", ""))

def a_verifier(url):
    if PRIVEE.match(url):
        return False
    return not any(h in url for h in R["liens_hotes_ignores"])

def repond(url, delai):
    """Vrai si l'adresse repond. None si on n'a pas pu joindre le reseau —
    dans ce cas on se tait, on ne refuse pas."""
    import urllib.request, urllib.error
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "garde-lien-mort/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=delai) as r:
            return r.status < 400
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):          # le site refuse la question, pas la page
            return True
        return False
    except Exception:
        return None                        # reseau coupe, ou site injoignable

def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)                        # entree illisible : on ne bloque rien
    if not isinstance(ev, dict):
        sys.exit(0)

    chemin = chemin_ecrit(ev)
    if chemin and not any(chemin.lower().endswith(x)
                          for x in R["liens_extensions_verifiees"]):
        sys.exit(0)                        # ce n'est pas un fichier qui se lit

    urls = []
    for u in ADRESSE.findall(texte_ecrit(ev)):
        u = u.rstrip('.,;:')
        if a_verifier(u) and u not in urls:
            urls.append(u)
    urls = urls[: R["liens_maximum"]]
    if not urls:
        sys.exit(0)

    morts, joignable = [], False
    for u in urls:
        etat = repond(u, R["liens_delai_secondes"])
        if etat is None:
            continue
        joignable = True
        if etat is False:
            morts.append(u)

    if not joignable or not morts:
        sys.exit(0)                        # reseau coupe, ou tout repond

    print("GARDE DES LIENS MORTS — REFUS.\n", file=sys.stderr)
    print("Ce fichier annonce une adresse qui ne repond pas :\n", file=sys.stderr)
    for u in morts:
        print("  " + u, file=sys.stderr)
    print("\nUne page peut etre vraie ligne par ligne et fausse dans sa", file=sys.stderr)
    print("promesse. Ne publie pas une adresse qui n'existe pas encore.\n", file=sys.stderr)
    print("Trois gestes possibles :", file=sys.stderr)
    print("  1. cree la page a cette adresse AVANT de la promettre ;", file=sys.stderr)
    print("  2. enleve le lien tant qu'il n'existe pas ;", file=sys.stderr)
    print("  3. si c'est un exemple, ecris-le sur example.com.", file=sys.stderr)
    sys.exit(2)

main()
