# industrial-pricing-ai

Projet personnel de reconstruction d'un pipeline ML complet (donnees -> modele
-> API -> application -> monitorage) pour la certification RNCP37827
(Developpeur en Intelligence Artificielle).

Le projet part d'un cas d'usage industriel simple : predire le prix d'un
article sur-mesure (`Article_price`) a partir de ses dimensions, de son
materiau, de son profile et d'options de finition. Les donnees utilisees sont
**generiques/fictives** (aucune donnee reelle d'entreprise).

## Etat d'avancement

- [x] Phase 1 - Analyse exploratoire et choix du modele (`ml/`, `reports/`)
- [ ] Phase 2 - Base de donnees PostgreSQL (`db/`)
- [ ] Phase 3 - API REST du modele (`api/`)
- [ ] Phase 4 - Application + tests + CI/CD (`app/`, `.github/workflows/`)
- [ ] Phase 5 - Monitorage et gestion d'incident

## Structure du depot

```
industrial-pricing-ai/
├── data/raw/            # dataset d'entrainement (fictif)
├── ml/                  # EDA, comparaison de modeles, entrainement
├── reports/             # figures PNG + rapports markdown pour la certification
├── db/                  # (Phase 2) schema PostgreSQL, scripts d'import
├── api/                 # (Phase 3) API REST exposant le modele
├── app/                 # (Phase 4) application consommant l'API
└── .github/workflows/   # (Phase 4) CI/CD
```

## Phase 1 - Analyse et choix du modele

Voir [reports/phase1_analysis.md](reports/phase1_analysis.md) pour le detail
(EDA, comparaison de 5 modeles, conclusion argumentee).

### Reproduire

```bash
python -m venv .venv
.venv/Scripts/activate       # ou source .venv/bin/activate sous Linux/Mac
pip install -r ml/requirements.txt

python ml/eda.py              # genere reports/figures/01..05
python ml/compare_models.py   # genere reports/figures/06..08 + reports/model_comparison.{md,csv}
```
