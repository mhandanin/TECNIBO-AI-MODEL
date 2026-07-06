# Incident simule : panne de la base de donnees

**Type** : simule et **reellement execute** pendant l'implementation de la
Phase 5 (pas un scenario hypothetique), `api`/`app`/`grafana` tournaient
via `docker compose up -d`, un modele etait deja enregistre et servait des
predictions. Objectif : verifier que le monitorage mis en place (readiness
probe, logs structures, dashboard Grafana) permet reellement de detecter
et diagnostiquer une panne de dependance.

## Chronologie (horodatages UTC reels)

| Heure | Evenement |
|---|---|
| 09:14:26 | Etat normal : `GET /health/ready` -> 200 |
| 09:15:05 | **Declenchement** : `docker compose stop db` |
| 09:15:32 | Detection : voir ci-dessous |
| 09:17:15 | **Resolution** : `docker compose start db` |
| 09:17:54 | Retour a la normale confirme (~39s apres redemarrage de la DB) |

## Detection

Trois signaux independants ont confirme l'incident, chacun avec un role
different :

**1. La liveness reste verte (comportement attendu, pas un faux negatif)** :
```
GET /health -> 200 {"status":"ok"}
```
Le processus `api` tourne toujours : `/health` ne verifie que ca
(liveness). Sans la readiness probe ajoutee en Phase 5, rien d'autre
n'aurait signale le probleme via l'API elle-meme.

**2. La readiness probe detecte la panne** (`GET /health/ready`, ajoutee
specifiquement pour ce cas) :
```json
{"status":"unavailable","detail":"(psycopg2.OperationalError) server closed the connection unexpectedly\n\tThis probably means the server terminated abnormally..."}
```
Status HTTP `503` en ~26ms, assez rapide pour un healthcheck
d'orchestrateur (Kubernetes readinessProbe, load balancer, etc.).

**3. Le dashboard Grafana signale le datasource en erreur** :
```
GET /api/datasources/uid/pricing_postgres/health
-> {"message":"driver: bad connection","status":"ERROR"}
```
Un operateur regardant le dashboard verrait le panel "Modele actif" /
"Derive des features" vides ou en erreur, et le panel "Volume de
predictions" cesser de se mettre a jour.

## Diagnostic

Log structure capture au moment de l'echec (`docker compose logs api`,
format JSON, voir `api/src/pricing_api/logging_config.py`) :

```json
{"timestamp": "2026-07-04T09:15:32.461...", "level": "ERROR", "logger": "pricing_api",
 "message": "readiness_check_failed",
 "exception": "...psycopg2.OperationalError: server closed the connection unexpectedly..."}
```

Un appel a un endpoint qui touche vraiment la base (`GET /catalogue`)
confirme et precise la cause racine : le nom de service Docker `db` ne
resout meme plus (le conteneur est arrete, pas juste inaccessible) :

```json
{"level": "ERROR", "message": "unhandled_exception", "path": "/catalogue",
 "exception": "...psycopg2.OperationalError: could not translate host name \"db\" to address: Name or service not known..."}
```

Cette deuxieme exception est interceptee par le handler generique
`@app.exception_handler(Exception)` (ajoute en Phase 5) : sans lui, cette
erreur aurait ete une trace non loggee, un 500 muet cote client, sans
aucune preuve dans les logs pour investiguer apres coup.

**Diagnostic** : la cause est la disponibilite de la dependance PostgreSQL,
pas un bug applicatif, confirme par le fait que `GET /health` (liveness)
reste vert pendant tout l'incident.

## Resolution

```bash
docker compose start db
```

Verification post-resolution (~39s apres) :
```
GET /health/ready -> 200 {"status":"ok"}
GET /catalogue    -> 200
Grafana datasource health -> {"message":"Database Connection OK","status":"OK"}
```

Aucune action manuelle sur `api`/`app`/`grafana` necessaire : SQLAlchemy
(pool de connexions) et le client Postgres de Grafana retablissent la
connexion automatiquement des que `db` redevient joignable.

## Mesures preventives / enseignements

- **La readiness probe (`/health/ready`) est la piece manquante qui a
  rendu cet incident diagnosticable** avant la Phase 5 : seule `/health`
  (toujours 200) existait, ce qui aurait masque une panne de la base
  derriere une apparence de service "en bonne sante".
- Le handler d'exception generique garantit qu'**aucune erreur inattendue
  ne reste silencieuse** : meme une route qui ne s'y attend pas (comme
  `/catalogue` ici) produit un log exploitable au lieu d'un 500 nu.
- En production, `docker-compose.yml` pourrait ajouter une
  `restart: unless-stopped` policy plus agressive avec `depends_on:
  condition: service_healthy` pour `api` (deja en place) combinee a une
  vraie sonde d'orchestrateur (Kubernetes `readinessProbe` pointant sur
  `/health/ready`) pour retirer automatiquement l'instance du load
  balancer pendant l'indisponibilite, au lieu de laisser les clients
  recevoir des 500/503.
- Le dashboard Grafana confirme son utilite d'**indicateur secondaire** :
  meme sans regarder les logs, l'etat "ERROR" du datasource est visible en
  un coup d'oeil.
