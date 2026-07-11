# AWEMA OS

> Le **système d'exploitation open source d'une agence digitale assistée par IA**.
> Auto-hébergé, sans SaaS, piloté **holistiquement par des humains et des agents IA**.

Ce dépôt n'est pas un simple dossier de fichiers : c'est le **cerveau opérationnel** d'une agence.
Il réunit la présence en ligne **réelle** des clients et fait **travailler une équipe d'agents IA
spécialisés** qui observent, analysent, **proposent** et préparent. **L'IA ne répond pas : elle
travaille.** Les humains décident.

---

## 🎯 Principe directeur

> **Tout ce qui est produit doit pouvoir être repris, compris et ré-exécuté par un autre agent (humain
> ou IA) sans contexte préalable.**

D'où : un `README.md` par dossier · méthodes séparées des livrables · volumes générés par script ·
charte et conventions centralisées et **obligatoires** · **données réelles, zéro fiction**.

---

## 🏛️ Le modèle : un Kernel, des modules

AWEMA repose sur un **Kernel** de concepts universels (Mission, Workflow, Knowledge, Memory, Context,
Agent, Event, Automation, Plugin, Security, API) qui **ne contient aucune logique métier**. Le métier
vit dans des **modules**. Aujourd'hui, **un seul module est officiel : Marketing.** Les autres domaines
(Finance, RH, Commercial…) sont **rendus possibles par l'architecture**, mais **ne sont pas développés**.

👉 La référence stable du projet est le corpus **[`docs/FOUNDATION/`](docs/FOUNDATION/README.md)**
(Constitution, Kernel, principes de conception, modèle de plugins, modèle d'agents, modèle de données,
gouvernance, ADR). **Il prime en cas de conflit.**

---

## 🗂️ Structure du dépôt

```
.
├── README.md · AGENTS.md            ← portes d'entrée (humains & agents IA)
├── docs/                            ← documentation
│   ├── FOUNDATION/                  ← 🏛️ socle de référence STABLE (Kernel, principes, ADR)
│   ├── PRD-AWEMA.md                 ← référence produit (North Star)
│   ├── ROADMAP.md                   ← feuille de route (SOURCE UNIQUE)
│   ├── PLAN-EXECUTION-BETA.md       ← plan module par module (M0→M6)
│   └── 01-… 14-…                    ← guides (conventions, charte, connecter réseaux/IA, sécurité…)
│
├── modules/                    ← un dossier par MODULE (renommé depuis departements/ — ADR-006)
│   └── marketing/                   ← 🟢 LE module officiel : méthodologie/ + templates/ + clients/
│
├── outils/                          ← outils web transverses (100 % statiques)
│   ├── _data/build.py               ← agrège les données → registre (config.js / agence.js)
│   ├── dashboard/                   ← cockpit (Command Center)
│   └── revue-visuels/               ← revue/annotation des visuels
│
├── scripts/                         ← cœur Python (stdlib) : awema.py (opérateur), awema_ai.py,
│                                       run-agent.py, connect-reseaux.py + manifestes (agents/connecteurs)
├── config/                          ← agence.json (personnalisation), ia-providers, licence, beta-seats
├── tests/                           ← harnais anti-régression (unittest stdlib)
├── .github/workflows/               ← automatisations (sync réseaux, agents IA, tests)
└── awema.html · onboarding · setup · connect-*.html …   ← pages produit (servies par GitHub Pages)
```

---

## 🚀 Démarrage rapide

### Voie principale — depuis GitHub, sans rien installer (recommandé)

> 🧭 **Débutant ? Suis le [Tutoriel d'installation complet (pas à pas)](docs/TUTORIEL-AGENCE.md)** — du fork
> jusqu'à AWEMA qui tourne, sans aucune commande.

> **Étape 0 (toujours) : Fork + activer Pages.** Tout le reste se configure **dans le navigateur**.

1. **Fork** ce dépôt → tu en deviens propriétaire (ton instance privée).
2. **Settings → Pages** → Source : branche `main`, dossier `/` → tu obtiens `https://<toi>.github.io/<repo>/`.
3. Ouvre ton URL Pages → la bannière **« Mise en route »** t'accueille → **Connecter GitHub** (un PAT, une fois).
4. Clé IA, tokens réseaux, OAuth TikTok/LinkedIn, clients : **tout depuis la page**. Les GitHub Actions
   (agents, synchro) tournent toutes seules ; Pages sert le cockpit à jour.

Aucune machine locale, aucun terminal. Le navigateur écrit dans **ton** dépôt via l'API GitHub
(le PAT est le seul pont) — c'est le principe « GitHub = back-end » ([ADR-007](docs/FOUNDATION/08-ARCHITECTURE_DECISIONS.md)).
Détails pas à pas → [`docs/17-mise-en-route-complete.md`](docs/17-mise-en-route-complete.md).

### Voie power-user — en local (optionnel, si tu as Python 3)

```bash
python3 scripts/awema.py serve     # build + serveur local + ouvre le navigateur
```
Et pour **piloter AWEMA en langage naturel** depuis Claude (MCP) → [`docs/16-piloter-avec-claude-mcp.md`](docs/16-piloter-avec-claude-mcp.md).

| Vous êtes… | Lisez en priorité |
|---|---|
| **Chief Architect / contributeur** | [`docs/FOUNDATION/`](docs/FOUNDATION/README.md) puis [`docs/PRD-AWEMA.md`](docs/PRD-AWEMA.md) |
| Un **agent IA** assigné à une tâche | [`AGENTS.md`](AGENTS.md) puis le module concerné |
| Une **agence qui veut auto-héberger** | [`docs/09-auto-hebergement.md`](docs/09-auto-hebergement.md) + `setup.html` |
| Au **module Marketing** | [`modules/marketing/README.md`](modules/marketing/README.md) |
| À la recherche d'un **outil** (cockpit, revue de visuels) | [`outils/README.md`](outils/README.md) |

---

## 🟢 Le module Marketing (seul module officiel)

Tout l'effort se concentre ici. Le module vise la meilleure solution possible pour : **community
management · calendrier éditorial · analyse · reporting · production · validation · assets ·
connecteurs · Mémoire Marketing · agents IA · automatisation**.

**Agents IA livrés** : Analyste (*pourquoi / quoi faire*) · Stratège (*plan*) · Créatif (*publications
prêtes*) · Rétrospective (*apprentissage hebdo : compare les sources et les perfs passées*) ·
Proactivité (*« 3 choses à faire aujourd'hui »*, déterministe, sans clé IA).
Contrat d'agent : [`docs/FOUNDATION/05-AGENT_MODEL.md`](docs/FOUNDATION/05-AGENT_MODEL.md).

**Exemple de client** : le client de **démo** (livré avec le template) illustre la structure d'une
mission complète — calendrier éditorial, présence digitale, Mémoire Marketing, sorties d'agents →
[`modules/marketing/clients/`](modules/marketing/clients/). Chaque client réel suit exactement la
même arborescence `_donnees/`.

---

## 🧭 Conventions essentielles (résumé)

1. **Français** comme langue de travail. Noms de fichiers en `kebab-case` sans accents.
2. **Markdown** (doc) · **CSV** (tabulaire) · **Python stdlib** (génération). Front : HTML/CSS/JS vanilla.
3. Un dossier = un `README.md`. La **charte graphique** est **non négociable**.
4. **Additif d'abord, plugin avant Kernel, données réelles, secrets jamais dans le dépôt.**
5. Rien n'est « fini » sans la *Definition of Done* ([`docs/03-conventions.md`](docs/03-conventions.md)
   et [`docs/FOUNDATION/03-DESIGN_PRINCIPLES.md`](docs/FOUNDATION/03-DESIGN_PRINCIPLES.md)).

## 📜 Licence

**GNU Affero General Public License v3.0 (AGPL-3.0)** — voir [`LICENSE`](LICENSE).

Copyright © 2026 AWEMA (codescooper).

AWEMA OS est un logiciel serveur : l'AGPL est choisie pour ça. Concrètement — **si tu forkes et
modifies AWEMA, puis le proposes à d'autres via un serveur (SaaS, hébergement pour des agences
tierces), tu dois offrir à ces utilisateurs le code source de ta version modifiée** (section 13,
« interaction réseau à distance »). Un usage interne à ta propre agence n'impose rien de plus que de
conserver cette licence. C'est ce qui garde l'écosystème ouvert et protège le modèle « Tech
Provider » : personne ne peut fermer un dérivé d'AWEMA en le cachant derrière un serveur.

---

_AWEMA OS — open source (AGPL-3.0) · auto-hébergé · données réelles · l'IA travaille, l'humain décide._
