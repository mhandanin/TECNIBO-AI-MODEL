# API — pricing industriel

API REST (FastAPI) exposant le modele Ridge retenu en Phase 1
(`reports/phase1_analysis.md`). Documentation OpenAPI generee
automatiquement, disponible sur `/docs` (Swagger UI) et `/openapi.json`
une fois le serveur lance.

## Endpoints

| Methode | Route | Auth | Description |
|---|---|---|---|
| GET | `/health` | non | Etat du service (liveness) |
| GET | `/model/info` | non | Version et metriques (R2/MAE/RMSE) du modele actif |
| GET | `/catalogue` | non | Liste des materiaux/profiles valides pour `/predict` |
| POST | `/predict` | **oui** (`X-API-Key`) | Predit le prix d'un article (formule finale) |

Chaque appel a `/predict` est journalise dans la table `prediction`
(features d'entree, prix predit, latence, horodatage, modele utilise).

## Authentification

Cle API partagee, transmise dans le header `X-API-Key`, verifiee contre la
variable d'environnement `API_KEY` (`.env`). Le schema est declare comme
`APIKeyHeader` FastAPI : il apparait dans `/docs` (bouton "Authorize") et
dans `openapi.json` sous `components.securitySchemes`.

C'est un choix volontairement simple (secret partage, pas d'OAuth2/JWT) —
suffisant pour un service interne/demo ; a faire evoluer (cles par
utilisateur, rotation, rate limiting) pour un usage multi-clients reel.

## Dependances

- La base PostgreSQL de la Phase 2 doit tourner (`docker compose up -d db`
  depuis la racine du depot).
- Un modele doit avoir ete entraine et enregistre (`api/scripts/train_and_register.py`)
  avant de demarrer l'API — sinon `/predict` et `/model/info` renvoient une
  erreur 500 explicite.

## Installation

```bash
# Depuis la racine du depot
pip install -e "./ml"     # pricing_ml (feature engineering partage)
pip install -e "./api"    # pricing_api (fastapi, sqlalchemy, ...)
```

## Entrainer et enregistrer un modele

```bash
cd api/scripts
python train_and_register.py
```

Lit la table `article` (jointe a `materiau`/`profile`), evalue le modele sur
un split train/test 80/20 (metriques honnetes, sans fuite), puis reentraine
sur 100% des donnees pour l'artefact final. Sauvegarde :

- l'artefact modele (pipeline + encodeur SPP + ordre des colonnes) dans
  `api/model_artifacts/ridge_v<timestamp>.joblib` (non versionne, cf.
  `.gitignore` — regenerable a tout moment)
- une ligne dans `modele_entrainement` (version, hyperparametres, metriques,
  chemin de l'artefact)

Relancer ce script cree une nouvelle version, qui devient automatiquement le
modele actif au prochain appel de l'API (le plus recent
`date_entrainement` gagne).

## Lancer l'API

```bash
uvicorn pricing_api.main:app --app-dir api/src --reload
```

Puis ouvrir `http://127.0.0.1:8000/docs`.

## Exemple d'appel

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
        "largeur_mm": 1360,
        "hauteur_mm": 1794,
        "materiau": "Glass_Tempered_8",
        "profile": "Aluminium_Thermal",
        "code_spp": "8906",
        "complexity_factor": 1.094923,
        "logistics_cost": 16.13
      }'
```

Reponse :

```json
{
  "prix_predit": 181.8,
  "id_entrainement": 1,
  "nom_modele": "Ridge",
  "version": "20260702144144",
  "latence_ms": 10.4
}
```
