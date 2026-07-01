# Phase 1 — Analyse exploratoire et justification du choix du modele

Genere a partir de `ml/eda.py` et `ml/compare_models.py`, sur
`data/raw/industrial_pricing_dataset_10000_rows.xlsx` (10 000 lignes, dataset generique/fictif).

## 1. Analyse exploratoire (EDA)

- **Valeurs manquantes** : aucune (0 sur les 15 colonnes apres feature engineering).
- **Valeurs aberrantes (regle IQR, k=1.5)** : concentrees sur `Article_price` (515),
  `Material_price_m2` (626) et les couts derives (`material_cost`,
  `complexity_material_cost`). Pas d'aberration sur les dimensions brutes
  (`Width_mm`, `Height_mm`) ni sur `Complexity_factor`/`Logistics_cost`.
  -> voir `reports/figures/01_target_distribution.png` (histogramme + boxplot).
- **Distributions des features** : `Width_mm`/`Height_mm` suivent une distribution
  quasi uniforme (bornes 500-6000mm / 500-3500mm), `Material_price_m2` et
  `Profile_price_unit` prennent des valeurs discretes (catalogue de prix par
  materiau/profile). -> `reports/figures/02_feature_distributions.png`.
- **Correlations avec `Article_price`** (`reports/figures/03_correlation_heatmap.png`) :
  tres fortes correlations lineaires avec `material_cost` et
  `complexity_material_cost` (features engineerees = Surface x prix materiau,
  et son produit par le facteur de complexite). Correlation plus faible mais
  non nulle avec `profile_cost` et `Logistics_cost`.
- **Effet du code SPP** (`reports/figures/05_spp_effect.png`) : ~400 codes distincts
  pour 10 000 lignes (~25 lignes/code). Le prix moyen par code varie nettement
  autour de la moyenne globale, ce qui justifie de le garder comme feature, mais
  **impose de calculer son encodage cible uniquement sur le jeu d'entrainement**
  (sinon fuite de donnees — voir Phase 0). C'est ce qui a ete corrige dans
  `ml/data_prep.py::SppEncoder` par rapport au script d'origine.

## 2. Modeles compares

Split train/test 80/20 (`random_state=42`), encodage SPP fit sur le train
uniquement, features standardisees pour les modeles lineaires (absent dans le
script d'origine). 5 modeles evalues : `LinearRegression`, `Ridge`,
`ElasticNetCV` (modele d'origine), `RandomForestRegressor`, `GradientBoostingRegressor`.

## 3. Tableau comparatif

| Modele | R2 (test) | MAE (test) | RMSE (test) | R2 CV (train, 5-fold) | Temps entrainement (s) |
|---|---|---|---|---|---|
| LinearRegression | 0.9999 | 4.05 EUR | 5.10 EUR | 0.9999 +/- 0.0000 | 0.17 |
| Ridge | 0.9999 | 4.09 EUR | 5.16 EUR | 0.9999 +/- 0.0000 | 0.01 |
| GradientBoosting | 0.9996 | 6.41 EUR | 9.15 EUR | 0.9997 +/- 0.0001 | 1.72 |
| RandomForest | 0.9996 | 6.02 EUR | 9.51 EUR | 0.9996 +/- 0.0001 | 2.01 |
| ElasticNetCV | 0.9980 | 13.30 EUR | 21.47 EUR | 0.9982 +/- 0.0001 | 0.55 |

Figures : `reports/figures/06_model_comparison_metrics.png` (barres R2/MAE/temps),
`07_feature_importance_best_model.png` (coefficients standardises du meilleur
modele), `08_predicted_vs_actual_best_model.png` (nuage predit vs reel).

## 4. Conclusion argumentee

Le dataset est generateur d'une relation **quasi parfaitement lineaire** entre
les features engineerees (`material_cost`, `profile_cost`,
`complexity_material_cost`, `SPP_price`, `Logistics_cost`) et `Article_price`
(R2 = 0.9999 pour une simple regression lineaire, sans aucune regularisation
ni non-linearite). Consequences pour le choix du modele :

- **`LinearRegression`/`Ridge` dominent** les modeles plus complexes
  (`RandomForest`, `GradientBoosting`) sur toutes les metriques (R2, MAE, RMSE)
  *et* sur le temps d'entrainement. Les modeles a base d'arbres n'apportent
  aucune valeur ici car ils approxi ment une fonction lineaire par des marches
  d'escalier, ce qui degrade legerement la precision (MAE ~6 EUR vs ~4 EUR).
- **`ElasticNetCV`, le modele utilise dans le script d'origine, est le moins bon
  des 5** (MAE = 13.30 EUR, 3x pire que `LinearRegression`). La regularisation
  L1/L2 n'apporte rien quand (a) le nombre d'observations (8000 en train) est
  tres grand par rapport au nombre de features (9) et (b) il n'y a pas de
  colinearite forte necessitant une penalisation. Elle biaise au contraire les
  coefficients vers 0, ce qui degrade la precision.
- **Modele retenu : `Ridge`** (regression lineaire avec une legere penalisation
  L2, alpha=1.0) plutot que `LinearRegression` pure : performance quasiment
  identique (R2 0.9999 dans les deux cas, ecart de MAE de 0.04 EUR,
  negligeable), mais `Ridge` reste plus robuste si de nouvelles categories de
  materiaux/profiles avec des prix plus correles apparaissent en production
  (legere colinearite potentielle entre `material_cost` et
  `complexity_material_cost`, qui sont tous deux fonction de `Surface_m2` et
  `Material_price_m2`). Cet ecart de robustesse ne se voit pas sur ce dataset
  synthetique mais constitue une garantie peu couteuse pour la mise en
  production (Phase 3).

**A documenter dans le rapport de certification** : ce resultat illustre un
principe important — un modele plus complexe (arbres, ensembles) n'est pas
toujours meilleur ; le choix doit etre justifie par la nature du probleme
(ici, une relation lineaire connue et peu bruitee) et non par defaut vers le
modele le plus sophistique.

## Correspondance avec le referentiel RNCP37827

Cette phase couvre typiquement les competences liees a l'analyse du jeu de
donnees et au choix argumente d'un algorithme (selon les versions du
referentiel, souvent numerotees autour de C6-C8, bloc 2). **A verifier et
ajuster avec le libelle exact de votre referentiel** avant de citer ces
numeros dans vos rapports E1-E5 — je n'ai pas le texte officiel sous les
yeux, seulement le decoupage de phases que vous m'avez donne (qui commence a
C4 en Phase 2).
