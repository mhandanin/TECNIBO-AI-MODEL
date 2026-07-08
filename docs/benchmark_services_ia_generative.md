# Benchmark de services d'IA generative pour l'explicabilite des predictions

Ce document precede toute implementation : il ne contient aucun code,
seulement l'analyse ayant mene au choix du service.

## Besoin fonctionnel

Le systeme de pricing (`api/`) renvoie aujourd'hui un prix predit brut (un
nombre) a partir des caracteristiques d'un article (dimensions, materiau,
profile, complexite, cout logistique). L'utilisateur n'a aucune indication
sur **pourquoi** ce prix a ete propose : quelles features ont le plus pese,
si le resultat est dans une fourchette habituelle, etc.

Le besoin est d'ajouter une fonctionnalite "Pourquoi cette prediction ?" qui
genere, en langage naturel, un court commentaire explicatif a partir du
resultat de prediction et des features en entree. Ce n'est **pas** un
probleme de Machine Learning a resoudre en interne (ce n'est pas un modele
de scoring ou de regression) : c'est un besoin de **generation de texte a
partir d'un contexte structure**, une tache generique bien couverte par les
services d'IA generative (LLM) du marche, sans justification a construire
un modele maison pour ca. L'approche la plus pertinente est donc
d'identifier et choisir un service existant plutot que de reinventer la
roue.

**Contrainte de conception importante (separation des responsabilites)** :
ce service tiers ne doit **jamais** influencer le prix predit lui-meme
(qui reste calcule exclusivement par le modele custom de `ml/`/`api/`). Il
recoit le resultat deja calcule et se contente de le commenter. Cette
frontiere est deliberement gardee etanche entre le modele maison qui
calcule le prix et le service preexistant qui se contente de l'expliquer.

## Services identifies

Trois services d'IA generative textuelle ont ete retenus comme candidats
pertinents, tous exposant une API HTTP simple avec SDK Python officiel,
adaptes a une tache de generation de texte courte a partir d'un prompt
structure :

1. **Mistral AI** ("La Plateforme", API `chat/completions`)
2. **OpenAI** (API `chat/completions`, modeles GPT)
3. **Hugging Face Inference API / Inference Endpoints**

D'autres alternatives ont ete ecartees des l'identification, pour des
raisons rapides a expliciter (pas de benchmark complet necessaire) :

- **Anthropic (Claude API)** : ecarte non pas pour des raisons de qualite,
  mais parce qu'au moment de ce benchmark l'entreprise n'a pas d'entite
  legale ni d'infrastructure de traitement des donnees dans l'Union
  Europeenne comparable a Mistral AI, ce qui aurait pose la meme
  problematique de transfert hors UE que OpenAI (cf. plus bas) sans
  apporter d'avantage differenciant pour ce cas d'usage (un simple
  commentaire de quelques phrases).
- **Un LLM auto-heberge (ex. Llama/Mistral open-weight via Ollama en
  local)** : ecarte pour ce besoin precis car cela demanderait de
  provisionner et maintenir une infrastructure GPU dediee (cout et
  complexite operationnelle disproportionnes pour generer un court texte
  explicatif occasionnel) ; cela reste une option valable si le volume
  d'appels devenait tres important, a reevaluer le cas echeant.

## Grille de comparaison

| Critere | Mistral AI | OpenAI | Hugging Face Inference API |
|---|---|---|---|
| **Cout / tarification** | A l'usage (par token). Modele d'entree de gamme (`mistral-small-latest`) tres bon marche, largement suffisant pour un texte court de quelques phrases. Pas de cout d'infrastructure idle. | A l'usage (par token). Modele d'entree de gamme (`gpt-4o-mini`) egalement tres bon marche et comparable en prix a l'offre Mistral. | **Serverless (gratuit/limite)** : quotas restrictifs et files d'attente, peu fiable pour un usage produit. **Inference Endpoints dedies** : factures a l'heure d'infrastructure active, pas a l'appel -- mauvais rapport cout/usage pour un appel occasionnel et imprevisible ("un utilisateur clique de temps en temps sur *Pourquoi ce prix ?*"). |
| **Latence typique** | Faible (quelques centaines de ms a ~1-2s pour un texte court avec un petit modele), infrastructure europeenne. | Faible a comparable, infrastructure majoritairement hors UE (latence reseau additionnelle depuis la France, generalement encore acceptable). | Tres variable : *cold start* frequent sur le tier serverless gratuit (plusieurs secondes, voire echec si le modele n'est pas deja charge) ; latence correcte uniquement sur un Endpoint dedie deja actif. |
| **Conformite RGPD / localisation des donnees** | **Entreprise francaise (Paris), soumise directement au RGPD.** Traitement des donnees dans l'UE annonce explicitement, pas de necessite de clauses contractuelles types (CCT) pour un transfert hors UE. Alignement direct avec `docs/rgpd_registre.md` deja redige pour ce projet. | Entreprise americaine. Traitement par defaut hors UE (necessite CCT / mecanismes de transfert type Data Privacy Framework) ; une option de residence des donnees en UE existe mais reservee a des offres entreprise/plus complexes a mettre en place que le besoin ne le justifie ici. | Entreprise americaine (Hugging Face Inc.). Le tier serverless gratuit ne garantit pas la region de traitement. Les Inference Endpoints dedies permettent de choisir explicitement une region AWS `eu-west-1`, mais uniquement sur l'offre payante dediee -- une garantie RGPD "par defaut" moins immediate que Mistral. |
| **Facilite d'integration technique** | SDK Python officiel (`mistralai`), authentification par simple cle Bearer, API tres proche du standard `chat/completions`, documentation claire. | SDK Python officiel (`openai`), tres mature, egalement standard `chat/completions`, ecosysteme le plus documente du marche. | SDK Python officiel (`huggingface_hub`, classe `InferenceClient`), mais necessite en plus de choisir/gerer un modele hebergeur precis et son format de prompt, un peu plus de configuration qu'un simple appel "chat". |
| **Contraintes techniques et pre-requis** | Necessite une cle API "La Plateforme" (creation de compte, carte bancaire pour depasser le tier gratuit d'essai). | Necessite une cle API OpenAI (compte + moyen de paiement). | Necessite un compte HF ; pour un usage fiable en production, necessite de provisionner un Inference Endpoint dedie (configuration d'infrastructure), sinon le tier serverless gratuit reste impropre a un usage produit stable. |
| **Demarche eco-responsable** | Seul des trois a avoir publie (juillet 2025) une analyse de cycle de vie (ACV) complete et auditee d'un de ses modeles (Mistral Large 2), realisee avec le cabinet Carbone 4 et l'agence francaise de la transition ecologique (ADEME), et revue par des pairs (Resilio, Hubblo). Perimetre couvrant la fabrication du materiel, l'entrainement et l'inference. Chiffres publies : 20,4 kt CO2e et 281 000 m3 d'eau pour l'entrainement du modele et 18 mois d'usage ; 1,14 g CO2e et 45 mL d'eau pour une reponse de 400 tokens via Le Chat. Les resultats seront verses a la base Empreinte de l'ADEME. | Aucun rapport methodologique audite publie pour ses modeles de production (dont `gpt-4o-mini`). La seule donnee chiffree publique est une estimation non auditee communiquee par le PDG Sam Altman sur son blog personnel (juin 2025, billet "The Gentle Singularity") : environ 0,34 Wh et 0,32 mL d'eau par "requete moyenne" -- sans definition precise de cette moyenne, sans prise en compte de l'entrainement, et sans verification independante. **Aucune donnee publique verifiable ou auditee n'est disponible a ce jour sur l'empreinte reelle du modele utilise dans ce projet.** | Pas de rapport global sur un modele generatif specifique equivalent a l'ACV de Mistral, mais Hugging Face est a l'origine d'outils de mesure standardises et publics : `CodeCarbon` (bibliotheque de mesure d'empreinte carbone d'entrainement/inference) et l'**AI Energy Score** (classement par etoiles de l'efficacite energetique de 166 modeles, methodologie et donnees brutes publiques, mesures sur GPU H100). Ces outils permettent de comparer l'efficacite de modeles individuels heberges sur le Hub, mais ne fournissent pas une empreinte deja calculee pour un usage via l'API d'inference telle quelle. |

**Sources** (consultees juillet 2026) : [Mistral AI -- Our contribution to a global environmental standard for AI](https://mistral.ai/news/our-contribution-to-a-global-environmental-standard-for-ai/) ; [Carbone4 -- A New Milestone for Environmental Transparency in Generative AI](https://www.carbone4.com/en/ia-generative-mission-mistral-ai) ; [Data Center Dynamics -- Sam Altman: ChatGPT queries consume 0.34 watt-hours](https://www.datacenterdynamics.com/en/news/sam-altman-chatgpt-queries-consume-034-watt-hours-of-electricity-and-0000085-gallons-of-water/) ; [Hugging Face -- AI Energy Score](https://huggingface.github.io/AIEnergyScore/) ; [Hugging Face -- Displaying carbon emissions for your model](https://huggingface.co/docs/hub/en/model-cards-co2).

## Recommandation

**Service retenu : Mistral AI**, via son API `chat/completions` (modele
`mistral-small-latest`, largement suffisant pour un texte explicatif court).

**Raisons du choix :**

1. **RGPD, critere determinant pour ce projet** : Mistral AI est une
   entreprise francaise traitant les donnees dans l'UE par defaut. C'est
   le seul des trois services qui n'impose, des le depart et sans option
   payante additionnelle, aucune reflexion sur un transfert de donnees hors
   UE. Cela s'aligne directement avec la demarche deja engagee dans
   `docs/rgpd_registre.md` : plutot que d'ajouter un nouveau traitement dont
   la conformite est "a verifier au cas par cas" (OpenAI) ou "garantie
   uniquement sur une offre payante dediee" (Hugging Face), le choix de
   Mistral rend ce nouveau traitement conforme par construction.
2. **Cout adapte a un usage occasionnel et imprevisible** : la facturation
   au token (et non a l'infrastructure active) evite le probleme majeur de
   Hugging Face Inference Endpoints, qui factureraient une machine allumee
   meme quand personne ne clique sur "Pourquoi ce prix ?".
3. **Integration simple** : SDK officiel, authentification par cle unique,
   API standard -- comparable en simplicite a OpenAI, sans le
   questionnement RGPD associe.
4. **Demarche eco-responsable, critere qui confirme le choix sans l'avoir
   initialement motive** : la decision reposait deja sur le RGPD et le
   cout avant d'examiner ce point. Mistral se distingue neanmoins comme le
   seul des trois a avoir rendu publique une analyse de cycle de vie
   auditee et chiffree de l'un de ses modeles, la ou OpenAI ne communique
   qu'une estimation non auditee via un blog personnel et ou Hugging Face
   fournit des outils de mesure generiques sans chiffrage direct de son
   service d'inference. Ce critere ne change donc pas la recommandation,
   mais renforce sa robustesse : le service deja retenu pour des raisons
   RGPD et de cout est aussi celui qui documente le mieux publiquement son
   impact environnemental.

**Raisons d'ecarter les deux autres :**

- **OpenAI** : ecarte non pas pour une raison technique (le SDK et la
  qualite de generation sont tout a fait comparables a Mistral) mais parce
  que le traitement par defaut hors UE aurait exige une justification RGPD
  supplementaire (mecanisme de transfert), une complexite evitable alors
  qu'une alternative europeenne equivalente existe pour ce besoin precis.
- **Hugging Face Inference API** : ecarte a cause de l'inadequation entre
  son modele de facturation (tier gratuit peu fiable en production /
  Endpoint dedie facture a l'infrastructure) et le profil d'usage vise
  (appels ponctuels et espaces dans le temps), ainsi qu'une garantie RGPD
  moins immediate que Mistral sur l'offre par defaut.
