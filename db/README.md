# Base de donnees : pricing industriel

PostgreSQL 16, lance via Docker Compose. Schema Merise documente dans
[docs/merise/MCD.md](../docs/merise/MCD.md) et
[docs/merise/MPD.md](../docs/merise/MPD.md).

## Dependances

- Docker Desktop
- Python 3.11+ (pour le script d'import), avec le package `pricing_ml`
  installe (voir `ml/README` / racine du depot)

## Installation

```bash
# Depuis la racine du depot :
cp .env.example .env
# Adapter POSTGRES_PORT si 5432 est deja pris par une instance PostgreSQL
# native sur la machine (c'est le cas par defaut de ce depot : 5433).

docker compose up -d db
```

Le schema (`db/sql/001_init_schema.sql`) est applique automatiquement au
premier demarrage du conteneur (monte dans `/docker-entrypoint-initdb.d`).
Il en va de meme pour `db/sql/002_monitoring.sql` (role `grafana_reader`
en lecture seule + vue `v_feature_drift`, Phase 5, voir
[monitoring/README.md](../monitoring/README.md)) sur un volume neuf.

**Sur un volume deja initialise** (cas du volume de developpement de ce
depot), `docker-entrypoint-initdb.d` ne se rejoue pas automatiquement pour
les nouveaux fichiers SQL ajoutes apres coup. Appliquer manuellement :

```bash
docker compose exec -T db psql -U pricing_user -d pricing_db < db/sql/002_monitoring.sql
```

(Le script est idempotent, le rejouer ne pose pas de probleme.)

## Import du dataset

```bash
cd db/scripts
python -m venv ../../.venv          # si pas deja fait a la racine
pip install -r requirements.txt     # installe pricing_ml (ml/) + psycopg2 + sqlalchemy + dotenv
python import_dataset.py
```

Le script :
1. charge et nettoie `data/raw/industrial_pricing_dataset_10000_rows.xlsx`
   avec les memes regles que le pipeline d'entrainement (`pricing_ml.data`) ;
2. vide et recharge les tables `materiau`, `profile`, `article`
   (idempotent, ne touche jamais `prediction` ni `modele_entrainement`) ;
3. affiche un resume (nombre de lignes importees par table).

## Verifier

```bash
docker compose exec db psql -U pricing_user -d pricing_db -c "\dt"
docker compose exec db psql -U pricing_user -d pricing_db -c "SELECT count(*) FROM article;"
```

## Commandes utiles

```bash
docker compose down          # arreter (conserve les donnees, volume pgdata)
docker compose down -v       # arreter et supprimer les donnees (reinit complete)
docker compose logs -f db    # logs du conteneur Postgres
```
