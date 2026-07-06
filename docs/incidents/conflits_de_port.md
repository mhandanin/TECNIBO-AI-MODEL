# Rapport retrospectif : conflits de port (Phases 2 et 4)

**Type** : incidents reels, rencontres pendant le developpement de ce
projet (pas simules). Regroupes ici car de meme nature : un service tiers
deja installe sur la machine de developpement occupait un port que le
projet voulait utiliser.

## Incident 1 : port 5432 (PostgreSQL), Phase 2

### Contexte

`docker-compose.yml` exposait initialement le conteneur PostgreSQL sur le
port par defaut, `5432:5432`.

### Detection

La connexion depuis les scripts Python (`db/scripts/import_dataset.py`)
echouait avec une erreur d'authentification, alors que les identifiants
(`POSTGRES_USER`/`POSTGRES_PASSWORD` dans `.env`) etaient corrects.

### Diagnostic

Le message d'erreur psycopg2 etait **en allemand et mal decode sous
Windows**, ce qui a d'abord masque la vraie cause (il ressemblait a une
erreur d'encodage plutot qu'a un probleme d'authentification). En
creusant : le port 5432 etait deja occupe par une **instance PostgreSQL
native** installee sur la machine (service Windows `postgresql-x64-18`).
Les connexions du projet atteignaient donc cette instance native (avec
d'autres identifiants) au lieu du conteneur Docker.

### Resolution

Exposer le conteneur sur le port **5433** au lieu de 5432
(`POSTGRES_PORT` dans `.env.example`/`.env`, repercute dans
`DATABASE_URL` et `docker-compose.yml`).

### Mesures preventives

- `.env.example` documente explicitement pourquoi 5433 et pas 5432
  (commentaire dans le fichier).
- Retenu comme point de vigilance recurrent pour ce depot : tout nouveau
  service expose un port doit d'abord verifier qu'il est libre sur cette
  machine (cf. incident 2, meme famille de probleme).

## Incident 2 : port 8080 (app cliente), Phase 4

### Contexte

En ajoutant le service `app` (application cliente) a `docker-compose.yml`
en Phase 4, le port hote choisi initialement etait le port web
conventionnel, **8080**.

### Detection

Apres `docker compose up -d`, `curl http://127.0.0.1:8080/` ne renvoyait
pas la page HTML de `pricing_app` attendue, mais une page HTML
d'un serveur Apache portant le logo **EnterpriseDB**
("Server is up and running", lien vers enterprisedb.com).

### Diagnostic

`Get-NetTCPConnection -LocalPort 8080 -State Listen` a montre qu'un
processus `httpd` natif (installe avec la meme distribution PostgreSQL
native que l'incident 1, EnterpriseDB fournit un serveur Apache avec ses
outils, ex. pgAdmin) ecoutait deja sur le port 8080 de la machine hote,
en plus du mapping Docker du service `app`. Le serveur natif repondait a
la place du conteneur.

### Resolution

Meme solution que l'incident 1, transposee : exposer `app` sur le port
**8090** au lieu de 8080 (variable `APP_PORT`, `.env`/`.env.example`,
`docker-compose.yml`), et documenter ce choix dans `README.md`/
`app/README.md`.

### Mesures preventives

- Verification systematique de la disponibilite d'un port hote avant de
  l'exposer dans `docker-compose.yml`, plutot que de supposer qu'un port
  "standard" (5432, 8080) est libre.
- Les deux incidents partagent la meme cause racine (l'installation
  PostgreSQL native EnterpriseDB de la machine occupe plusieurs ports
  "attendus"), a garder en tete pour tout futur service ajoute a ce
  depot sur cette machine.

## Synthese

| | Port en conflit | Occupant reel | Detection | Resolution |
|---|---|---|---|---|
| Incident 1 (Phase 2) | 5432 | PostgreSQL natif (service Windows) | Erreur d'auth trompeuse (message mal decode) | Port 5433 |
| Incident 2 (Phase 4) | 8080 | Apache/EnterpriseDB natif | Reponse HTTP inattendue (page Apache au lieu de l'app) | Port 8090 |

Les deux incidents illustrent une meme lecon : sur une machine de
developpement partagee avec d'autres logiciels deja installes, ne jamais
supposer qu'un port par defaut est libre : le verifier, et documenter le
choix fait (voir aussi `docs/incidents/panne_db_simulee.md` pour un
incident de nature differente, une panne de dependance).
