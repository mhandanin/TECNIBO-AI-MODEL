# Modele Physique de Donnees (MPD) — PostgreSQL

Traduction directe du [MCD](MCD.md) en tables relationnelles. Cle primaire
soulignee (`PK`), cles etrangeres en italique (`FK`). DDL correspondant :
[`db/sql/001_init_schema.sql`](../../db/sql/001_init_schema.sql).

## MATERIAU

| Colonne | Type | Contrainte |
|---|---|---|
| id_materiau | SERIAL | **PK** |
| nom | VARCHAR(100) | NOT NULL, UNIQUE |
| prix_m2 | NUMERIC(10,2) | NOT NULL, > 0 |

## PROFILE

| Colonne | Type | Contrainte |
|---|---|---|
| id_profile | SERIAL | **PK** |
| nom | VARCHAR(100) | NOT NULL, UNIQUE |
| prix_unitaire | NUMERIC(10,2) | NOT NULL, > 0 |

## ARTICLE

| Colonne | Type | Contrainte |
|---|---|---|
| id_article | SERIAL | **PK** |
| largeur_mm | INTEGER | NOT NULL, > 0 |
| hauteur_mm | INTEGER | NOT NULL, > 0 |
| surface_m2 | NUMERIC(10,4) | NOT NULL, > 0 |
| code_spp | VARCHAR(20) | NOT NULL |
| complexity_factor | NUMERIC(6,4) | NOT NULL |
| logistics_cost | NUMERIC(10,2) | NOT NULL |
| prix_reel | NUMERIC(12,2) | NOT NULL, > 0 |
| id_materiau | INTEGER | *FK* -> materiau(id_materiau), NOT NULL |
| id_profile | INTEGER | *FK* -> profile(id_profile), NOT NULL |
| date_import | TIMESTAMPTZ | NOT NULL, DEFAULT now() |

Index : `code_spp` (recherches/aggregations par code de finition).

## MODELE_ENTRAINEMENT

| Colonne | Type | Contrainte |
|---|---|---|
| id_entrainement | SERIAL | **PK** |
| nom_modele | VARCHAR(50) | NOT NULL |
| version | VARCHAR(20) | NOT NULL |
| date_entrainement | TIMESTAMPTZ | NOT NULL, DEFAULT now() |
| hyperparametres | JSONB | nullable |
| r2 | NUMERIC(6,4) | nullable |
| mae | NUMERIC(10,2) | nullable |
| rmse | NUMERIC(10,2) | nullable |
| nb_echantillons | INTEGER | nullable |
| chemin_artifact | TEXT | nullable |

Contrainte : UNIQUE(nom_modele, version).

## PREDICTION

| Colonne | Type | Contrainte |
|---|---|---|
| id_prediction | BIGSERIAL | **PK** |
| id_entrainement | INTEGER | *FK* -> modele_entrainement(id_entrainement), NOT NULL |
| horodatage | TIMESTAMPTZ | NOT NULL, DEFAULT now() |
| largeur_mm | INTEGER | NOT NULL |
| hauteur_mm | INTEGER | NOT NULL |
| surface_m2 | NUMERIC(10,4) | NOT NULL |
| materiau_prix_m2 | NUMERIC(10,2) | NOT NULL |
| profile_prix_unitaire | NUMERIC(10,2) | NOT NULL |
| code_spp | VARCHAR(20) | NOT NULL |
| complexity_factor | NUMERIC(6,4) | NOT NULL |
| logistics_cost | NUMERIC(10,2) | NOT NULL |
| prix_predit | NUMERIC(12,2) | NOT NULL |
| latence_ms | NUMERIC(10,2) | nullable (mesuree cote API) |
| source | VARCHAR(20) | NOT NULL, DEFAULT 'api' |

Index : `horodatage` (requetes de monitorage par periode),
`id_entrainement` (jointure vers le modele utilise).

## Choix de conception notables

- `PREDICTION` denormalise volontairement les features (pas de FK vers
  `MATERIAU`/`ARTICLE`) : une prediction en production porte sur une saisie
  utilisateur libre, et doit rester un instantane fidele de ce qui a ete
  envoye a l'API, independamment de l'evolution ulterieure du catalogue.
- `MODELE_ENTRAINEMENT` sert de journal des entrainements (competence C4 —
  historisation du cycle de vie de la donnee/du modele) et de point
  d'ancrage pour le monitorage de derive en Phase 5 (comparer les
  metriques par version de modele dans le temps).
