from flask import Flask, request, jsonify
from flask_cors import CORS
from model import model
import pandas as pd
import os
import pathlib

# Allow overriding the data path via the DATA_PATH environment variable.
# Default to the repository-relative `data/atp_tennis.csv` file.
DEFAULT_DATA = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "atp_tennis.csv")
)
DATA_PATH = os.environ.get("DATA_PATH", DEFAULT_DATA)

df = pd.read_csv(DATA_PATH)
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date").reset_index(drop=True)


def recent_win_rate(player, data, window):
    matches = data[(data["Player_1"] == player) | (data["Player_2"] == player)].copy()
    history = []

    for _, row in matches.iterrows():
        if row["Winner"] == player:
            history.append(1)
        else:
            history.append(0)

    if not history:
        return 0.5

    recent = history[-window:]
    return sum(recent) / len(recent)


def surface_recent_win_rate(player, surface, data, window):
    matches = data[
        ((data["Player_1"] == player) | (data["Player_2"] == player))
        & (data["Surface"] == surface)
    ].copy()
    history = []

    for _, row in matches.iterrows():
        if row["Winner"] == player:
            history.append(1)
        else:
            history.append(0)

    if not history:
        return 0.5

    recent = history[-window:]
    return sum(recent) / len(recent)


def head_to_head_count(player1, player2, data):
    matches = data[
        ((data["Player_1"] == player1) & (data["Player_2"] == player2))
        | ((data["Player_1"] == player2) & (data["Player_2"] == player1))
    ].copy()

    p1_wins = 0
    p2_wins = 0

    for _, row in matches.iterrows():
        if row["Winner"] == player1:
            p1_wins += 1
        elif row["Winner"] == player2:
            p2_wins += 1

    return p1_wins, p2_wins


app = Flask(__name__)
CORS(app)


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    required_fields = [
        "player1", "player2", "surface", "round",
        "rank1", "rank2", "pts1", "pts2"
    ]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    player1 = data["player1"]
    player2 = data["player2"]
    if player1 == player2:
        return jsonify({"error": "Choose two different players."}), 400

    surface = data["surface"]
    round_name = data["round"]

    try:
        rank1 = float(data["rank1"])
        rank2 = float(data["rank2"])
        pts1 = float(data["pts1"])
        pts2 = float(data["pts2"])
    except (TypeError, ValueError):
        return jsonify({"error": "Rank and points values must be numeric."}), 400

    if surface not in {"Hard", "Clay", "Grass", "Carpet"}:
        return jsonify({"error": "Invalid surface value."}), 400

    surface_code = {"Hard": 0, "Clay": 1, "Grass": 2, "Carpet": 3}[surface]
    round_code = {
        "1st Round": 1,
        "2nd Round": 2,
        "3rd Round": 3,
        "4th Round": 4,
        "Quarterfinals": 5,
        "Semifinals": 6,
        "Final": 7,
    }.get(round_name, 0)

    rank_diff = rank2 - rank1
    pts_diff = pts1 - pts2

    p1_last_5 = recent_win_rate(player1, df, 5)
    p2_last_5 = recent_win_rate(player2, df, 5)
    p1_last_10 = recent_win_rate(player1, df, 10)
    p2_last_10 = recent_win_rate(player2, df, 10)

    p1_surface_5 = surface_recent_win_rate(player1, surface, df, 5)
    p2_surface_5 = surface_recent_win_rate(player2, surface, df, 5)
    p1_surface_10 = surface_recent_win_rate(player1, surface, df, 10)
    p2_surface_10 = surface_recent_win_rate(player2, surface, df, 10)

    form_diff_5 = p1_last_5 - p2_last_5
    form_diff_10 = p1_last_10 - p2_last_10
    surface_form_diff_5 = p1_surface_5 - p2_surface_5
    surface_form_diff_10 = p1_surface_10 - p2_surface_10

    h2h_p1, h2h_p2 = head_to_head_count(player1, player2, df)
    h2h_diff = h2h_p1 - h2h_p2

    feature_vector = [
        rank_diff,
        pts_diff,
        surface_code,
        round_code,
        p1_last_5,
        p2_last_5,
        p1_last_10,
        p2_last_10,
        form_diff_5,
        form_diff_10,
        p1_surface_5,
        p2_surface_5,
        p1_surface_10,
        p2_surface_10,
        surface_form_diff_5,
        surface_form_diff_10,
        h2h_p1,
        h2h_p2,
        h2h_diff,
    ]

    prediction = model.predict([feature_vector])[0]
    winner = player1 if prediction == 1 else player2

    return jsonify({"winner": winner})


if __name__ == "__main__":
    app.run(debug=True)