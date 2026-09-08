#!/usr/bin/env python3
"""Porte a secrets — deterministe, aucune IA (doctrine Victor).

Elle lit ce qu'un outil s'apprete a faire et REFUSE si un secret y apparait
en clair. Une porte qui n'a jamais refuse ne garde rien : celle-ci refuse.

Payee deux fois :
  - 18/08/2026 : un jeton GitHub colle en clair dans une session, reste des
    heures dans la transcription.
  - 19/08/2026 : CINQ jetons distincts retrouves en clair sur la tour, dont
    deux dans des URL de remote git — qu'un simple `git remote -v` affiche.

Contrat du crochet PreToolUse : sortir 2 = BLOQUER l'outil, tout autre code =
laisser passer. Ce qui est ecrit sur la sortie d'erreur revient a l'agent.
"""
import json
import re
import sys

# Ce qu'on refuse de voir passer en clair. Chaque motif porte son nom, pour
# que le refus dise QUOI a ete vu, au lieu d'un vague « secret detecte ».
MOTIFS = [
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"), "jeton GitHub"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "jeton GitHub fin"),
    (re.compile(r"sk-ant-[A-Za-z0-9\-_]{20,}"), "cle Anthropic"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "cle OpenAI"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "cle AWS"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "cle privee"),
    (re.compile(r"https?://[^/\s:@]+:[^/\s@]{8,}@"), "mot de passe dans une URL"),
]

# Les seuls endroits ou un secret a le DROIT d'etre : c'est leur role meme.
LIEUX_LEGITIMES = (".git-credentials", "secrets-a-masquer.txt", "/.ssh/", ".env")


def ce_qui_va_etre_fait(donnees):
    """Le texte que l'outil s'apprete reellement a ecrire ou executer."""
    entree = donnees.get("tool_input") or {}
    morceaux = [entree[c] for c in
                ("command", "content", "new_string", "file_text", "prompt")
                if isinstance(entree.get(c), str)]
    return "\n".join(morceaux), str(entree.get("file_path") or "")


def main():
    try:
        donnees = json.load(sys.stdin)
    except Exception:
        # Une porte qui casse ne doit pas bloquer le travail. Mais elle ne
        # pretend pas non plus avoir verifie : elle se tait et laisse passer.
        return 0

    texte, chemin = ce_qui_va_etre_fait(donnees)
    if not texte:
        return 0
    if any(lieu in chemin for lieu in LIEUX_LEGITIMES):
        return 0

    vus = [nom for motif, nom in MOTIFS if motif.search(texte)]
    if not vus:
        return 0

    sys.stderr.write(
        "PORTE A SECRETS — REFUSE.\n\n"
        "Ce que tu allais faire contient en clair : %s.\n\n"
        "Ne recolle pas la valeur. Trois gestes possibles :\n"
        "  1. passe par le magasin git (~/.git-credentials, deja en place) ;\n"
        "  2. lis la valeur depuis le Coffre au lieu de l'ecrire ;\n"
        "  3. mets-la dans une variable d'environnement, jamais dans le texte.\n\n"
        "Si cette valeur a DEJA ete exposee, elle est brulee : il faut la\n"
        "REVOQUER, pas la cacher.\n" % ", ".join(vus))
    return 2


if __name__ == "__main__":
    sys.exit(main())
