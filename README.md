# Tennis Predictor

A full-stack tennis match prediction app that uses ATP match history, calculated player  features, and a trained machine learning model to predict the likely winner of a match.

## Overview

This project combines:

- Python + Flask for the backend API
- scikit-learn for the prediction model
- React + Vite for the frontend interface
- ATP tennis data for historical match features

The app predicts who is more likely to win based on factors such as:

- player ranking difference
- ranking points difference
- surface type
- match round
- recent form over the last 5 and 10 matches
- surface-specific recent form
- head-to-head history

## Project structure

- `backend/` — Flask API, feature engineering, and model logic
- `frontend/` — React UI
- `data/` — ATP tennis dataset used for training and prediction
- `run.sh` — one-click startup script for the full app
- `tests/` — regression tests for feature engineering

## Tech stack

- Python 3
- Flask
- Flask-CORS
- pandas
- scikit-learn
- React
- Vite

## Quick start

From the project root:

```bash
chmod +x run.sh
./run.sh
```

Then open:

```text
http://localhost:5173
```

The script will:

1. install backend dependencies
2. start the Flask API
3. install frontend dependencies if needed
4. start the React dev server

The repository includes the main dataset at `data/atp_tennis.csv`. If you use a different CSV, point the app at it with `DATA_PATH=/path/to/your.csv`. The startup script also supports an optional `data/sample_atp_tennis.csv` file if you add one locally; that sample file is not currently included in the repository.

## Manual setup

### Backend

```bash
cd backend
python3 -m pip install flask flask-cors pandas scikit-learn
python3 app.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

## API usage

The backend exposes a POST endpoint at:

```text
http://127.0.0.1:5000/predict
```

Example request:

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
{
  "winner": "Sinner"
}
```

## Model notes

The project uses a chronological train/test split: matches before 2024-01-01 are used for training, and matches on or after that date are held out for testing. Recent-form and head-to-head features are built from earlier dates only; matches on the same date are grouped so their results do not leak into one another's features.

Run the model script to calculate accuracy on the current dataset. Recalculate this metric whenever the data or feature pipeline changes instead of treating a previous score as guaranteed.

## Important limitations

This is a portfolio/demo project, not a production-grade betting system.

- it is trained on historical ATP data only
- prediction history is limited to matches before the requested `match_date` (defaults to today's date)
- it does not include live injury, fatigue, weather, or form context outside the dataset
- the model is a simple feature-based classifier rather than a full sports analytics pipeline
- predictions should be treated as educational/experimental, not investment advice

## Tests

From the repository root, run:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m py_compile backend/app.py backend/model.py backend/prepare_data.py backend/model_tuner.py
```
