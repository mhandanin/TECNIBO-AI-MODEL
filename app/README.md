# Application cliente — pricing industriel

Petite application web (FastAPI + HTML/JS vanilla) permettant de simuler un
prix depuis un formulaire, sans passer par `/docs` ou `curl`.

## Pourquoi un backend, pas juste une page HTML statique

`POST /predict` de l'API necessite une cle (`X-API-Key`). Si le JS du
navigateur appelait directement l'API avec cette cle, elle serait visible en
clair dans le code source de la page et dans l'onglet reseau des devtools.
Le backend `pricing_app` sert donc de **proxy** : le navigateur n'appelle
que `pricing_app` (memes origine, pas de CORS a gerer), qui relaie ensuite
la requete a l'API pricing en y ajoutant la cle cote serveur.

```
navigateur --(sans cle)--> pricing_app --(X-API-Key)--> pricing_api --(SQL)--> PostgreSQL
```

## Configuration

Variables lues depuis `.env` a la racine du depot (voir `.env.example`) :

| Variable | Role |
|---|---|
| `PRICING_API_BASE_URL` | URL de base de l'API pricing (defaut `http://127.0.0.1:8000`) |
| `API_KEY` | Meme cle que celle configuree cote API |

## Installation et lancement

```bash
# Depuis la racine du depot
pip install -e "./app[dev]"
uvicorn pricing_app.main:app --app-dir app/src --reload --port 8090
```

Puis ouvrir `http://127.0.0.1:8090`. L'API pricing (`api/`) doit deja
tourner (voir `api/README.md`).

> Port 8090 (pas 8080) : le 8080 est deja pris par un serveur natif sur
> certaines machines (Apache/EnterpriseDB installe avec PostgreSQL) --
> memes ports par defaut que `docker-compose.yml` (variable `APP_PORT`).

## Tests

```bash
pytest app/tests -v
```

Les tests ne dependent d'aucun service externe : l'appel a l'API pricing
(`_pricing_api_request` dans `main.py`) est mocke.
