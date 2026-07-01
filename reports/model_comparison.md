| Modele | R2 (test) | MAE (test) | RMSE (test) | R2 CV (train, 5-fold) | Temps entrainement (s) |
|---|---|---|---|---|---|
| LinearRegression | 0.9999 | 4.05 EUR | 5.10 EUR | 0.9999 +/- 0.0000 | 0.02 |
| Ridge | 0.9999 | 4.09 EUR | 5.16 EUR | 0.9999 +/- 0.0000 | 0.01 |
| GradientBoosting | 0.9996 | 6.41 EUR | 9.15 EUR | 0.9997 +/- 0.0001 | 1.79 |
| RandomForest | 0.9996 | 6.02 EUR | 9.51 EUR | 0.9996 +/- 0.0001 | 2.17 |
| ElasticNetCV | 0.9980 | 13.30 EUR | 21.47 EUR | 0.9982 +/- 0.0001 | 0.51 |