# Code walkthrough

This guide goes through how the Tennis Predictor works. The basic idea is that the website collects the match details, the backend turns those details into model features, and the random forest predicts which player wins.

## How a prediction works

1. You enter two players and the match details in the frontend.
2. The frontend sends a request to the Flask API.
3. The backend checks the input and loads the match data.
4. The data preparation code calculates things like recent form, surface record, and head-to-head results using matches before the requested date.
5. The random forest uses those features to predict the winner.
6. The API sends the prediction back to the frontend.

The date matters. If the model uses results from the match it is predicting, or results that happened after it, that is data leakage. It can make evaluation look much better than real predictions would be. Since the dataset has dates but not match start times, this project only uses matches from earlier calendar dates when building historical features.

## The main files

| File | What it does |
| --- | --- |
| `backend/app.py` | Flask API, request checks, and prediction response. |
| `backend/prepare_data.py` | Loads and cleans match data and creates model features. |
| `backend/model.py` | Sets up the random forest and trains it when needed. |
| `backend/evaluate_model.py` | Tests the model on a later period and compares it with a ranking baseline. |
| `backend/model_tuner.py` | Optional hyperparameter search using time-series cross-validation. |
| `backend/inspect_data.py` | Small helper for looking at the dataset. |
| `frontend/src/App.jsx` | Match input form and prediction display. |
| `frontend/src/App.css` | Main frontend layout styles. |
| `tests/` | Tests for feature engineering, the API, and evaluation behavior. |
| `run.sh` | Sets up the local environment and starts both parts of the app. |

## What the model looks at

The model uses 19 features. They include the difference in player ranking and ranking points, surface and tournament round, recent win rates over the last 5 and 10 matches, recent results on the selected surface, and previous head-to-head results.

Many features describe one player compared with the other. For example, it can use the difference between their recent win rates rather than only looking at one player's number. The idea is to give the model a picture of how the two players compare before the match.

## Why the date is important

When you request a prediction for a match date, only matches strictly before that date should count as history. Results from the same date are left out too, because the dataset doesn't say which match started first. That is a conservative choice, but it avoids using information that might not have been available at prediction time.

The model's evaluation uses a chronological split: matches before January 1, 2024 are used for training, and matches on or after that date are held out for testing. This is closer to the real use case than randomly mixing old and new matches. The evaluation also compares against a basic baseline that predicts the player with the better ranking number.

Don't tune the model based on the held-out test results. If you keep adjusting it to improve that score, the test period stops being a fair check of how it generalizes.

## Run it

From the repository root, the simplest option is:

```bash
./run.sh
```

Then open `http://localhost:5173`. The API runs at `http://127.0.0.1:5000`.

To evaluate the model, run:

```bash
python -m backend.evaluate_model
```

To run the tests:

```bash
python -m unittest discover -s tests -v
```

If you started with `./run.sh`, use `.venv/bin/python` instead of `python` for those commands.

## What the metrics mean

- **Accuracy** is the share of predictions that were correct.
- **Precision** asks, among the matches predicted as Player 1 wins, how often Player 1 actually won.
- **Recall** asks, among actual Player 1 wins, how many the model found.
- **F1** combines precision and recall into one score.
- **Confusion matrix** shows correct and incorrect predictions for both classes.

Look at these together and compare the model to the ranking baseline. A good-looking accuracy number by itself doesn't tell the whole story. It also matters which seasons are in the dataset and how many matches were available for testing.

## Current limitations

The output is a winner label, not a calibrated probability. The model doesn't currently account for injuries, fatigue, travel, weather, withdrawals, or all the changes in a player's ability over time. The quality and date coverage of the CSV affect the results too. This is a learning project, so it shouldn't be used for betting or treated as a reliable forecast of a future match.
