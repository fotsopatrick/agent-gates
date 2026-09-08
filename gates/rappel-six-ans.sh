#!/usr/bin/env bash
# rappel-six-ans.sh — garde-fou de la règle des six ans (demande du proprietaire).
# Branché sur UserPromptSubmit : ce texte est réinjecté dans le contexte de
# Claude À CHAQUE message. Un rappel en mémoire s'oublie ; celui-ci est
# mécanique — il tombe, que Claude le veuille ou non.
cat <<'FIN'
RÈGLE DES SIX ANS — garde-fou mécanique, à appliquer à CETTE réponse :
- Chaque phrase doit se comprendre par un enfant de six ans, seule, sans relire l'échange.
- Chaque symbole, sigle, nom d'outil ou de commande est DÉCODÉ à l'endroit où il apparaît.
- Une commande donnée à la personne = chaque morceau expliqué + la preuve visible de réussite.
- Pas de jargon nu, pas de liste morte : finir sur la prochaine action.
FIN
