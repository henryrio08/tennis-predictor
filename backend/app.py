import os
from datetime import date

import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from .model import get_model
except ImportError:  # Support `python app.py` from the backend directory.
    from model import get_model


DEFAULT_DATA = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "atp_tennis.csv")
)
DATA_PATH = os.environ.get("DATA_PATH", DEFAULT_DATA)

if not os.path.isfile(DATA_PATH):
    raise FileNotFoundError(
        f"Dataset not found at {DATA_PATH}. Set DATA_PATH to a valid ATP CSV file."
    )

df = pd.read_csv(DATA_PATH)
required_columns = {"Date", "Player_1", "Player_2", "Winner", "Surface"}
missing_columns = required_columns - set(df.columns)
if missing_columns:
    raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing_columns))}")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"]).sort_values("Date", kind="stable").reset_index(drop=True)


def recent_win_rate(player, data, window):
    matches = data[
        (data["Player_1"] == player) | (data["Player_2"] == player)
    ]
    if matches.empty:
        return 0.5

    wins = (matches["Winner"] == player).astype(int).tolist()
    recent = wins[-window:]
    return sum(recent) / len(recent)


def surface_recent_win_rate(player, surface, data, window):
    matches = data[
        ((data["Player_1"] == player) | (data["Player_2"] == player))
        & (data["Surface"] == surface)
    ]
    if matches.empty:
        return 0.5

    wins = (matches["Winner"] == player).astype(int).tolist()
    recent = wins[-window:]
    return sum(recent) / len(recent)


def head_to_head_count(player1, player2, data):
    matches = data[
        (
            (data["Player_1"] == player1) & (data["Player_2"] == player2)
        )
        | (
            (data["Player_1"] == player2) & (data["Player_2"] == player1)
        )
    ]
    p1_wins = int((matches["Winner"] == player1).sum())
    p2_wins = int((matches["Winner"] == player2).sum())
    return p1_wins, p2_wins


app = Flask(__name__)
CORS(app)

SURFACE_CODES = {"Hard": 0, "Clay": 1, "Grass": 2, "Carpet": 3}
ROUND_CODES = {
    "1st Round": 1,
    "2nd Round": 2,
    "3rd Round": 3,
    "4th Round": 4,
    "Quarterfinals": 5,
    "Semifinals": 6,
    "Final": 7,
    "Round Robin": 3,
    "Qualifying": 0,
    "Qualification": 0,
}


@app.route("/health", methods=["GET"])
def health():
    """Lightweight readiness check that does not train the model."""
    return jsonify({"status": "ok", "dataset_matches": int(len(df))})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    required_fields = [
        "player1", "player2", "surface", "round",
        "rank1", "rank2", "pts1", "pts2",
    ]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    player1, player2 = data["player1"], data["player2"]
    if not isinstance(player1, str) or not isinstance(player2, str):
        return jsonify({"error": "Player names must be strings."}), 400

    player1, player2 = player1.strip(), player2.strip()
    if not player1 or not player2:
        return jsonify({"error": "Player names cannot be empty."}), 400
    if player1.casefold() == player2.casefold():
        return jsonify({"error": "Choose two different players."}), 400

    surface, round_name = data["surface"], data["round"]
    if not isinstance(surface, str) or surface not in SURFACE_CODES:
        return jsonify({"error": "Invalid surface value."}), 400
    if not isinstance(round_name, str) or round_name not in ROUND_CODES:
        return jsonify({"error": "Invalid round value."}), 400

    try:
        numeric_values = [float(data[key]) for key in ("rank1", "rank2", "pts1", "pts2")]
    except (TypeError, ValueError):
        return jsonify({"error": "Rank and points values must be numeric."}), 400

    rank1, rank2, pts1, pts2 = numeric_values
    if not all(pd.notna(value) and abs(value) != float("inf") for value in numeric_values):
        return jsonify({"error": "Rank and points values must be finite numbers."}), 400
    if rank1 <= 0 or rank2 <= 0 or pts1 < 0 or pts2 < 0:
        return jsonify({
            "error": "Ranks must be greater than zero and points cannot be negative."
        }), 400

    match_date_value = data.get("match_date", date.today().isoformat())
    if not isinstance(match_date_value, str):
        return jsonify({"error": "match_date must be a date string in YYYY-MM-DD format."}), 400
    try:
        match_date = pd.to_datetime(match_date_value, format="%Y-%m-%d", errors="raise")
        if match_date.strftime("%Y-%m-%d") != match_date_value:
            raise ValueError("Date must use YYYY-MM-DD.")
    except (TypeError, ValueError):
        return jsonify({"error": "match_date must be a valid date in YYYY-MM-DD format."}), 400

    # No result from the requested date or any later date can affect the prediction.
    history = df[df["Date"] < match_date.normalize()]

    rank_diff = rank2 - rank1
    pts_diff = pts1 - pts2
    p1_last_5 = recent_win_rate(player1, history, 5)
    p2_last_5 = recent_win_rate(player2, history, 5)
    p1_last_10 = recent_win_rate(player1, history, 10)
    p2_last_10 = recent_win_rate(player2, history, 10)
    p1_surface_5 = surface_recent_win_rate(player1, surface, history, 5)
    p2_surface_5 = surface_recent_win_rate(player2, surface, history, 5)
    p1_surface_10 = surface_recent_win_rate(player1, surface, history, 10)
    p2_surface_10 = surface_recent_win_rate(player2, surface, history, 10)
    h2h_p1, h2h_p2 = head_to_head_count(player1, player2, history)

    feature_vector = [
        rank_diff, pts_diff, SURFACE_CODES[surface], ROUND_CODES[round_name],
        p1_last_5, p2_last_5, p1_last_10, p2_last_10,
        p1_last_5 - p2_last_5, p1_last_10 - p2_last_10,
        p1_surface_5, p2_surface_5, p1_surface_10, p2_surface_10,
        p1_surface_5 - p2_surface_5, p1_surface_10 - p2_surface_10,
        h2h_p1, h2h_p2, h2h_p1 - h2h_p2,
    ]

    prediction = get_model().predict([feature_vector])[0]
    winner = player1 if prediction == 1 else player2
    return jsonify({"winner": winner})


if __name__ == "__main__":
    app.run(debug=False)
