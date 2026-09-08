---
name: ovh
description: Modifier le DNS et le courrier de mon-site.example chez OVH — lire la zone, poser un enregistrement (A, AAAA, TXT, CAA, MX), activer la signature des e-mails (DKIM), refabriquer le jeton quand il est refuse. À invoquer dès que la personne parle de « DNS », « OVH », « sous-domaine », « DKIM », « SPF », « DMARC », « CAA », « IPv6 », « MX », ou quand un contrôle réclame un enregistrement DNS. Ne jamais répondre « je ne sais pas manipuler OVH ».
---

# Piloter OVH

**Règle absolue : on ne dit JAMAIS « je ne sais pas manipuler OVH ».**
Tout est ici. Si un mur se dresse, on le NOMME et on donne le geste qui l'ouvre.

## 1. Où sont les clefs

Elles ne sont **pas** dans un fichier. Elles sont dans le **coffre d'Odoo**,
dans la base **`tour`** (pas `controle-tour` — piège payé le 06/09/2026).

```sh
# Voir les noms des secrets (jamais les valeurs)
docker exec tour-db-1 psql -U odoo -d tour -tAc \
  "select id||' | '||name from vault_secret where name ~* 'ovh' order by write_date desc"
```

Le secret qui sert est **« OVH — API DNS (bascule) »**. Il contient trois
morceaux, en JSON : `AK` (la clef de l'application), `AS` (son secret),
`CK` (le jeton de consentement).

**Pour lire un secret depuis une coquille Odoo, il faut `--no-http`** :
sinon Odoo essaie d'ouvrir un port déjà pris et meurt sur
`OSError: [Errno 98] Address already in use`.

```sh
docker exec -i tour-odoo-1 odoo shell --no-http -d tour --db_host db \
  --db_user odoo --db_password "$(grep -m1 POSTGRES_PASSWORD ~/tour/.env | cut -d= -f2 | tr -d '"')" < prog.py
```

## 2. Le bon point d'entrée

`https://eu.api.ovh.com/1.0` — **Europe**. Rien d'autre.

Comment le savoir sans deviner : on essaie les trois et on lit le refus.
- Europe : « This **credential** is not valid » → l'application existe ici,
  c'est le **consentement** qui est mort.
- Canada / États-Unis : « This **application** key is invalid » → l'application
  n'existe pas là-bas.

**Deux messages différents = deux pannes différentes.** On les lit, on ne
les confond pas.

## 3. Comment on signe un appel

OVH veut une signature dans l'en-tête. La recette, exactement :

```
a_signer = AS + "+" + CK + "+" + METHODE + "+" + URL_COMPLETE + "+" + CORPS + "+" + HORODATAGE
signature = "$1$" + sha1(a_signer)
```

- `CORPS` est la chaîne vide quand il n'y a pas de corps (donc deux `+` collés).
- `HORODATAGE` se demande à OVH : `GET /auth/time` (pas l'heure de la machine).
- Les quatre en-têtes : `X-Ovh-Application`, `X-Ovh-Consumer`,
  `X-Ovh-Timestamp`, `X-Ovh-Signature`.

L'outil qui fait tout ça : **`~/outils/dns-ovh.py`** sur la tour.

## 4. Les gestes

```sh
python3 ~/outils/dns-ovh.py lire              # toute la zone
python3 ~/outils/dns-ovh.py lire TXT          # un seul type
python3 ~/outils/dns-ovh.py poser CAA @ '0 issue "letsencrypt.org"'
python3 ~/outils/dns-ovh.py poser AAAA @ 2001:41d0:305:2100::1:3ae4
python3 ~/outils/dns-ovh.py poser TXT _smtp._tls 'v=TLSRPTv1; rua=mailto:contact@mon-site.example'
python3 ~/outils/dns-ovh.py poser TXT _mta-sts 'v=STSv1; id=20260906000000'
python3 ~/outils/dns-ovh.py rafraichir        # SANS CECI, RIEN N'EST APPLIQUE
```

**`rafraichir` n'est pas optionnel.** Un enregistrement posé et non rafraîchi
n'existe pour personne. On vérifie ensuite avec `dig +short <type> <nom>`.

## 5. Quand le jeton est refusé

Message : `{"class":"Client::Forbidden","message":"This credential is not valid"}`

Ça veut dire : la clef d'application est bonne, **le consentement est mort**.
Un consentement se re-signe en **un clic**, connecté au compte OVH.

```sh
python3 ~/outils/ovh-nouveau-jeton.py demander   # fabrique l'adresse a cliquer
# -> montrer l'adresse a la personne avec ~/bin/ouvrir-page.sh
python3 ~/outils/ovh-nouveau-jeton.py finir      # range le jeton neuf dans le coffre
```

Le jeton demandé ne peut faire **que** ceci, et rien d'autre :
lire et écrire la zone `mon-site.example`, lire et écrire son courrier.
Pas les serveurs, pas la facturation, pas les autres domaines.

**C'est le SEUL moment où la main de la personne est nécessaire** — parce qu'il
faut être connecté à son compte OVH. Tout le reste se fait sans lui.

## 6. Le piège du joker

`mon-site.example` a un enregistrement **`*`** (joker) qui renvoie
**n'importe quel nom** vers `MON-SERVEUR`.

Donc : `alice.mon-site.example`, `nimportequoi-xyz.mon-site.example`,
tout répond — **sans que personne n'ait rien créé**.

**Ne jamais conclure « quelqu'un a créé ce sous-domaine ».** On vérifie
d'abord avec un nom inventé :

```sh
dig +short jenaijamaiscree-$RANDOM.mon-site.example
# si ca repond une adresse, c'est le joker, pas une creation
```

## 7. La signature des e-mails (DKIM)

DKIM ne se pose pas comme un simple enregistrement : c'est OVH qui fabrique
la paire de clefs, du côté du service de courrier.

```
GET  /email/domain/mon-site.example/dkim          # ce qui existe
POST /email/domain/mon-site.example/dkim          # en fabriquer un
```

Puis on vérifie : `dig +short TXT <selecteur>._domainkey.mon-site.example`

**Ordre à respecter, sinon les e-mails partent aux indésirables :**
1. DKIM signe vraiment (vérifié avec `dig`) ;
2. on attend une semaine de rapports DMARC ;
3. **seulement après**, on passe DMARC de `p=quarantine` à `p=reject`.

## 8. Ce qu'on ne fait jamais

- Recopier une clef dans un fichier, un message, ou un commit.
- Deviner un point d'entrée ou un nom de champ — on lit le refus.
- Poser un `AAAA` sans avoir vérifié que le serveur répond en IPv6 :
  les navigateurs essaient IPv6 **en premier**, et un IPv6 muet casse le site.
- Dire « je ne sais pas manipuler OVH ».

Compétences sœurs : [[eveil]] pour l'état réel avant d'agir,
[[jimmy]] pour la preuve avant de dire que c'est fait.
