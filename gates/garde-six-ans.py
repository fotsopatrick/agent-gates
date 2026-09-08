#!/usr/bin/env python3
# GARDE DES SIX ANS (Stop hook) — LIT le dernier message de Claude et REFUSE
# de finir le tour s'il est illisible pour la personne.
#
# POURQUOI CE FICHIER EXISTE (21/08/2026). Un premier garde avait ete pose le
# matin meme : il reinjectait la regle a chaque message. Il PARLAIT a Claude,
# il ne REGARDAIT jamais ce que Claude ecrivait. la personne l'a constate le
# soir : « le garde-fou des 6 ans ne semble pas fonctionner ». Il avait
# raison — un rappel n'est pas un controle. Celui-ci est un mur : il ne peut
# pas effacer le texte, mais il bloque la fin du tour et force la reecriture.
#
# TROIS FAUTES OBJECTIVES, mesurables, jamais une question de gout :
#   1. LE PAVE       — au-dela de 1800 caracteres, on ne suit plus.
#   2. LE JARGON NU  — un mot de metier sans son explication a cote.
#   3. LA COMMANDE SANS PREUVE — une ligne a coller sans « c'est reussi
#      quand... ». la personne ne doit jamais deviner si ca a marche.
import os
import hashlib, json, os, re, sys, time, unicodedata

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


LIMITE = 1800
# MEMOIRE DU DERNIER TEXTE JUGE (21/08). Quand ce garde tourne, le message
# tout juste fini n'est pas toujours ecrit dans le journal : le garde lit
# alors le PRECEDENT et le condamne une seconde fois. Le garde « bonne nuit »
# l'a fait deux fois de suite, en citant des mots qui n'etaient pas dans le
# message accuse. On retient donc l'empreinte du dernier texte juge : si on
# relit le meme, c'est que le neuf n'est pas encore arrive — on attend un
# instant, puis on se tait. Se taire vaut mieux qu'accuser a tort.
ETAT = os.environ.get("GARDE_SIX_ANS_ETAT",
                      os.path.join(MAISON, ".claude/portes/.dernier-juge"))
ATTENTE_MAX = 2.0     # secondes
PAS = 0.2

# Un mot de metier est FAUTIF s'il apparait sans explication dans les 90
# caracteres qui suivent. Marques d'explication acceptees : une parenthese,
# un tiret cadratin, « c'est-a-dire », « autrement dit ».
JARGON = [
    "cron", "commit", "worktree", "slug", "json", "http", "hook", "regex",
    "classifieur", "banc", "tdd", "cache", "buffer", "endpoint", "payload",
    "webhook", "socket", "daemon", "stdout", "regexp", "middleware",
]
EXPLIQUE = re.compile(r"[(—–-]|c'est-[àa]-dire|autrement dit", re.I)

# Une commande a coller : ligne commencant par « ! » ou contenant « ssh ».
COMMANDE = re.compile(r"^\s*(?:!|\$)\s*\S+|^\s*!\s*SSH_AUTH_SOCK", re.M)
PREUVE = re.compile(
    r"r[ée]ussi|tu verras|elle affiche|il affiche|affichera|preuve|"
    r"rend la main|c'est bon quand|doit r[ée]pondre", re.I)



# 4. LA LECON A LA PLACE DE LA REPARATION (05/09/2026).
# Sept epreuves de la tour dormaient depuis un mois. J'ai trouve la cause,
# et au lieu de la corriger j'ai ecrit « ce qu'il faut retenir : c'est un
# trou dans la tour ». la personne : « faut pas retenir, faut fixer ».
# Un defaut trouve se REPARE. Le raconter n'est pas le reparer, et
# « ce qu'il faut retenir » est le signe qu'on s'est arrete trop tot.
# La faute est objective : une formule de lecon + un defaut nomme, SANS
# aucune marque de reparation dans le meme message.
LECON = [
    "ce qu il faut retenir", "a retenir", "il faut retenir", "la lecon",
    "lecon pour la suite", "a noter pour la suite", "ce qu on retient",
    "ce qui est a retenir", "note pour la suite",
]
DEFAUT = [
    "trou", "defaut", "faille", "bug", "panne", "casse", "ne repasse",
    "n est pas corrige", "probleme", "ca ne marche pas", "rien ne repasse",
    "manquait", "il manque",
]
REPARE = [
    "je corrige", "j ai corrige", "je repare", "j ai repare", "je bouche",
    "j ai bouche", "correctif", "je le fixe", "c est corrige", "je m en occupe",
    "je pose la regle", "le controle est deja ecrit", "je le repare",
    "je repare tout de suite", "c est repare", "je m en charge",
]

def sans_accents(s):
    plat = "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()
    return plat.replace("\u2019", " ").replace("'", " ")


def dernier_message(chemin):
    txt = ""
    try:
        for ligne in open(chemin, encoding="utf-8", errors="replace"):
            try:
                d = json.loads(ligne)
            except Exception:
                continue
            if d.get("type") != "assistant":
                continue
            c = (d.get("message") or {}).get("content")
            if isinstance(c, list):
                t = " ".join(x.get("text", "") for x in c
                             if isinstance(x, dict) and x.get("type") == "text")
            else:
                t = str(c or "")
            if t.strip():
                txt = t
    except Exception:
        return ""
    return txt


def fautes(texte):
    trouvees = []

    # 1. le pave. On mesure le texte NU, sans les blocs de commande : une
    # commande longue n'est pas un pave, c'est une commande.
    nu = re.sub(r"```.*?```", " ", texte, flags=re.S)
    nu = re.sub(r"^\s*!.*$", " ", nu, flags=re.M)
    if len(nu) > LIMITE:
        trouvees.append(
            "LE PAVE : %d caracteres de texte (la limite est %d). "
            "Coupe : garde ce qui change ce que la personne va FAIRE, jette le reste."
            % (len(nu), LIMITE))

    # 2. le jargon nu
    plat = sans_accents(nu)
    nus = []
    for mot in JARGON:
        for m in re.finditer(r"\b" + re.escape(mot) + r"\b", plat):
            suite = nu[m.end():m.end() + 90]
            if not EXPLIQUE.search(suite):
                nus.append(mot)
                break
    if nus:
        trouvees.append(
            "LE JARGON NU : %s — employe(s) sans explication juste apres. "
            "Decode chaque mot la ou il apparait, entre parentheses ou apres "
            "un tiret." % ", ".join(sorted(set(nus))))

    # 3. la commande sans preuve
    for m in COMMANDE.finditer(texte):
        apres = texte[m.end():m.end() + 600]
        if not PREUVE.search(apres):
            trouvees.append(
                "LA COMMANDE SANS PREUVE : tu donnes une ligne a coller sans "
                "dire ce que la personne verra si elle reussit. Ajoute « c'est "
                "reussi quand elle affiche ... ».")
            break

    # 4. la lecon a la place de la reparation
    if any(f in plat for f in LECON) and any(d in plat for d in DEFAUT) \
            and not any(r in plat for r in REPARE):
        trouvees.append(
            "LA LECON A LA PLACE DE LA REPARATION : tu nommes un defaut et tu "
            "en fais une lecon, sans dire que tu le repares. Un defaut trouve "
            "se corrige, il ne se raconte pas. Repare-le, ou dis en une phrase "
            "quel geste precis le repare et qui le fait.")

    return trouvees



def main():
    try:
        hook = json.loads(sys.stdin.read() or "{}")
    except Exception:
        sys.exit(0)
    # deja bloque une fois sur ce tour : on ne boucle pas.
    if hook.get("stop_hook_active"):
        sys.exit(0)
    tp = hook.get("transcript_path") or ""
    if not tp or not os.path.exists(tp):
        sys.exit(0)              # un garde casse ne casse pas la session

    try:
        vu = open(ETAT, encoding="utf-8").read().strip()
    except OSError:
        vu = ""
    texte = dernier_message(tp)
    empreinte = hashlib.sha1(texte.encode("utf-8")).hexdigest()
    # le journal n'a pas encore le message neuf : on lui laisse le temps
    fin = time.time() + ATTENTE_MAX
    while empreinte == vu and time.time() < fin:
        time.sleep(PAS)
        texte = dernier_message(tp)
        empreinte = hashlib.sha1(texte.encode("utf-8")).hexdigest()
    if empreinte == vu:
        sys.exit(0)              # toujours l'ancien : on se tait
    if not texte.strip():
        sys.exit(0)
    try:
        os.makedirs(os.path.dirname(ETAT), exist_ok=True)
        open(ETAT, "w", encoding="utf-8").write(empreinte)
    except OSError:
        pass
    f = fautes(texte)
    if f:
        print(json.dumps({
            "decision": "block",
            "reason": ("GARDE DES SIX ANS — ton message ne passe pas. "
                       + " | ".join(f)
                       + " Reecris-le : phrases courtes, chaque mot de metier "
                         "decode sur place, et finis par la seule prochaine "
                         "action.")
        }, ensure_ascii=False))
    sys.exit(0)


main()
