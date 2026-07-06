-- Phase 5 : role de lecture seule pour Grafana + vue de derive des features.
--
-- NOTE : docker-entrypoint-initdb.d ne s'execute qu'au tout premier
-- demarrage d'un volume Postgres vide. Sur un volume deja initialise
-- (cas du volume "pgdata" de developpement), appliquer ce fichier
-- manuellement :
--   docker compose exec -T db psql -U pricing_user -d pricing_db < db/sql/002_monitoring.sql

-- Role dedie a Grafana : lecture seule, jamais d'ecriture possible.
-- Mot de passe fixe (comme API_KEY/POSTGRES_PASSWORD ailleurs dans ce
-- depot) : simplification assumee pour un projet de demonstration, pas
-- un vrai secret de production. Doit correspondre a GRAFANA_DB_PASSWORD
-- dans .env / monitoring/grafana/provisioning/datasources/datasource.yml.
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'grafana_reader') THEN
        CREATE ROLE grafana_reader LOGIN PASSWORD 'change_me_grafana_reader';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE pricing_db TO grafana_reader;
GRANT USAGE ON SCHEMA public TO grafana_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafana_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO grafana_reader;

-- Derive des donnees d'entree : compare les features des predictions
-- recentes (derniere 24h) aux distributions du jeu d'entrainement
-- (article). z_score = (moyenne recente - moyenne baseline) / ecart-type
-- baseline -- |z| > 2 ou 3 suggere que le modele est sollicite hors de son
-- domaine d'entrainement (pas de fuite : ne lit jamais la table
-- "prediction" pour entrainer quoi que ce soit, seulement pour la
-- surveiller).
CREATE OR REPLACE VIEW v_feature_drift AS
WITH baseline AS (
    SELECT
        avg(largeur_mm) AS largeur_mean, stddev(largeur_mm) AS largeur_std,
        avg(hauteur_mm) AS hauteur_mean, stddev(hauteur_mm) AS hauteur_std,
        avg(complexity_factor) AS complexity_mean, stddev(complexity_factor) AS complexity_std,
        avg(logistics_cost) AS logistics_mean, stddev(logistics_cost) AS logistics_std
    FROM article
),
recent AS (
    SELECT
        avg(largeur_mm) AS largeur_mean,
        avg(hauteur_mm) AS hauteur_mean,
        avg(complexity_factor) AS complexity_mean,
        avg(logistics_cost) AS logistics_mean,
        count(*) AS n
    FROM prediction
    WHERE horodatage > now() - interval '24 hours'
)
SELECT
    'largeur_mm' AS feature,
    b.largeur_mean AS baseline_mean, b.largeur_std AS baseline_std,
    r.largeur_mean AS recent_mean, r.n AS recent_count,
    CASE WHEN b.largeur_std > 0 THEN (r.largeur_mean - b.largeur_mean) / b.largeur_std END AS z_score
FROM baseline b, recent r
UNION ALL
SELECT
    'hauteur_mm',
    b.hauteur_mean, b.hauteur_std,
    r.hauteur_mean, r.n,
    CASE WHEN b.hauteur_std > 0 THEN (r.hauteur_mean - b.hauteur_mean) / b.hauteur_std END
FROM baseline b, recent r
UNION ALL
SELECT
    'complexity_factor',
    b.complexity_mean, b.complexity_std,
    r.complexity_mean, r.n,
    CASE WHEN b.complexity_std > 0 THEN (r.complexity_mean - b.complexity_mean) / b.complexity_std END
FROM baseline b, recent r
UNION ALL
SELECT
    'logistics_cost',
    b.logistics_mean, b.logistics_std,
    r.logistics_mean, r.n,
    CASE WHEN b.logistics_std > 0 THEN (r.logistics_mean - b.logistics_mean) / b.logistics_std END
FROM baseline b, recent r;

GRANT SELECT ON v_feature_drift TO grafana_reader;
