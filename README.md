# Tennis Predictor

A full-stack tennis match prediction app that uses ATP match history, engineered player form features, and a trained machine learning model to predict the likely winner of a match.

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
- `backend.log` — backend output log
- `frontend.log` — frontend output log

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

Note: for convenience the repository includes a small demo dataset at `data/sample_atp_tennis.csv`. If you do not have the full `data/atp_tennis.csv` file, the backend can be run using this sample by setting the `DATA_PATH` environment variable to `data/sample_atp_tennis.csv`, or by copying `sample_atp_tennis.csv` to `data/atp_tennis.csv`.

Run script behavior: `run.sh` checks for `data/atp_tennis.csv`; if it's missing and `data/sample_atp_tennis.csv` exists, `run.sh` will automatically use the sample by setting `DATA_PATH`. If neither file exists, `run.sh` will exit and explain how to provide a dataset. To copy the sample into place for an easy demo, run:

```bash
cp data/sample_atp_tennis.csv data/atp_tennis.csv
```

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
    "pts2": 9800
  }'
```

Example response:

```json
{
  "winner": "Sinner"
}
```

## Model notes

The project uses a time-based train/test split so the model is evaluated on more recent data, which is a more realistic test of predictive power than random shuffling.

The current version performs around the mid-60% range on the out-of-time test split, which is reasonable for a tennis prediction demo but not strong enough to be considered a real betting or sports analytics product.

## Important limitations

This is a portfolio/demo project, not a production-grade betting system.

- it is trained on historical ATP data only
- it does not include live injury, fatigue, weather, or form context outside the dataset
- the model is a simple feature-based classifier rather than a full sports analytics pipeline
- predictions should be treated as educational/experimental, not investment advice