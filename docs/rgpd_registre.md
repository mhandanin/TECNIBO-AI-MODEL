# Registre des traitements de donnees personnelles (RGPD)

Registre minimal, tenu au format recommande par la CNIL (finalite,
categories de donnees, personnes concernees, destinataires, duree de
conservation, mesures de securite), applique a ce projet.

## Cadrage general

Ce projet est un projet personnel de certification, construit sur des
**donnees generiques/fictives** (dimensions et prix d'articles industriels
sur-mesure). Il ne traite **pas de donnees personnelles reelles**
(pas de nom de client, pas d'email, pas d'adresse). Le raisonnement
ci-dessous est neanmoins mene comme si le systeme etait mis en production,
pour identifier ou des donnees personnelles pourraient apparaitre dans le
pipeline et comment les traiter, c'est ce raisonnement qui est evalue pour
la certification, independamment du fait que les donnees actuelles soient
fictives.

## Traitement 1 : Donnees d'entrainement du modele (table `article`)

| Champ | Valeur |
|---|---|
| Finalite | Entrainer et evaluer un modele de prediction du prix d'un article industriel sur-mesure |
| Responsable de traitement | Le porteur du projet (usage personnel / certification) |
| Categories de donnees traitees | Dimensions (largeur, hauteur), materiau, profile, complexite, cout logistique, prix. **Aucune donnee a caractere personnel** : ce sont des caracteristiques d'objets (articles), pas de personnes. |
| Personnes concernees | Aucune (donnees produits/commandes, pas de donnees individu) |
| Base legale | Sans objet (pas de donnee personnelle) |
| Destinataires | Aucun tiers ; usage interne au pipeline (entrainement + evaluation) |
| Duree de conservation | Illimitee en l'etat (donnees de reference pour re-entrainement). A revoir si des donnees reelles de commandes client venaient a etre utilisees (cf. limitation ci-dessous). |
| Mesures de securite | Base PostgreSQL locale, non exposee publiquement ; acces restreint par identifiants (`.env`, non versionne) |

**Point d'attention pour un usage reel (hors perimetre de ce depot)** : si ce
pipeline etait un jour alimente par les vraies donnees de commandes de
l'entreprise (cf. Phase 0, fichiers exclus de ce depot), la table
`article`/`ORDERID` contiendrait potentiellement un identifiant de commande
relie a un client (personne physique ou societe). Il faudrait alors :
pseudonymiser l'identifiant client avant import, documenter la duree de
conservation (ex. alignee sur la duree legale de conservation des documents
commerciaux), et restreindre les acces (RBAC applicatif).

## Traitement 2 : Historique des predictions en production (table `prediction`, Phase 3+)

| Champ | Valeur |
|---|---|
| Finalite | Tracer les predictions realisees par l'API (audit, debogage, monitorage de derive du modele) |
| Responsable de traitement | Le porteur du projet |
| Categories de donnees traitees | Horodatage, features d'entree (dimensions, materiau, profile, code SPP), prix predit, latence. Potentiellement, selon l'implementation de l'API (Phase 3/5) : **adresse IP de l'appelant** (loggee par le serveur web/l'API) et **identifiant de cle API** si une authentification par cle est mise en place. |
| Personnes concernees | Utilisateurs/systemes appelant l'API (l'IP d'un poste utilisateur est une donnee personnelle au sens RGPD) |
| Base legale | Interet legitime (securite, detection d'abus, debogage operationnel) |
| Destinataires | Aucun tiers ; usage interne (monitorage, Phase 5) |
| Duree de conservation | **IP et logs techniques bruts : 30 jours** (duree usuelle recommandee CNIL pour des logs de securite), au-dela agregation/anonymisation. **Predictions metier (features + prix predit, sans IP) : 12 mois**, utile pour le monitorage de derive du modele dans la duree. |
| Mesures de securite | Base non exposee publiquement, `.env` non versionne, acces limite en local/dev. En production : chiffrement au repos, acces par role, rotation des cles API. |

**Mise en oeuvre technique correspondante** : le schema actuel (`prediction`,
`db/sql/001_init_schema.sql`) ne stocke pas d'IP ni d'identifiant appelant,
c'est volontaire a ce stade (Phase 2). Si une authentification est ajoutee en
Phase 3, ce registre devra etre mis a jour avec la colonne ajoutee et sa
duree de conservation propre.

## Droits des personnes

Sans objet en l'etat (aucune donnee personnelle reellement collectee). Si le
traitement 2 est etendu avec des IP/identifiants utilisateurs, prevoir : droit
d'acces et de suppression sur demande, information des utilisateurs de l'API
(mentions dans la documentation OpenAPI, cf. Phase 3).
