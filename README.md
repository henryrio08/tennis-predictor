# Tennis Predictor

A full-stack tennis match prediction demo that combines a React interface, a Flask API, and a scikit-learn random forest to estimate which of two ATP players is more likely to win.

## What it uses

The model receives 19 features:

- ranking difference and ranking-points difference
- encoded court surface and tournament round
- each player's win rate over their previous 5 and 10 matches
- differences between the players' recent win rates
- each player's recent record on the selected surface and the corresponding differences
- head-to-head wins for each player and the difference

Recent-form, surface-form, and head-to-head features are computed using matches from earlier calendar dates only. Since the source data has dates rather than match start times, results from all matches on the same date are held out of one another's features.

## Tech stack

- Python, pandas, scikit-learn
- Flask + Flask-CORS
- React + Vite
- GitHub Actions for regression tests and frontend builds

## Project structure

- `backend/app.py` — prediction API and request validation
- `backend/model.py` — reproducible random-forest configuration and lazy training
- `backend/prepare_data.py` — chronological split and feature engineering
- `backend/evaluate_model.py` — held-out metrics compared with a ranking-only baseline
- `backend/model_tuner.py` — optional randomized hyperparameter search with time-series cross-validation
- `frontend/` — browser interface
- `data/atp_tennis.csv` — primary dataset
- `data/sample_atp_tennis.csv` — tiny sample for setup checks, not meaningful model evaluation
- `tests/` — feature-engineering, API, and metric regression tests

## Quick start

Requirements: Python 3, Node.js/npm, and the ATP dataset.

From the repository root:

```bash
python3 -m pip install -r requirements.txt
cd frontend && npm ci && cd ..
chmod +x run.sh
./run.sh
```

Open http://localhost:5173. The API listens on http://127.0.0.1:5000.

The launcher checks for Python, npm, and a dataset. It uses the main CSV when available and falls back to the sample CSV otherwise. The sample contains only a few rows; it exists to exercise the app and should not be used to claim model accuracy.

### Manual setup

Terminal 1 — backend:

```bash
python3 -m pip install -r requirements.txt
python3 backend/app.py
```

Terminal 2 — frontend:

```bash
cd frontend
npm ci
npm run dev
```

If your CSV is somewhere else, set `DATA_PATH` before starting the backend:

```bash
DATA_PATH=/absolute/path/to/atp_tennis.csv python3 backend/app.py
```

If the backend runs at a different address, copy `frontend/.env.example` to `frontend/.env.local` and set `VITE_API_URL` to the backend base URL. Restart Vite after changing environment variables.

## API

`POST /predict` expects JSON with two distinct player names, a supported surface and round, numeric ranks and points, and an optional `match_date` in `YYYY-MM-DD` format. If omitted, the backend uses its local system date. Only matches strictly before the requested date are used as history.

Example:

```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "player1": "Sinner",
    "player2": "Alcaraz",
    "surface": "Hard",
    "round": "Final",
    "rank1": 1,
    "rank2": 2,
    "pts1": 12000,
    "pts2": 9800,
    "match_date": "2026-10-20"
  }'
```

Example response:

```json
{"winner": "Sinner"}
```

A lightweight readiness endpoint is available at `GET /health`. It confirms the API loaded the dataset; the model is trained on the first prediction request rather than at server startup.

## Evaluate model quality

From the repository root, run:

```bash
python -m pip install -r requirements.txt
python -m backend.evaluate_model
```

The evaluation uses matches before 2024-01-01 for training and matches on or after that date for the held-out test period. It reports accuracy, precision, recall, F1, a confusion matrix, and a classification report. It also reports the same metrics for a simple baseline that predicts Player 1 when Player 1 has the better ranking number.

Interpret the metrics together:

- **Accuracy:** fraction of all held-out matches predicted correctly.
- **Precision:** among matches predicted as Player 1 wins, how often Player 1 actually won.
- **Recall:** among actual Player 1 wins, how many the model identified.
- **F1:** harmonic mean of precision and recall.
- **Confusion matrix:** counts correct and incorrect predictions for each class.

Do not report a metric without also recording the dataset version/size and test period. Compare against the baseline; a complicated model that does not beat a sensible baseline has not demonstrated added value. Do not tune hyperparameters against the held-out test set. The tuning script uses time-series cross-validation on the training period.

## Tests

From the repository root:

```bash
python -m unittest discover -s tests -v
python -m py_compile backend/app.py backend/model.py backend/prepare_data.py backend/model_tuner.py backend/evaluate_model.py
```

GitHub Actions runs the unit tests, Python compile checks, and frontend production build on pushes and pull requests to `main`.

## Limitations and next steps

This is a portfolio/learning project, not a production-grade betting system. The result is a winner label rather than a calibrated win probability. The model does not currently account for injuries, fatigue, travel, weather, withdrawals, odds, or changes in player ability beyond the included features. Ranking data quality and the date coverage of the CSV matter substantially. A more rigorous next step would be walk-forward evaluation across multiple seasons, probability calibration, and confidence intervals rather than optimizing only one test-period score.
