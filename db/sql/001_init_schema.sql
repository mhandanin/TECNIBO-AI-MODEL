-- Schema PostgreSQL pour le pipeline de pricing industriel.
-- Traduction directe du MPD : docs/merise/MPD.md

CREATE TABLE materiau (
    id_materiau SERIAL PRIMARY KEY,
    nom         VARCHAR(100) NOT NULL UNIQUE,
    prix_m2     NUMERIC(10, 2) NOT NULL CHECK (prix_m2 > 0)
);

CREATE TABLE profile (
    id_profile    SERIAL PRIMARY KEY,
    nom           VARCHAR(100) NOT NULL UNIQUE,
    prix_unitaire NUMERIC(10, 2) NOT NULL CHECK (prix_unitaire > 0)
);

CREATE TABLE article (
    id_article        SERIAL PRIMARY KEY,
    largeur_mm        INTEGER NOT NULL CHECK (largeur_mm > 0),
    hauteur_mm        INTEGER NOT NULL CHECK (hauteur_mm > 0),
    surface_m2        NUMERIC(10, 4) NOT NULL CHECK (surface_m2 > 0),
    code_spp          VARCHAR(20) NOT NULL,
    complexity_factor NUMERIC(6, 4) NOT NULL,
    logistics_cost    NUMERIC(10, 2) NOT NULL,
    prix_reel         NUMERIC(12, 2) NOT NULL CHECK (prix_reel > 0),
    id_materiau       INTEGER NOT NULL REFERENCES materiau (id_materiau),
    id_profile        INTEGER NOT NULL REFERENCES profile (id_profile),
    date_import       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_article_code_spp ON article (code_spp);

CREATE TABLE modele_entrainement (
    id_entrainement   SERIAL PRIMARY KEY,
    nom_modele        VARCHAR(50) NOT NULL,
    version           VARCHAR(20) NOT NULL,
    date_entrainement TIMESTAMPTZ NOT NULL DEFAULT now(),
    hyperparametres   JSONB,
    r2                NUMERIC(6, 4),
    mae               NUMERIC(10, 2),
    rmse              NUMERIC(10, 2),
    nb_echantillons   INTEGER,
    chemin_artifact   TEXT,
    UNIQUE (nom_modele, version)
);

CREATE TABLE prediction (
    id_prediction          BIGSERIAL PRIMARY KEY,
    id_entrainement        INTEGER NOT NULL REFERENCES modele_entrainement (id_entrainement),
    horodatage             TIMESTAMPTZ NOT NULL DEFAULT now(),
    largeur_mm             INTEGER NOT NULL CHECK (largeur_mm > 0),
    hauteur_mm             INTEGER NOT NULL CHECK (hauteur_mm > 0),
    surface_m2             NUMERIC(10, 4) NOT NULL CHECK (surface_m2 > 0),
    materiau_prix_m2       NUMERIC(10, 2) NOT NULL,
    profile_prix_unitaire  NUMERIC(10, 2) NOT NULL,
    code_spp               VARCHAR(20) NOT NULL,
    complexity_factor      NUMERIC(6, 4) NOT NULL,
    logistics_cost         NUMERIC(10, 2) NOT NULL,
    prix_predit            NUMERIC(12, 2) NOT NULL,
    latence_ms             NUMERIC(10, 2),
    source                 VARCHAR(20) NOT NULL DEFAULT 'api'
);

CREATE INDEX idx_prediction_horodatage ON prediction (horodatage);
CREATE INDEX idx_prediction_entrainement ON prediction (id_entrainement);

COMMENT ON TABLE materiau IS 'Catalogue des materiaux et de leur prix au m2';
COMMENT ON TABLE profile IS 'Catalogue des profiles et de leur prix unitaire';
COMMENT ON TABLE article IS 'Historique des articles vendus, utilise comme jeu d''entrainement du modele';
COMMENT ON TABLE modele_entrainement IS 'Journal des entrainements du modele de prediction de prix (une ligne par run)';
COMMENT ON TABLE prediction IS 'Historique des predictions realisees en production par l''API';
