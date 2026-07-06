# Monitorage : Grafana

Tableau de bord Grafana lisant directement PostgreSQL (pas de service
intermediaire) via un role **lecture seule** dedie (`grafana_reader`, cree
par `db/sql/002_monitoring.sql`).

## Acces

```bash
docker compose up -d grafana
```

Puis ouvrir `http://127.0.0.1:${GRAFANA_PORT:-3000}` (identifiants :
`admin` / `GRAFANA_ADMIN_PASSWORD`, voir `.env`). Le datasource PostgreSQL
et le dashboard "Pricing industriel : monitorage" sont **provisionnes
automatiquement** au demarrage (fichiers sous `monitoring/grafana/`), rien
a configurer manuellement dans l'interface.

## Pre-requis

`db/sql/002_monitoring.sql` doit avoir ete applique (cree le role
`grafana_reader` + la vue `v_feature_drift`). Sur le volume Postgres de
developpement (deja initialise), l'appliquer manuellement une fois :

```bash
docker compose exec -T db psql -U pricing_user -d pricing_db < db/sql/002_monitoring.sql
```

(Sur un volume neuf, ce fichier s'applique automatiquement comme
`001_init_schema.sql`, cf. `db/README.md`.)

## Panels

| Panel | Source | Role |
|---|---|---|
| Volume de predictions | `prediction`, groupe par heure | Detecter un arret du trafic (ex: panne) ou un pic anormal |
| Latence `/predict` | `prediction.latence_ms`, moyenne + p95 | Detecter une degradation de performance |
| Distribution des prix predits | `prediction.prix_predit` | Reperer un decalage global des prix produits |
| Modele actif | `modele_entrainement`, dernier run | Verifier en un coup d'oeil quelle version/quelles metriques (R2/MAE/RMSE) sont en production |
| Derive des features | vue `v_feature_drift` | Voir la section suivante |

## Derive des donnees d'entree (`v_feature_drift`)

Le modele n'a pas de boucle de feedback (pas de prix de vente reel renvoye
apres une prediction), donc pas de vraie mesure de derive de
**performance** (MAE/R2 dans le temps) possible en production. Ce qu'on
peut surveiller, c'est la derive des **donnees d'entree** : est-ce que les
requetes `/predict` recentes ressemblent statistiquement au jeu
d'entrainement (`article`) ?

Pour `largeur_mm`, `hauteur_mm`, `complexity_factor` et `logistics_cost`,
la vue calcule :

```
z_score = (moyenne des 24 dernieres heures - moyenne d'entrainement) / ecart-type d'entrainement
```

Le panel colore `|z_score|` : vert (`< 2`), orange (`2-3`), rouge (`> 3`).
Un score eleve signifie que le modele est sollicite sur des dimensions/
complexites hors de son domaine d'entrainement : les predictions associees
sont potentiellement moins fiables, sans que l'API ne le signale d'elle-meme
(elle extrapole silencieusement).

**Limite assumee** : `recent_count` peut etre faible (peu de trafic sur ce
projet de demonstration), un z-score sur 1-2 points n'est pas
statistiquement robuste. A l'echelle d'un vrai volume de production, la
fenetre de 24h et le seuil de significativite seraient a recalibrer.

## Securite

`grafana_reader` n'a que `SELECT` sur les tables (`GRANT SELECT ... ALTER
DEFAULT PRIVILEGES`, voir `db/sql/002_monitoring.sql`) : Grafana ne peut
jamais modifier la base, meme si son mot de passe fuitait. Mot de passe
fixe dans ce depot de demonstration (comme `API_KEY`), a remplacer par un
secret genere en cas d'usage reel.
