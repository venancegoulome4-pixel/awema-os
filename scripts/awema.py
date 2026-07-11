#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""awema — opérateur de connexions multi-plateformes (CLI + agent /awema).

Gère les identifiants (clés / tokens / mots de passe) de chaque plateforme :
  • garde le DERNIER identifiant courant + un HISTORIQUE (liste) dans un fichier LOCAL
    .awema/credentials.json (gitignoré — JAMAIS poussé) ;
  • connaît les identifiants requis par plateforme (scripts/awema-connectors.json) ;
  • lance la procédure de connexion d'une plateforme avec ces identifiants ;
  • « incrémente » (rotation) un identifiant : le nouveau devient courant, l'ancien part en historique.

Conçu pour être piloté en langage naturel par la commande /awema (l'agent ne demande QUE
les valeurs inconnues à l'utilisateur), ou utilisé directement en CLI.

Commandes :
  awema list                         plateformes connues + état (identifiants présents ?)
  awema needs <plat> [--json]        identifiants requis + lesquels manquent
  awema set  <plat> KEY=VAL ...      enregistre/incrémente des identifiants (rotation + historique)
  awema set  <plat> KEY --stdin      lit la valeur (secrète) sur l'entrée standard
  awema get  <plat> [--reveal]       métadonnées (valeurs masquées) + taille d'historique
  awema env  <plat>                  lignes export/set pour utiliser les identifiants stockés
  awema connect <plat>               lance la connexion (avec les identifiants stockés)
  awema rotate  <plat> KEY=VAL       incrémente un identifiant (garde l'ancien en historique)
  awema history <plat> [--reveal]    historique des identifiants (masqué par défaut)
  awema setup [KEY=VAL ...]          personnalise l'agence (auto-hébergement) → config/agence.json
  awema licence delivrer "<agence>" [contact=…]      délivre une clé + l'enregistre (PREUVE)
  awema licence registre                             liste les licences délivrées (preuve : à qui/quand)
  awema licence verifier-cle <cle>                   prouve si TU as délivré cette clé (et à qui)
  awema licence revoquer-cle <cle> | set <cle> | verifier   gestion (voir docs/ACCES-AGENCE.md)
  awema acces demande "<agence>" [client= reseau= …]  enregistre une demande d'accès API managé
  awema acces lister | accepter <id> | refuser <id>   tu valides PAR AGENCE (défaut : API autonomes)
  awema attente ajouter "<nom>" contact=… [profil=…]  inscrit à la liste d'attente (PRIVÉ, hors git)
  awema attente lister | compter                      qui attend le lancement (sur abonnement)
  awema client new <slug|auto> ...   crée la fiche d'un client
  awema client memoire <slug> ...    édite la Mémoire Marketing (ton, personas, produits, faq…)
  awema client list                  liste les clients gérés
  awema serve [port]                 build + serveur local + ouvre le navigateur (1 commande)
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(RACINE, "scripts", "awema-connectors.json")
STORE_DIR = os.path.join(RACINE, ".awema")
STORE = os.path.join(STORE_DIR, "credentials.json")
HIST_MAX = 10


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def manifest():
    return json.load(open(MANIFEST, encoding="utf-8")).get("platforms", {})


# --------- Création / gestion de clients (onboarding assisté) ---------
import re
import unicodedata

CLIENTS_DIR = os.path.join(RACINE, "modules", "marketing", "clients")
CLIENT_CHAMPS = ["nom", "secteur", "lieu", "statut", "fb_page_id", "ig_user_id",
                 "yt_handle", "yt_channel_id", "slogan"]
CLIENT_LIENS = ["facebook", "instagram", "tiktok", "linkedin", "whatsapp", "youtube"]


def _slugify(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower() or "client"


def _initiales(nom):
    parts = [p for p in re.split(r"\s+", nom or "") if p]
    if not parts:
        return "AW"
    return ((parts[0][:1] + parts[1][:1]) if len(parts) >= 2 else parts[0][:2]).upper()


def cmd_client_new(slug, pairs):
    vals = {}
    for kv in pairs:
        if "=" in kv:
            k, v = kv.split("=", 1)
            vals[k] = v
    nom = vals.get("nom", slug)
    if not slug or slug in ("-", "auto"):
        slug = _slugify(nom)
    donnees = os.path.join(CLIENTS_DIR, slug, "_donnees")
    os.makedirs(donnees, exist_ok=True)
    cj = os.path.join(donnees, "client.json")
    if os.path.exists(cj):
        d = json.load(open(cj, encoding="utf-8"))
    else:
        d = {"id": slug, "nom": nom, "secteur": "", "lieu": "", "module": "marketing",
             "statut": "actif", "initiales": _initiales(nom),
             "reseaux": {k: "" for k in CLIENT_LIENS},
             "chemins": {"campagne": "_donnees/campagne.json", "reseaux": "_donnees/reseaux.json",
                         "revue": f"../../../../outils/revue-visuels/index.html?client={slug}"}}
    for k in CLIENT_CHAMPS:
        if vals.get(k):
            d[k] = vals[k]
    d.setdefault("reseaux", {})
    for k in CLIENT_LIENS:
        if vals.get(k):
            d["reseaux"][k] = vals[k]
    if vals.get("nom"):
        d["initiales"] = _initiales(vals["nom"])
    json.dump(d, open(cj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✅ Client « {d['nom']} » (slug: {slug}) créé/mis à jour → {os.path.relpath(cj, RACINE)}")
    subprocess.call([sys.executable, os.path.join(RACINE, "outils", "_data", "build.py")])
    print("\nProchaines étapes : connecte ses réseaux —")
    print("  • Facebook/Instagram : awema connect meta   (ou docs/05)")
    print("  • TikTok  : awema connect tiktok            (guide connect-tiktok.html)")
    print("  • YouTube : ajoute yt_handle + awema connect youtube  (guide connect-youtube.html)")


CONFIG_PATH = os.path.join(RACINE, "config", "agence.json")
LICENCE_PATH = os.path.join(RACINE, "config", "licence.json")
LEDGER = os.path.join(STORE_DIR, "licences-registre.json")   # registre PRIVÉ de délivrance (preuve)
ACCES_REG = os.path.join(STORE_DIR, "acces-api-registre.json")  # demandes d'accès API managé (preuve)
ATTENTE_REG = os.path.join(STORE_DIR, "liste-attente.json")  # liste d'attente lancement (PRIVÉ, hors git)
CONFIG_CHAMPS = ("nom", "nom_complet", "tagline", "slogan", "initiales", "langue", "contact")
CHARTE_KEYS = ("nuit", "ciel", "gold", "violet", "mint", "pink")


def cmd_setup(pairs):
    """Personnalise l'agence (auto-hébergement) : écrit config/agence.json puis régénère config.js.

    Clés : nom, nom_complet, tagline, slogan, initiales, langue, contact,
           github.owner, github.repo, charte.<nuit|ciel|gold|violet|mint|pink>.
    Sans argument : affiche la config courante.
    """
    cfg = json.load(open(CONFIG_PATH, encoding="utf-8")) if os.path.exists(CONFIG_PATH) else {}
    if not pairs:
        view = {k: v for k, v in cfg.items() if k != "_doc"}
        print("Configuration de l'agence (config/agence.json) :")
        print(json.dumps(view, ensure_ascii=False, indent=2))
        print("\nÉditer : awema setup nom=\"Mon Agence\" github.owner=monpseudo charte.ciel=#1DA1F2")
        return
    for kv in pairs:
        if "=" not in kv:
            continue
        k, v = kv.split("=", 1)
        if k in ("github.owner", "github.repo"):
            cfg.setdefault("github", {})[k.split(".", 1)[1]] = v
        elif k.startswith("charte."):
            ck = k.split(".", 1)[1]
            if ck not in CHARTE_KEYS:
                raise ValueError(f"couleur inconnue « {ck} » (attendu : {', '.join(CHARTE_KEYS)})")
            cfg.setdefault("charte", {})[ck] = v
        elif k in CONFIG_CHAMPS:
            cfg[k] = v
        else:
            raise ValueError(f"clé inconnue « {k} » (voir : awema setup)")
    if cfg.get("nom") and not cfg.get("initiales"):
        cfg["initiales"] = _initiales(cfg["nom"])
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    json.dump(cfg, open(CONFIG_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✅ Config mise à jour → {os.path.relpath(CONFIG_PATH, RACINE)}")
    subprocess.call([sys.executable, os.path.join(RACINE, "outils", "_data", "build.py")])
    print("\nTout l'outil (accueil, dashboard, guides) s'adapte automatiquement.")
    print("Pousse tes changements puis active GitHub Pages (depuis la racine) sur ton fork.")


def memoire_vide():
    """Schéma de la Mémoire Marketing d'un client (cf. docs/PRD-AWEMA.md §6)."""
    return {
        "identite": {"mission": "", "proposition_valeur": "", "cible": "", "secteur": ""},
        "ton": "", "charte": {"couleurs": [], "polices": [], "mots_cles": []},
        "personas": [], "produits": [], "faq": [], "campagnes": [],
        "performances_synthese": "", "references_visuelles": [],
    }


_MEM_SCALAIRES = {"ton": ("ton",), "mission": ("identite", "mission"),
                  "cible": ("identite", "cible"), "secteur": ("identite", "secteur"),
                  "proposition": ("identite", "proposition_valeur"),
                  "perf": ("performances_synthese",)}


def appliquer_memoire(mem, pairs):
    """Applique des paires à la mémoire. Fonction PURE (testable). Renvoie la mémoire modifiée.
    Scalaire : ton=… mission=… cible=… secteur=… proposition=… perf=…
    Listes (append) : faq+="Q::R"  persona+="Nom::besoin::objection"  produit+="Nom::desc::prix"
                      mot_cle+="…"  couleur+="…"  police+="…\""""
    def parts(v, n):
        p = [x.strip() for x in v.split("::")]
        return (p + [""] * n)[:n]
    for kv in pairs:
        if "+=" in kv:
            k, v = kv.split("+=", 1)
            if k == "faq":
                q, r = parts(v, 2); mem["faq"].append({"q": q, "r": r})
            elif k == "persona":
                n, b, o = parts(v, 3); mem["personas"].append({"nom": n, "besoin": b, "objection": o})
            elif k == "produit":
                n, d, p = parts(v, 3); mem["produits"].append({"nom": n, "description": d, "prix": p})
            elif k == "mot_cle":
                mem["charte"]["mots_cles"].append(v.strip())
            elif k == "couleur":
                mem["charte"]["couleurs"].append(v.strip())
            elif k == "police":
                mem["charte"]["polices"].append(v.strip())
            else:
                raise ValueError(f"liste inconnue « {k}+= » (faq/persona/produit/mot_cle/couleur/police)")
        elif "=" in kv:
            k, v = kv.split("=", 1)
            if k not in _MEM_SCALAIRES:
                raise ValueError(f"clé inconnue « {k} » (voir : awema client memoire <slug>)")
            tgt, path = mem, _MEM_SCALAIRES[k]
            for p in path[:-1]:
                tgt = tgt.setdefault(p, {})
            tgt[path[-1]] = v
        else:
            raise ValueError(f"format attendu KEY=VALUE ou KEY+=VALUE (reçu : {kv})")
    return mem


def cmd_client_memoire(slug, pairs):
    donnees = os.path.join(CLIENTS_DIR, slug, "_donnees")
    if not os.path.isdir(donnees):
        sys.exit(f"❌ client introuvable : {slug} (crée-le d'abord : awema client new …)")
    mj = os.path.join(donnees, "memoire.json")
    try:
        mem = json.load(open(mj, encoding="utf-8"))
    except Exception:
        mem = memoire_vide()
    if not pairs:
        print(f"Mémoire de « {slug} » ({os.path.relpath(mj, RACINE)}) :")
        print(json.dumps(mem, ensure_ascii=False, indent=2))
        print("\nÉditer : awema client memoire " + slug +
              " ton=\"…\" mission=\"…\" faq+=\"Question::Réponse\" persona+=\"Nom::besoin\"")
        return
    mem = appliquer_memoire(mem, pairs)
    json.dump(mem, open(mj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✅ Mémoire « {slug} » mise à jour → {os.path.relpath(mj, RACINE)}")
    subprocess.call([sys.executable, os.path.join(RACINE, "outils", "_data", "build.py")])
    print("La mémoire nourrit les agents IA (Analyste, Stratège, Créatif).")


def _licence_lire():
    try:
        return json.load(open(LICENCE_PATH, encoding="utf-8"))
    except Exception:
        return {"agence": "", "cle": "", "statut": "non-active", "delivre_par": "AWEMA"}


def _licence_valide(cle):
    return bool(re.match(r"^AWEMA-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$", cle or ""))


def _ledger_load():
    try:
        return json.load(open(LEDGER, encoding="utf-8"))
    except Exception:
        return {"delivre_par": "AWEMA", "licences": []}


def _ledger_save(led):
    os.makedirs(STORE_DIR, exist_ok=True)
    gi = os.path.join(STORE_DIR, ".gitignore")
    if not os.path.exists(gi):
        open(gi, "w").write("*\n")
    with open(LEDGER, "w", encoding="utf-8") as f:
        json.dump(led, f, ensure_ascii=False, indent=2)
    try:
        os.chmod(LEDGER, 0o600)
    except Exception:
        pass


def licence_ajouter(ledger, agence, contact, cle, quand):
    """Ajoute une licence au registre de preuve. Fonction PURE (testable)."""
    import hashlib
    n = len(ledger.get("licences", [])) + 1
    e = {"n": n, "agence": agence, "contact": contact, "cle": cle,
         "cle_hash": hashlib.sha256(cle.encode()).hexdigest(),
         "delivre_le": quand, "statut": "delivree"}
    ledger.setdefault("licences", []).append(e)
    return e


def cmd_licence(args):
    """Licence d'activation + REGISTRE de délivrance (preuve) — cf. docs/ACCES-AGENCE.md.
    Côté éditeur : delivrer "<agence>" [contact=…] · registre · verifier-cle <cle> · revoquer-cle <cle>.
    Côté instance : set <cle> · verifier · revoquer. Le registre (.awema, privé) prouve à qui tu as
    délivré (ou non) une licence — ta base juridique. Le vrai verrou technique reste l'accès API (modèle B)."""
    import hashlib
    sub = args[0] if args else "verifier"
    # ---------- Côté ÉDITEUR : délivrance & preuve ----------
    if sub == "delivrer":
        agence = args[1] if len(args) > 1 and "=" not in args[1] else ""
        if not agence:
            sys.exit('Usage : awema licence delivrer "Nom de l\'agence" [contact=email]')
        contact = next((a.split("=", 1)[1] for a in args[2:] if a.startswith("contact=")), "")
        h = hashlib.sha256((agence + os.urandom(8).hex()).encode()).hexdigest().upper()
        cle = "AWEMA-" + h[0:4] + "-" + h[4:8] + "-" + h[8:12]
        led = _ledger_load()
        e = licence_ajouter(led, agence, contact, cle, _now())
        _ledger_save(led)
        print(f"🔑 Licence n°{e['n']} pour « {agence} » :\n   {cle}")
        print(f"📒 Enregistrée comme PREUVE → {os.path.relpath(LEDGER, RACINE)} (privé, gitignoré, à sauvegarder).")
        print("→ Transmets la clé à l'agence (elle l'active : awema licence set " + cle + ").")
        print("→ Note la place dans config/beta-seats.json. Révoquer : awema licence revoquer-cle " + cle)
        print("→ Rappel : délivre AUSSI l'accès API (modèle B) — c'est le verrou réel.")
        return
    if sub == "registre":
        led = _ledger_load()
        ls = led.get("licences", [])
        if not ls:
            print("Aucune licence délivrée pour l'instant.")
            return
        print(f"📒 Registre de délivrance — {len(ls)} licence(s) · PREUVE ({os.path.relpath(LEDGER, RACINE)}) :")
        for e in ls:
            ligne = f"  n°{e['n']:2}  {e['statut']:9}  {e.get('delivre_le', '')[:10]}  {e['agence']}"
            if e.get("contact"):
                ligne += f" · {e['contact']}"
            print(ligne + f"  [{e['cle']}]")
        return
    if sub == "verifier-cle":
        cle = args[1] if len(args) > 1 else ""
        m = [e for e in _ledger_load().get("licences", []) if cle and (e.get("cle") == cle or e.get("cle_hash") == cle)]
        if m:
            e = m[0]
            print(f"✅ Délivrée à « {e['agence']} »" + (f" ({e['contact']})" if e.get("contact") else "")
                  + f" le {e.get('delivre_le', '')[:10]} — statut {e['statut']}.")
        else:
            print("❌ Cette clé n'est PAS dans ton registre (non délivrée par toi).")
        return
    if sub == "revoquer-cle":
        cle = args[1] if len(args) > 1 else ""
        led = _ledger_load()
        chg = False
        for e in led.get("licences", []):
            if e.get("cle") == cle:
                e["statut"] = "revoquee"
                e["revoque_le"] = _now()
                chg = True
        if chg:
            _ledger_save(led)
            print("⛔ Licence marquée révoquée dans le registre. Révoque AUSSI l'accès API (verrou réel).")
        else:
            print("Clé introuvable dans le registre.")
        return
    # ---------- Côté INSTANCE : activation locale ----------
    lic = _licence_lire()
    if sub == "set":
        cle = args[1] if len(args) > 1 else ""
        agence = next((a.split("=", 1)[1] for a in args[2:] if a.startswith("agence=")), lic.get("agence", ""))
        if not _licence_valide(cle):
            sys.exit("❌ clé invalide (format AWEMA-XXXX-XXXX-XXXX). Demande-la à l'éditeur AWEMA.")
        lic.update({"cle": cle, "agence": agence, "statut": "active"})
        json.dump(lic, open(LICENCE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"✅ Instance activée pour « {agence or '—'} ».")
        subprocess.call([sys.executable, os.path.join(RACINE, "outils", "_data", "build.py")])
        return
    if sub == "revoquer":
        lic.update({"cle": "", "statut": "revoquee"})
        json.dump(lic, open(LICENCE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("⛔ Licence révoquée. Rappel : révoque AUSSI l'accès API (le verrou réel).")
        subprocess.call([sys.executable, os.path.join(RACINE, "outils", "_data", "build.py")])
        return
    ok = lic.get("statut") == "active" and _licence_valide(lic.get("cle"))
    print(f"Licence : {'✅ active' if ok else '❌ ' + str(lic.get('statut'))} · agence: {lic.get('agence') or '—'}")
    if not ok:
        print("Activer : awema licence set <cle-fournie-par-AWEMA>")


def _acces_load():
    try:
        return json.load(open(ACCES_REG, encoding="utf-8"))
    except Exception:
        return {"demandes": []}


def _acces_save(reg):
    os.makedirs(STORE_DIR, exist_ok=True)
    gi = os.path.join(STORE_DIR, ".gitignore")
    if not os.path.exists(gi):
        open(gi, "w").write("*\n")
    with open(ACCES_REG, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
    try:
        os.chmod(ACCES_REG, 0o600)
    except Exception:
        pass


def acces_ajouter(reg, agence, contact, client, reseau, motif, quand):
    """Ajoute une demande d'accès API managé. Fonction PURE (testable)."""
    n = len(reg.get("demandes", [])) + 1
    e = {"id": n, "agence": agence, "contact": contact, "client": client, "reseau": reseau,
         "motif": motif, "demande_le": quand, "statut": "en_attente"}
    reg.setdefault("demandes", []).append(e)
    return e


def cmd_acces(args):
    """Accès API MANAGÉ (modèle B) — sur demande, validé PAR AGENCE. Par défaut, chaque agence
    fournit ses propres API (modèle A). Le routage par NOS API n'a lieu qu'après ton accord explicite.
    Sous-commandes : demande "<agence>" [contact= client= reseau= motif=] · lister ·
    accepter <id> [note=] · refuser <id> [note=]."""
    sub = args[0] if args else "lister"
    reg = _acces_load()

    def kv(prefixe):
        return next((a.split("=", 1)[1] for a in args[2:] if a.startswith(prefixe + "=")), "")

    if sub == "demande":
        agence = args[1] if len(args) > 1 and "=" not in args[1] else ""
        if not agence:
            sys.exit('Usage : awema acces demande "Agence" [contact= client= reseau= motif=]')
        e = acces_ajouter(reg, agence, kv("contact"), kv("client"), kv("reseau"), kv("motif"), _now())
        _acces_save(reg)
        print(f"📝 Demande n°{e['id']} enregistrée — « {agence} »"
              + (f" · client: {e['client']}" if e["client"] else "")
              + (f" · réseau: {e['reseau']}" if e["reseau"] else "") + " · statut: en_attente")
        print("→ À valider : awema acces accepter " + str(e["id"]) + "  (ou refuser)")
        return
    if sub in ("accepter", "refuser"):
        try:
            idd = int(args[1])
        except Exception:
            sys.exit(f"Usage : awema acces {sub} <id> [note=…]")
        note = kv("note")
        statut = "accepte" if sub == "accepter" else "refuse"
        trouve = False
        for e in reg.get("demandes", []):
            if e.get("id") == idd:
                e["statut"] = statut
                e["decide_le"] = _now()
                if note:
                    e["note"] = note
                trouve = True
        if not trouve:
            sys.exit(f"Demande n°{idd} introuvable (voir : awema acces lister).")
        _acces_save(reg)
        print(f"{'✅ Acceptée' if statut == 'accepte' else '⛔ Refusée'} — demande n°{idd}.")
        if statut == "accepte":
            print("→ Ouvre l'accès côté plateforme (ajoute la Page à ton App Meta / testeur TikTok…), "
                  "puis transmets le token via Secret GitHub. C'est le passage réel par tes API.")
        return
    # lister / défaut
    ds = reg.get("demandes", [])
    if not ds:
        print("Aucune demande d'accès API managé. (Par défaut, les agences utilisent LEURS propres API.)")
        return
    print(f"📋 Demandes d'accès API managé — {len(ds)} (PREUVE, {os.path.relpath(ACCES_REG, RACINE)}) :")
    for e in ds:
        ligne = f"  n°{e['id']:2}  {e['statut']:11}  {e.get('demande_le', '')[:10]}  {e['agence']}"
        if e.get("client"):
            ligne += f" · {e['client']}"
        if e.get("reseau"):
            ligne += f" [{e['reseau']}]"
        print(ligne)


def _attente_load():
    try:
        return json.load(open(ATTENTE_REG, encoding="utf-8"))
    except Exception:
        return {"inscrits": []}


def _attente_save(reg):
    os.makedirs(STORE_DIR, exist_ok=True)
    gi = os.path.join(STORE_DIR, ".gitignore")
    if not os.path.exists(gi):
        open(gi, "w").write("*\n")
    with open(ATTENTE_REG, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
    try:
        os.chmod(ATTENTE_REG, 0o600)
    except Exception:
        pass


def attente_ajouter(reg, nom, contact, profil, quand):
    """Ajoute un inscrit à la liste d'attente du lancement. Fonction PURE (testable).
    Dédoublonne sur le contact (email/tel) pour éviter les doublons d'un même intéressé."""
    contact_norm = (contact or "").strip().lower()
    for e in reg.get("inscrits", []):
        if contact_norm and (e.get("contact", "").strip().lower() == contact_norm):
            return e  # déjà inscrit → idempotent
    n = len(reg.get("inscrits", [])) + 1
    e = {"n": n, "nom": nom, "contact": contact, "profil": profil, "inscrit_le": quand}
    reg.setdefault("inscrits", []).append(e)
    return e


def cmd_attente(args):
    """Liste d'attente du lancement (sur abonnement). Stockée en PRIVÉ (.awema/, hors git).
    Sous-commandes : ajouter "<nom>" contact=<email/tel> [profil=…] · lister · compter."""
    sub = args[0] if args else "lister"
    reg = _attente_load()

    def kv(prefixe):
        return next((a.split("=", 1)[1] for a in args[1:] if a.startswith(prefixe + "=")), "")

    if sub == "ajouter":
        nom = args[1] if len(args) > 1 and "=" not in args[1] else ""
        if not nom:
            sys.exit('Usage : awema attente ajouter "Nom" contact=email [profil=…]')
        avant = len(reg.get("inscrits", []))
        e = attente_ajouter(reg, nom, kv("contact"), kv("profil"), _now())
        _attente_save(reg)
        if len(reg["inscrits"]) == avant:
            print(f"↺ Déjà inscrit·e — « {e['nom']} » (n°{e['n']}).")
        else:
            print(f"📩 Inscrit·e n°{e['n']} ajouté·e — « {nom} »"
                  + (f" · {e['profil']}" if e["profil"] else "") + f" · total : {len(reg['inscrits'])}")
        return
    if sub == "compter":
        print(len(reg.get("inscrits", [])))
        return
    # lister / défaut
    ins = reg.get("inscrits", [])
    if not ins:
        print("Liste d'attente vide. (Ajouter : awema attente ajouter \"Nom\" contact=email)")
        return
    print(f"📋 Liste d'attente — {len(ins)} inscrit·e·s (PRIVÉ, {os.path.relpath(ATTENTE_REG, RACINE)}) :")
    for e in ins:
        print(f"  n°{e['n']:3}  {e.get('inscrit_le', '')[:10]}  {e['nom']}"
              + (f" · {e['profil']}" if e.get("profil") else "")
              + (f"  <{e['contact']}>" if e.get("contact") else ""))


def cmd_client_list():
    motif = os.path.join(CLIENTS_DIR, "*", "_donnees", "client.json")
    import glob as _g
    rows = []
    for cj in sorted(_g.glob(motif)):
        try:
            d = json.load(open(cj, encoding="utf-8"))
        except Exception:
            continue
        rows.append((d.get("id", "?"), d.get("nom", "?"), d.get("secteur", ""), d.get("lieu", "")))
    print(f"{len(rows)} client(s) :")
    for i, (sid, nom, sec, lieu) in enumerate(rows, 1):
        print(f"  {i:2}. {sid:28} {nom}" + (f" — {sec}" if sec else "") + (f" · {lieu}" if lieu else ""))


def load():
    try:
        return json.load(open(STORE, encoding="utf-8"))
    except FileNotFoundError:
        return {"platforms": {}}


def save(store):
    os.makedirs(STORE_DIR, exist_ok=True)
    gi = os.path.join(STORE_DIR, ".gitignore")          # filet de sécurité : ce dossier ne se versionne pas
    if not os.path.exists(gi):
        open(gi, "w").write("*\n")
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)
    try:
        os.chmod(STORE, 0o600)
    except Exception:
        pass


def mask(v):
    if v is None:
        return "—"
    s = str(v)
    return s if len(s) <= 6 else s[:3] + "…" + s[-3:]


def plat_or_die(p):
    m = manifest()
    if p not in m:
        sys.exit(f"❌ plateforme inconnue : {p}. Connues : {', '.join(m)}")
    return m[p]


def current(store, p):
    return store["platforms"].get(p, {}).get("current", {})


def known_value(store, p, key):
    cur = current(store, p)
    v = cur.get(key)
    return v if v not in (None, "") else os.environ.get(key)


def cmd_list():
    m = manifest()
    store = load()
    for p, info in m.items():
        cur = current(store, p)
        req = [k["name"] for k in info["keys"] if not k.get("optional") and not k.get("managed")]
        have = sum(1 for k in req if known_value(store, p, k))
        if info.get("statut"):
            etat = "🔜 " + info["statut"]
        else:
            etat = (f"maj {cur.get('_set_at', '')[:10]}" if cur.get("_set_at") else "vide")
        print(f"• {p:11} {info['label']:30} identifiants {have}/{len(req)} · {etat}")


def cmd_needs(p, as_json):
    info = plat_or_die(p)
    store = load()
    out = []
    for k in info["keys"]:
        val = known_value(store, p, k["name"])
        out.append({"key": k["name"], "present": bool(val), "secret": k.get("secret", False),
                    "optional": k.get("optional", False), "managed": k.get("managed", False),
                    "prompt": k.get("prompt", ""), "github": k.get("github")})
    if as_json:
        print(json.dumps({"platform": p, "label": info["label"], "keys": out}, ensure_ascii=False))
        return
    print(f"{info['label']} — identifiants :")
    for k in out:
        tag = "✅" if k["present"] else ("(optionnel)" if k["optional"] else "❌ manquant")
        print(f"  {k['key']:26} {tag}  {k['prompt']}")
    miss = [k["key"] for k in out if not k["present"] and not k["optional"] and not k["managed"]]
    print("À fournir :", ", ".join(miss) if miss else "— tout est là")


def _archive_set(store, p, newvals):
    pl = store["platforms"].setdefault(p, {"current": {}, "history": []})
    cur = dict(pl.get("current", {}))
    change = any(cur.get(k) != v for k, v in newvals.items())
    if change and any(k != "_set_at" for k in cur):     # archive l'ancienne version si elle change
        snap = dict(cur)
        snap["_archived_at"] = _now()
        pl.setdefault("history", []).insert(0, snap)
        pl["history"] = pl["history"][:HIST_MAX]
    cur.update(newvals)
    cur["_set_at"] = _now()
    pl["current"] = cur


def cmd_set(p, pairs, stdin_key=None):
    plat_or_die(p)
    store = load()
    vals = {}
    for kv in pairs:
        if "=" not in kv:
            sys.exit(f"❌ format attendu KEY=VALUE (reçu : {kv})")
        k, v = kv.split("=", 1)
        vals[k] = v
    if stdin_key:
        vals[stdin_key] = sys.stdin.read().strip()
    if not vals:
        sys.exit("❌ rien à enregistrer.")
    _archive_set(store, p, vals)
    save(store)
    n = len(store["platforms"][p].get("history", []))
    print(f"✅ {p} : {', '.join(vals)} enregistré(s). Historique : {n} version(s) précédente(s).")


def cmd_rotate(p, pairs):
    cmd_set(p, pairs)
    print("↻ rotation effectuée — l'ancienne valeur est conservée en historique (awema history "
          + p + ").")


def cmd_get(p, reveal):
    info = plat_or_die(p)
    store = load()
    pl = store["platforms"].get(p, {})
    cur = pl.get("current", {})
    print(f"{info['label']} — courant (maj {cur.get('_set_at', '—')}) :")
    for k in info["keys"]:
        v = cur.get(k["name"]) or os.environ.get(k["name"])
        src = " (env)" if (not cur.get(k["name"]) and os.environ.get(k["name"])) else ""
        disp = (v if (reveal or not k.get("secret")) else mask(v)) if v else "—"
        print(f"  {k['name']:26} {disp}{src}")
    print(f"Historique : {len(pl.get('history', []))} version(s).")


def cmd_env(p):
    info = plat_or_die(p)
    store = load()
    cur = current(store, p)
    win = os.name == "nt"
    for k in info["keys"]:
        v = cur.get(k["name"]) or os.environ.get(k["name"])
        if v:
            print((f"set {k['name']}={v}") if win else (f"export {k['name']}={v}"))


def cmd_history(p, reveal):
    info = plat_or_die(p)
    store = load()
    hist = store["platforms"].get(p, {}).get("history", [])
    if not hist:
        print("Aucun historique pour " + p + ".")
        return
    for i, h in enumerate(hist):
        line = f"#{i + 1} archivé {h.get('_archived_at', '')[:19]} :"
        for k in info["keys"]:
            if k["name"] in h:
                v = h[k["name"]]
                line += f" {k['name']}={v if reveal or not k.get('secret') else mask(v)}"
        print(line)


def cmd_connect(p):
    info = plat_or_die(p)
    store = load()
    miss = [k["name"] for k in info["keys"]
            if not k.get("optional") and not k.get("managed") and not known_value(store, p, k["name"])]
    if miss:
        print("❌ identifiants manquants :", ", ".join(miss))
        print("   → fournis-les :  awema set " + p + " " + " ".join(f"{m}=…" for m in miss))
        sys.exit(2)
    cmds = info.get("commands", {})
    cmd = cmds.get("connect") or cmds.get("onboard")
    if not cmd:
        print("ℹ️ Pas de commande de connexion directe pour " + p + ". Voir :", info.get("doc", ""))
        return
    env = dict(os.environ)
    for k in info["keys"]:
        v = known_value(store, p, k["name"])
        if v:
            env[k["name"]] = v
    print("▶", cmd)
    sys.exit(subprocess.call(cmd, shell=True, cwd=RACINE, env=env))


def cmd_serve(args):
    """Lance AWEMA en local en UNE commande : régénère le registre, démarre un serveur
    statique (stdlib) et ouvre le navigateur. Usage : awema serve [port]."""
    import http.server
    import socketserver
    import threading
    import webbrowser
    port = next((int(a) for a in args if a.isdigit()), 8000)
    print("→ Régénération du registre…")
    subprocess.call([sys.executable, os.path.join(RACINE, "outils", "_data", "build.py")])
    os.chdir(RACINE)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = None
    for p in range(port, port + 20):                      # cherche un port libre
        try:
            httpd = socketserver.TCPServer(("127.0.0.1", p), handler)
            port = p
            break
        except OSError:
            continue
    if not httpd:
        sys.exit("❌ Aucun port libre entre %d et %d." % (port, port + 19))
    url = "http://127.0.0.1:%d/awema.html" % port
    print("✅ AWEMA en local : %s" % url)
    print("   Cockpit : http://127.0.0.1:%d/outils/dashboard/index.html" % port)
    print("   (Ctrl+C pour arrêter)")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 AWEMA arrêté.")


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return
    c = a[0]
    try:
        if c == "list":
            cmd_list()
        elif c == "needs" and len(a) >= 2:
            cmd_needs(a[1], "--json" in a)
        elif c == "set" and len(a) >= 3 and "--stdin" in a:
            key = [x for x in a[2:] if x != "--stdin"][0]
            cmd_set(a[1], [], stdin_key=key)
        elif c == "set" and len(a) >= 3:
            cmd_set(a[1], [x for x in a[2:] if "=" in x])
        elif c == "rotate" and len(a) >= 3:
            cmd_rotate(a[1], [x for x in a[2:] if "=" in x])
        elif c == "get" and len(a) >= 2:
            cmd_get(a[1], "--reveal" in a)
        elif c == "env" and len(a) >= 2:
            cmd_env(a[1])
        elif c == "history" and len(a) >= 2:
            cmd_history(a[1], "--reveal" in a)
        elif c == "connect" and len(a) >= 2:
            cmd_connect(a[1])
        elif c == "client" and len(a) >= 3 and a[1] == "new":
            cmd_client_new(a[2], a[3:])
        elif c == "client" and len(a) >= 3 and a[1] == "memoire":
            cmd_client_memoire(a[2], a[3:])
        elif c == "client" and len(a) >= 2 and a[1] == "list":
            cmd_client_list()
        elif c == "setup":
            cmd_setup([x for x in a[1:] if "=" in x])
        elif c == "licence":
            cmd_licence(a[1:])
        elif c == "acces":
            cmd_acces(a[1:])
        elif c == "attente":
            cmd_attente(a[1:])
        elif c == "serve":
            cmd_serve(a[1:])
        else:
            print(__doc__)
            sys.exit(1)
    except SystemExit:
        raise
    except Exception as e:
        sys.exit(f"❌ {e}")


if __name__ == "__main__":
    main()
