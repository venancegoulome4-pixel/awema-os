---
titre: ✅ Recette manuelle (test complet de bout en bout)
tags: [awema, recette, qa, test, checklist]
maj: 2026-07-02
---

# ✅ Recette manuelle — test complet de bout en bout

> Ce que les tests automatiques **ne peuvent pas** vérifier : OAuth réel,
> publication live sur les réseaux, écritures GitHub depuis le navigateur,
> vrais tokens, rendu visuel. À dérouler dans l'ordre — chaque phase suppose
> la précédente réussie. Complète : `python3 -m unittest discover -s tests`
> (117) + `tests/tests.html` (40 JS) + le job CI **Tests**.
>
> **Règle d'or à vérifier partout : « données réelles, zéro fiction ».** Aucun
> chiffre, aucune image, aucun nom ne doit apparaître sans provenir d'une vraie
> source. En cas de doute, un **tiret « — »** est la bonne réponse, jamais un
> zéro inventé ni un « undefined ».

Légende : ✅ résultat attendu · ⚠️ piège à surveiller · 🔴 bloquant si échec.

---

## Phase 0 — Prérequis

- Un compte GitHub (gratuit).
- Au moins **une** vraie ressource à connecter (Page Facebook, compte TikTok,
  chaîne YouTube ou Page LinkedIn) — sinon la recette s'arrête à la phase 3.
- Une clé IA gratuite (Groq recommandé : <https://console.groq.com/keys>).
- Navigateur de bureau + navigateur mobile (ou fenêtre étroite) pour le responsive.

---

## Phase 1 — Parcours nouvelle agence (fork → site en ligne)

1. Ouvrir la landing du template public (`awema.html` sur la branche `main`).
   ✅ Le cockpit affiche des chiffres neutres (pas de vrai client), CTA
   « Suivre le tutoriel » visible.
2. Ouvrir `tutoriel.html` → suivre les étapes 0→2 : compte GitHub, **Fork**,
   activer **GitHub Pages** (Settings → Pages → branche `main` → Save).
   ✅ Étape 2 : le bouton « Ouvrir les réglages Pages » mène **à TON dépôt**
   (pas au dépôt d'origine, pas de 404). 🔴 Si 404 → le fork n'est pas détecté.
   ⚠️ En lecture depuis le site d'origine (pas ton fork), le bouton doit dire
   « Retrouver ma copie (fork) » — c'est normal.
3. Attendre « Your site is live at … », ouvrir cette adresse.
   ✅ C'est **ton** AWEMA. À partir d'ici, tout se fait depuis cette URL.
4. Ouvrir le dashboard (`outils/dashboard/index.html`).
   ✅ Un seul client « **Éclat Beauté — DÉMO** » (données d'exemple, marquées démo).
   ✅ **Aucune** pastille « 📡 Données : il y a X » ni bouton Synchroniser
   (le client démo est exclu de la fraîcheur — une agence vierge ne voit pas de
   fausse alerte). 🔴 Si une pastille de fraîcheur apparaît → régression.

---

## Phase 2 — Brancher l'IA (le cerveau)

1. Dashboard → **Réglages** → « ① GitHub » → « Connecter mon GitHub ».
   Coller un **PAT fin** (fine-grained) avec accès en écriture à ton dépôt.
   ✅ Affiche « ✅ <ton pseudo> » + bouton « 🔒 Se déconnecter ».
   ⚠️ Le PAT vit **uniquement** dans le localStorage de ce navigateur.
2. « ③ Cerveau » → choisir Groq → coller la clé → Enregistrer.
   ✅ Message « ✅ groq branché » **ou** « colle la clé comme Secret » avec la
   fenêtre GitHub Secrets pré-ouverte. Vérifier dans GitHub : le **Secret**
   `GROQ_API_KEY` (et éventuellement la Variable `AWEMA_AI_PROVIDER`) existe.
   🔴 La clé ne doit **jamais** apparaître dans un commit ni dans les logs.
3. Onglet GitHub → **Actions** : le workflow `agents` peut être lancé
   (`Run workflow`) ou attendre son cron.
   ✅ Il se termine en vert ; un commit `chore(agents): …` apparaît.
   🔴 S'il échoue « clé absente » alors que la clé est là → vérifier le nom du Secret.

---

## Phase 3 — Connecter les vrais réseaux

Dashboard → **Connecter les réseaux** (section native, pas d'iframe).
✅ Six cartes ; chacune indique un **statut réel** (« N clients ✓ » ou « à connecter »).

- **Facebook / Instagram** : suivre `connect-facebook.html`, créer le Secret
  `META_TOKEN` (token longue durée). Lancer le workflow `sync-reseaux`.
  ✅ Un client par Page gérée apparaît. ⚠️ Token expiré → message clair (code 190).
- **TikTok** : « Se connecter avec TikTok » (OAuth), autoriser.
  ✅ Le compte remonte. 🔴 **Point critique** : relancer `sync-tiktok` **deux
  fois** — le 2ᵉ run doit réussir (les refresh tokens tournent et sont
  ré-enregistrés après chaque compte). Si le 2ᵉ run échoue « token invalide »,
  la sauvegarde de la Variable `TIKTOK_TOKENS` n'a pas marché → vérifier le
  Secret `TIKTOK_PAT` (scope « Variables: Read and write »).
- **YouTube** : clé API Google (Secret `YOUTUBE_API_KEY`), pas d'OAuth.
- **LinkedIn** : « Se connecter avec LinkedIn » (OAuth échangé dans une Action).

⚠️ Sur chaque page de connexion : les libellés doivent nommer **le bon réseau**
(pas « TikTok » en dur sur la page LinkedIn).

---

## Phase 4 — Première synchro & fraîcheur des données

1. Réglages → « ④ Lancer la 1ʳᵉ récupération » (ou bouton Synchroniser).
   ✅ Lance `sync-reseaux` + `sync-tiktok`. Attendre ~1–2 min, recharger.
2. Barre du haut : pastille « 📡 Données : il y a X ».
   ✅ Au survol : date/heure exacte de la dernière synchro.
   ✅ Si la synchro date de **plus de 24 h**, un bouton « 🔄 Synchroniser »
   apparaît à côté ; sinon non.
   ⚠️ La démo n'entre jamais dans ce calcul.

---

## Phase 5 — Données réelles (« zéro fiction »)

Choisir un vrai client → **Présence digitale**.

1. **Tuiles KPI** : chaque métrique montre une valeur **globale** + le détail
   par réseau en dessous (points aux **couleurs de marque** de chaque plateforme).
   ✅ Les couleurs FB/IG/TikTok/YouTube/LinkedIn sont respectées (jamais re-thémées).
   ✅ Une métrique absente affiche « — », jamais 0.
2. **Cadence de publication** : global (« depuis le dernier post · <réseau> ») +
   une ligne **par réseau**.
   🔴 Un client actif seulement sur TikTok ne doit **jamais** afficher
   « · Facebook » ni un compteur gonflé. ✅ « ≥ N » = estimation, « — » = inconnu,
   jamais « undefined ».
3. **Meilleur créneau** : une reco **par réseau** (l'engagement ne se compare pas
   entre plateformes).
4. **Courbe d'évolution des abonnés** : survoler → infobulle (valeur, date, delta
   coloré). ✅ L'axe X est proportionnel au **temps réel** (points espacés selon
   les vraies dates, pas régulièrement).
5. **Avatars & couverture** : après une 2ᵉ synchro (les URLs d'images arrivent),
   vue **Clients** → chaque carte porte l'avatar + le bandeau de couverture réels.
   ⚠️ Rien ne s'affiche tant que la vraie URL n'est pas là (aucune image fictive).

---

## Phase 6 — Mémoire de marque

1. Dashboard → **Mémoire** (formulaire natif, pas d'iframe).
   ✅ Pré-rempli si le client a déjà une mémoire.
2. Remplir mission, ton, mots-clés, ajouter 1 persona / 1 produit / 1 FAQ →
   « 💾 Enregistrer la mémoire ».
   ✅ Message « ✅ Enregistré ». Vérifier dans GitHub :
   `…/_donnees/memoire.json` committé.
   ✅ Le workflow `agents` se relance → propositions mises à jour ~1–2 min après.

---

## Phase 7 — Le processus de contenu (cœur du produit)

> Trois flux → une seule file de publication. Vérifier que chaque origine est
> tracée et que les deux axes (production / diffusion) s'affichent partout.

### 7.a — Propositions IA
1. **Planifier & publier** → champ idée (ou vide) → « ✨ Générer ».
   ✅ 1–2 min plus tard, des propositions apparaissent (hook + script + réseau).
2. « ✍️ Utiliser ce contenu » sur une proposition.
   ✅ Le composeur se remplit, la carte est surlignée d'un **halo or** ~2 s,
   le curseur est dans le champ texte (pas juste un rechargement).

### 7.b — Plan éditorial & revue des visuels
1. Dashboard → **Contenus** : la liste du plan.
   ✅ Pastille = **production** (statut de revue), badge = **diffusion**.
   ✅ Bouton **🗓️** sur les lignes non encore programmées.
2. Ouvrir le **Visualiseur** (« Visualiseur ↗ » depuis une carte client).
   Changer un statut (En revue / À retoucher / Validé), ajouter une note →
   « 💾 GitHub ».
   ✅ `…/_donnees/retours-visuels.json` committé.
   ✅ Recharger le dashboard (rebuild du registre) → la pastille de la vue
   Contenus reflète le nouveau statut de revue. ⚠️ Sans le bouton GitHub, le
   statut ne survivrait qu'au navigateur local.

### 7.c — Programmer depuis le plan
1. Vue Contenus → **🗓️** sur un contenu **Validé**.
   ✅ Le composeur se pré-remplit : légende + hashtags, date du plan (ramenée à
   aujourd'hui si passée), heure, réseau coché.
2. Vérifier, choisir une date proche → « 🗓️ Programmer ».
   ✅ Fichier `…/_donnees/_planning/<id>.json` committé avec `source:"plan"` et
   `plan_id`. La ligne du plan porte alors le badge « 🗓 programmé ».

### 7.d — Publication réelle (live)
1. Attendre le cron `publish` (toutes les 15 min) ou le lancer à la main.
   ✅ Le post part **réellement** sur le réseau. Le fichier passe à
   `statut:"publie"`, `resultats.<réseau>.url` porte le lien du post.
   ✅ Vue Contenus / Visualiseur : le badge devient « ✅ publié » **cliquable**
   → ouvre le vrai post en ligne.
   🔴 Le vert de « publié » doit être **identique** dans le dashboard et le
   visualiseur (#34E5C4).
2. **LinkedIn avec image** (validation live spécifique) : programmer un post
   LinkedIn avec une URL d'image publique.
   ✅ L'image est bien attachée (flux registerUpload → PUT → ugcPosts).
   🔴 Nécessite un `LINKEDIN_TOKEN` avec le scope `w_organization_social`.
   ⚠️ Si l'upload échoue, le réseau échoue **entièrement** (retry au prochain
   run) — jamais de post publié sans son visuel.

---

## Phase 8 — Calendrier éditorial

Dashboard → **Calendrier**.
✅ Grille mensuelle Lun→Dim, jour courant surligné or, navigation ← / → /
Aujourd'hui. ✅ Chaque case : plan éditorial (couleur de la **plateforme**) +
file de publication (couleur du **statut**). ✅ « +N autre(s) » si débordement.

---

## Phase 9 — Scoring

Dashboard → **Scoring**.
✅ Explication en 3 étapes (points like=1/comm=2/partage=3 → ratio vs **ta**
moyenne → note A→E = décision). ✅ Les posts réels sont notés ; un petit compte
peut avoir des A, un gros des E (comparaison **interne** au client).
✅ Si aucun post : état vide honnête, pas de faux score.

---

## Phase 10 — Rapport client

1. Carte client → « Rapport ↗ » (ou `rapport.html?client=<slug>`).
   ✅ En-tête (avatar/couverture réels), 6 KPIs, courbe, réseau par réseau,
   meilleur créneau, top 5 contenus, file de publication.
2. **Ctrl+P** → aperçu PDF.
   ✅ Le bouton « Imprimer » disparaît, pas de coupure au milieu d'une carte,
   mise en page propre.
3. `rapport.html?client=inexistant` → message « Rapport indisponible » propre.

---

## Phase 11 — Réponses aux commentaires (in-app)

> Nécessite une vraie synchro Meta ayant remonté des commentaires sans réponse
> (les IDs Graph n'existent qu'après synchro).

1. Présence digitale → carte **« À répondre »** → écrire une réponse → « Envoyer ».
   ✅ Fichier `…/_donnees/_reponses/<id>.json` committé (`statut:"a_envoyer"`).
   ✅ `reply.yml` se lance → la réponse est postée **en tant que la Page** via
   la Graph API ; le fichier passe à `statut:"envoye"`.
   ⚠️ Sur un ancien relevé sans ID Graph : la note « après la prochaine synchro »
   s'affiche à la place du champ — normal.

---

## Phase 12 — Rétrospective (hebdomadaire)

Le dimanche (ou lancer `retrospective` à la main une fois qu'il y a du publié).
✅ Vue **Mémoire** → bloc « Rétrospective de la semaine » : leçons (succès /
échec / abandon) + suggestions de mémoire.
✅ Quand il y a du publié de plusieurs **sources** (ia-creatif / plan / manuel),
la rétro compare leurs performances. 🔴 Elle **ne doit jamais** écrire la mémoire
elle-même — seulement suggérer ; l'humain valide.

---

## Phase 13 — Sécurité

1. **Déconnexion PAT** : Réglages → « 🔒 Se déconnecter ».
   ✅ Le token quitte le localStorage ; les actions d'écriture redemandent la
   connexion. (À faire sur un ordinateur partagé.)
2. **Aucun secret dans le dépôt** : parcourir les commits récents.
   🔴 Aucun token / clé ne doit apparaître, ni dans le code ni dans les logs
   d'Actions.
3. **Anti-injection (XSS)** : si un vrai commentaire, un titre de post ou une
   sortie d'IA contient du HTML (`<b>`, `<img …>`, `<`), il doit s'afficher
   **comme du texte littéral**, jamais s'exécuter ni casser la carte.
   ⚠️ Cas réel déjà rencontré : un titre commençant par « < » — vérifier que la
   carte « Meilleurs posts » reste intacte.

---

## Phase 13 bis — Réinitialiser le projet (zone dangereuse)

> Pour repartir sur une base neuve après un fork, ou tout recommencer.

1. Réglages → **Zone dangereuse**.
   ✅ Le bouton « 🗑️ Réinitialiser » est **désactivé** tant que le champ ne
   contient pas exactement `REINITIALISER`.
2. Cocher (ou non) « aussi l'identité de l'agence », taper `REINITIALISER`,
   cliquer → une **2ᵉ** confirmation navigateur s'affiche.
   ✅ Après OK : le workflow `reset-projet` se lance.
3. Attendre ~1 min, recharger.
   ✅ Portée **client** : plus aucun vrai client, seul « Client Démo » ; l'identité
   de l'agence (nom, charte) est conservée.
   ✅ Portée **complet** : en plus, l'agence est remise à neutre (« Mon Agence »).
   🔴 Les **Secrets/tokens** GitHub et l'**historique git** ne sont pas touchés
   (les anciennes données restent dans les commits passés — nouveau départ, pas
   de réécriture).
   ⚠️ Sans taper `REINITIALISER` **ou** en annulant la 2ᵉ confirmation : **rien**
   n'est supprimé.

---

## Phase 14 — Template public propre (pour une future agence)

1. Cloner / ouvrir la branche `main` (le template public).
   🔴 **Aucune** donnée d'un vrai client : un seul client démo, noms neutralisés.
   🔴 Aucun `data.js` mono-client, aucun `reseaux.json` réel.
2. La branche par défaut du dépôt public = `main` (jamais la branche privée).

---

## Phase 15 — Intégration continue

Onglet GitHub → **Actions** → workflow **Tests**.
✅ Job `unittest` vert (117). ✅ Job `js` vert (« AWEMA-TESTS-RESULTAT: OK 40/40 »).
🔴 Un rouge ici bloque toute mise en production.

---

## Récapitulatif — check-list express

- [ ] Fork → Pages → dashboard s'ouvre, liens GitHub corrects (pas de 404)
- [ ] IA branchée (Secret présent, agents verts)
- [ ] Réseaux connectés ; TikTok survit à **2** syncs de suite
- [ ] Pastille de fraîcheur + bouton > 24 h ; démo exclue
- [ ] KPI global + détail par réseau ; « — » jamais « undefined » ni 0 inventé
- [ ] Cadence & créneau **multi-réseaux** (pas de « Facebook » fantôme)
- [ ] Avatars/couverture réels après synchro
- [ ] Mémoire enregistrée dans GitHub → agents régénérés
- [ ] Proposition IA → composeur (halo) ; source `ia-creatif` tracée
- [ ] Retours du visualiseur sauvegardés dans GitHub → pastille production MAJ
- [ ] 🗓️ depuis le plan → composeur pré-rempli ; badge diffusion ; `plan_id`
- [ ] Publication live → badge « publié » cliquable → vrai post
- [ ] LinkedIn image (registerUpload) — token `w_organization_social`
- [ ] Calendrier, Scoring, Rapport (PDF), Réponses in-app, Rétrospective
- [ ] Réinitialisation : bouton verrouillé sans `REINITIALISER` ; client vs complet
- [ ] Déconnexion PAT ; aucun secret dans le dépôt ; HTML hostile = texte
- [ ] `main` propre ; CI verte (113 + 40)
