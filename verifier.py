#!/usr/bin/env python3
"""LE BANC D'ESSAI DU DEPOT PUBLIC.

Il refuse exactement les defauts trouves le 07/09/2026 dans le depot public
`control-tower` : un chemin ecrit en dur vers la machine de la personne, le meme
fichier recopie trois fois, une promesse de controle automatique sans controle
automatique, aucune description.

Il ne fait confiance a rien de ce que le README raconte. Il regarde le disque.
Usage :  python3 verifier.py [dossier]      (defaut : le dossier du script)
"""
import hashlib
import os
import re
import sys
from pathlib import Path

RACINE = Path(sys.argv[1] if len(sys.argv) > 1 else __file__).resolve()
RACINE = RACINE if RACINE.is_dir() else RACINE.parent
RES = []


def controle(nom, passe, detail):
    RES.append((nom, passe, detail))
    print(("  VERT  " if passe else "  ROUGE ") + nom)
    print("        " + detail)


def fichiers():
    for p in RACINE.rglob("*"):
        if p.is_file() and ".git/" not in str(p) and "/.git" not in str(p):
            yield p


# --- 1. le depot existe et il est suivi par git ---------------------------
controle("Le depot existe et git le suit",
         (RACINE / ".git").exists(),
         f"dossier : {RACINE}")

# --- 2. il contient les trois choses promises -----------------------------
for quoi, mini in (("gates", 8), ("circuits", 3), ("skills", 8)):
    d = RACINE / quoi
    n = sum(len(list(d.rglob("*." + e))) for e in ("py", "sh", "md", "json")) \
        if d.is_dir() else 0
    controle(f"Le dossier {quoi} contient au moins {mini} fichiers",
             n >= mini, f"trouve : {n}")

# --- 3. aucun secret ------------------------------------------------------
SECRETS = re.compile(
    r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|"
    r"AKIA[0-9A-Z]{12,}|BEGIN (RSA |OPENSSH )?PRIVATE KEY|"
    r"AIza[0-9A-Za-z_-]{30,}")
trouves = []
for p in fichiers():
    try:
        t = p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    if SECRETS.search(t):
        trouves.append(str(p.relative_to(RACINE)))
controle("Aucun secret dans aucun fichier", not trouves,
         "propre" if not trouves else "SECRET dans : " + ", ".join(trouves[:5]))

# --- 4. aucun chemin ecrit en dur vers la machine de la personne --------------
DUR = re.compile(r"~|~|192\.168\.1\.\d+|145\.239\.77\.232|"
                 r"tour-vps|matourdecontrole")
dur = []
for p in fichiers():
    if p.name == "verifier.py":
        continue
    try:
        t = p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    if DUR.search(t):
        dur.append(str(p.relative_to(RACINE)))
controle("Aucun chemin ni adresse de la maison", not dur,
         "propre" if not dur else f"{len(dur)} fichier(s) : " + ", ".join(dur[:5]))

# --- 5. aucun fichier recopie a l'identique ------------------------------
vus, doubles = {}, []
for p in fichiers():
    try:
        e = hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        continue
    if e in vus:
        doubles.append(f"{p.relative_to(RACINE)} = {vus[e]}")
    else:
        vus[e] = str(p.relative_to(RACINE))
controle("Aucun fichier recopie a l'identique", not doubles,
         "propre" if not doubles else "doublons : " + " | ".join(doubles[:4]))

# --- 6. le README dit comment s'en servir --------------------------------
r = RACINE / "README.md"
t = r.read_text(encoding="utf-8", errors="ignore") if r.is_file() else ""
controle("Le README existe et explique comment lancer",
         bool(t) and re.search(r"(?i)\b(install|usage|run|quick ?start|getting started)\b", t) is not None,
         f"{len(t)} caracteres" if t else "ABSENT")

# --- 7. une licence ------------------------------------------------------
controle("Une licence est presente",
         any((RACINE / n).is_file() for n in ("LICENSE", "LICENSE.md", "LICENCE.md")),
         "oui" if any((RACINE / n).is_file() for n in ("LICENSE", "LICENSE.md", "LICENCE.md")) else "ABSENTE")

# --- 8. un controle automatique qui lance VRAIMENT ce banc d'essai -------
flux = list((RACINE / ".github/workflows").glob("*.yml")) + \
       list((RACINE / ".github/workflows").glob("*.yaml"))
lance = any("verifier.py" in f.read_text(encoding="utf-8", errors="ignore")
            for f in flux)
controle("Un controle automatique lance ce banc d'essai a chaque envoi",
         lance,
         f"{len(flux)} fichier(s) de controle, verifier.py lance : {lance}")

# --- 9. chaque garde a son test ------------------------------------------
g = RACINE / "gates"
sans = []
if g.is_dir():
    for p in sorted(g.glob("*.py")):
        base = p.stem
        if not list((RACINE / "tests").glob(f"*{base}*")):
            sans.append(base)
controle("Chaque garde a son test (un garde sans refus prouve est une promesse)",
         not sans, "tous testes" if not sans else "sans test : " + ", ".join(sans[:6]))

# --- verdict -------------------------------------------------------------
v = sum(1 for _, p, _ in RES if p)
r_ = len(RES) - v
print("-" * 66)
print(f"RESULTAT : {v} vert / {r_} rouge sur {len(RES)} controles")
sys.exit(0 if r_ == 0 else 1)
