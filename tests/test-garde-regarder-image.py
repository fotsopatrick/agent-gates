#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Le garde « regarde l'image » fait-il son travail ?

Un garde qui n'a jamais refuse ne garde rien. On lui joue donc quatre
situations, avec un faux journal, et on verifie qu'il bloque exactement
celles qu'il doit bloquer.

Lancer :  python3 ~/.claude/portes/test-garde-regarder-image.py
Reussi quand la derniere ligne dit : LE GARDE FAIT SON TRAVAIL
"""
import json
import os
import subprocess
import sys
import tempfile

GARDE = os.path.expanduser("~/.claude/portes/garde-regarder-image.py")


def journal(evenements):
    """Ecrit un faux journal de conversation et rend son chemin."""
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False,
                                    encoding="utf-8")
    for e in evenements:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
    f.close()
    return f.name


def message_patrick(texte):
    return {"type": "user", "message": {"role": "user", "content": texte}}


def fabrique_image(cmd):
    return {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Bash", "input": {"command": cmd}}]}}


def regarde_image(chemin):
    return {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Read", "input": {"file_path": chemin}}]}}


def dit(texte):
    return {"type": "assistant", "message": {"content": [
        {"type": "text", "text": texte}]}}


def juge(evenements):
    """Rend True si le garde BLOQUE."""
    chemin = journal(evenements)
    entree = json.dumps({"transcript_path": chemin, "stop_hook_active": False})
    r = subprocess.run([sys.executable, GARDE], input=entree,
                       capture_output=True, text=True)
    os.unlink(chemin)
    return r.returncode == 2


CAS = [
    ("il fabrique, ne regarde pas, et vante l'image  -> DOIT BLOQUER", True, [
        message_patrick("fais-moi la fontaine"),
        fabrique_image("blender -b -P blender/planche.py"),
        dit("Regarde l'image : la fontaine est bien fabriquee."),
    ]),
    ("il fabrique ET regarde l'image                 -> doit passer", False, [
        message_patrick("fais-moi la fontaine"),
        fabrique_image("blender -b -P blender/planche.py"),
        regarde_image("/tmp/demo-home/labo-3d/blender/apercus/fontaine.png"),
        dit("Regarde l'image : ce n'est pas une fontaine, ce sont quatre murs."),
    ]),
    ("il fabrique et n'affirme rien sur l'aspect     -> doit passer", False, [
        message_patrick("fabrique le fichier"),
        fabrique_image("blender -b -P blender/planche.py"),
        dit("Le fichier est ecrit : 46 176 octets. Je ne l'ai pas encore ouvert."),
    ]),
    ("il parle DU garde lui-meme                    -> doit passer", False, [
        message_patrick("pose le garde des images"),
        fabrique_image("python3 ~/.claude/portes/test-garde-regarder-image.py"),
        dit("Regarde : le garde bloque bien la mauvaise capture d ecran."),
    ]),
    ("aucune image fabriquee                         -> doit passer", False, [
        message_patrick("range les dossiers"),
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {"command": "ls ~"}}]}},
        dit("Voila la liste, tout est range."),
    ]),
]


def main():
    rate = 0
    for titre, doit_bloquer, evs in CAS:
        bloque = juge(evs)
        ok = bloque == doit_bloquer
        if not ok:
            rate += 1
        print("  %-5s %s" % ("OK" if ok else "RATE", titre))
    print()
    if rate:
        print("  %d CAS SUR %d ECHOUE(NT) — le garde ne garde pas\n"
              % (rate, len(CAS)))
        return 1
    print("  LE GARDE FAIT SON TRAVAIL\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
