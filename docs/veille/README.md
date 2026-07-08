# Veille technique et reglementaire

## Thematique

**Cadre reglementaire et evolution des services d'IA generative europeens**, suivie
selon deux angles combines :

1. **Reglementaire** : application du reglement europeen sur l'IA (AI Act, reglement
   (UE) 2024/1689) aux systemes qui integrent un service d'IA generative tiers,
   notamment les obligations de transparence envers l'utilisateur final.
2. **Technique** : evolution de l'ecosysteme des LLM heberges/souverains en Europe
   (nouvelles offres, tarifs, nouveaux modeles, acteurs) susceptible d'affecter un choix
   technique deja fait.

## Objectif

Ce projet a integre un service d'IA generative tiers (Mistral AI) pour generer une
explication en langage naturel des predictions de prix (fonctionnalite "Pourquoi cette
prediction ?"). Ce choix a ete argumente dans
[`docs/benchmark_services_ia_generative.md`](../benchmark_services_ia_generative.md),
notamment sur des criteres de conformite RGPD et de souverainete des donnees (traitement
dans l'UE).

Un choix technique fonde sur un cadre reglementaire n'est pas une decision figee : le
reglement europeen sur l'IA est encore en cours de deploiement (obligations qui entrent
en application par etapes jusqu'en 2027), la doctrine de la CNIL sur l'IA generative
continue d'evoluer, et le paysage concurrentiel des LLM europeens change vite (nouveaux
modeles, nouveaux investissements, nouveaux entrants). Cette veille sert a verifier,
semaine apres semaine, si le choix fait reste pertinent ou s'il doit etre reexamine.

## Frequence engagee

**1 heure par semaine, chaque vendredi.**

La toute premiere entree ([2026-07-08](entrees/2026-07-08.md)) a ete redigee le jour de
la mise en place de cette veille (un mercredi, hors cycle). Le rythme hebdomadaire du
vendredi commence a partir du **10 juillet 2026**.

## Outil d'agregation

**Feedly** (offre gratuite, jusqu'a 100 flux RSS suivis). Les sources listees ci-dessous
sont ajoutees comme flux suivis lorsqu'elles en proposent un ; a defaut, elles sont
consultees directement (voir details par source ci-dessous).

## Sources suivies et evaluation de fiabilite

Pour chaque source, les six criteres suivants sont documentes explicitement : (1)
auteur/organisation identifie, (2) elements confirmant sa competence/notoriete et
l'absence d'interets personnels caches, (3) contenu date recemment et sourced, (4) site
structure, (5) normes d'accessibilite de base respectees, (6) information recoupable
avec d'autres sources fiables.

### 1. Commission europeenne — AI Act Service Desk / Digital Strategy

`ai-act-service-desk.ec.europa.eu`, `digital-strategy.ec.europa.eu`

- **Auteur identifie** : Commission europeenne (DG CNECT), domaine officiel `.europa.eu`.
- **Competence/absence d'interets caches** : institution legislatrice/regulatrice
  elle-meme, source primaire du texte reglementaire ; aucun interet commercial.
- **Contenu date et sourced** : pages mises a jour avec reference directe aux articles
  du reglement (UE) 2024/1689 et a leurs dates d'entree en application.
- **Site structure** : navigation par article du reglement, sommaire clair, moteur de
  recherche interne.
- **Accessibilite** : les sites institutionnels de l'UE sont soumis a une obligation
  legale d'accessibilite (directive (UE) 2016/2102, norme EN 301 549 / WCAG).
- **Recoupement possible** : oui, analyses reprises et commentees par des cabinets
  d'avocats specialises (ex. William Fry, Jones Day) et par la presse juridique/tech.

### 2. CNIL — rubrique Intelligence artificielle

`cnil.fr/fr/intelligence-artificielle-ia`

- **Auteur identifie** : CNIL, autorite administrative independante francaise, domaine
  officiel `cnil.fr`.
- **Competence/absence d'interets caches** : autorite de regulation independante avec
  mandat legal de protection des donnees ; aucun interet commercial.
- **Contenu date et sourced** : publications datees, qui renvoient explicitement aux
  textes RGPD et aux deliberations correspondantes.
- **Site structure** : site organise par rubrique thematique, dont une rubrique dediee
  a l'intelligence artificielle.
- **Accessibilite** : declaration d'accessibilite publiee par la CNIL (obligation legale
  RGAA pour un service public francais).
- **Recoupement possible** : oui, publications reprises par la presse juridique/tech
  specialisee RGPD.

### 3. Mistral AI — blog officiel

`mistral.ai/news`

- **Auteur identifie** : Mistral AI, entreprise francaise identifiee.
- **Competence/absence d'interets caches** : **a nuancer explicitement** — c'est une
  source interessee (communication d'une entreprise sur ses propres produits). Fiable
  pour les annonces factuelles datees (nouveaux modeles, chiffres publies, rapports
  co-signes avec des tiers independants comme Carbone4/ADEME), mais toute affirmation a
  caractere qualitatif ou comparatif doit etre recoupee avec une source independante
  avant d'etre reprise telle quelle.
- **Contenu date et sourced** : articles dates ; certaines publications s'appuient sur
  des rapports methodologiques co-realises avec des tiers (ex. le rapport d'impact
  environnemental avec Carbone4 et l'ADEME, deja cite dans le benchmark).
- **Site structure** : blog d'entreprise structure par categorie (annonces produit,
  recherche, entreprise).
- **Accessibilite** : non verifiee specifiquement a ce jour.
- **Recoupement possible** : oui, systematiquement recoupe avec la presse tech
  independante (ex. LeMagIT) dans le cadre de cette veille.

### 4. LeMagIT

`lemagit.fr`

- **Auteur identifie** : redaction de journalistes signes, edite par TechTarget (groupe
  de presse specialise B2B/IT).
- **Competence/absence d'interets caches** : presse specialisee IT reconnue en France
  depuis pres de 20 ans, independante des editeurs/entreprises qu'elle couvre (modele
  publicitaire/abonnement, pas de financement par les acteurs cites).
- **Contenu date et sourced** : articles horodates, citant leurs sources (etudes
  d'analystes comme Gartner/Forrester, communiques, autres medias).
- **Site structure** : site organise par rubrique (actualites, definitions, conseils,
  etudes de cas).
- **Accessibilite** : non verifiee specifiquement a ce jour.
- **Recoupement possible** : oui, c'est justement le role de cette source dans la
  veille : croiser les annonces officielles (Mistral, Commission europeenne, CNIL) avec
  une lecture journalistique independante.

## Journal des entrees (ordre chronologique)

- [2026-07-08 — Mise en place de la veille : AI Act art. 50, recommandations CNIL,
  actualite Mistral AI et souverainete cloud europeenne](entrees/2026-07-08.md)
