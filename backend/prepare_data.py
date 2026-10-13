import os

import pandas as pd


def rolling_win_rate(history, window):
    if not history:
        return 0.5
    recent = history[-window:]
    return sum(recent) / len(recent)


def add_recent_form_features(df):
    history = {}
    surface_history = {}
    h2h_counts = {}

    df = df.copy()

    for idx, row in df.iterrows():
        player_1 = row["Player_1"]
        player_2 = row["Player_2"]
        surface = row["Surface"]

        p1_history = history.setdefault(player_1, [])
        p2_history = history.setdefault(player_2, [])

        p1_surface_history = surface_history.setdefault((player_1, surface), [])
        p2_surface_history = surface_history.setdefault((player_2, surface), [])

        p1_last_5 = rolling_win_rate(p1_history, 5)
        p2_last_5 = rolling_win_rate(p2_history, 5)
        p1_last_10 = rolling_win_rate(p1_history, 10)
        p2_last_10 = rolling_win_rate(p2_history, 10)

        p1_surface_5 = rolling_win_rate(p1_surface_history, 5)
        p2_surface_5 = rolling_win_rate(p2_surface_history, 5)
        p1_surface_10 = rolling_win_rate(p1_surface_history, 10)
        p2_surface_10 = rolling_win_rate(p2_surface_history, 10)

        pair = tuple(sorted((player_1, player_2)))
        head_to_head = h2h_counts.setdefault(pair, {})

        df.at[idx, "P1_Last_5"] = p1_last_5
        df.at[idx, "P2_Last_5"] = p2_last_5
        df.at[idx, "P1_Last_10"] = p1_last_10
        df.at[idx, "P2_Last_10"] = p2_last_10
        df.at[idx, "Form_Diff_5"] = p1_last_5 - p2_last_5
        df.at[idx, "Form_Diff_10"] = p1_last_10 - p2_last_10

        df.at[idx, "P1_Surface_5"] = p1_surface_5
        df.at[idx, "P2_Surface_5"] = p2_surface_5
        df.at[idx, "P1_Surface_10"] = p1_surface_10
        df.at[idx, "P2_Surface_10"] = p2_surface_10
        df.at[idx, "Surface_Form_Diff_5"] = p1_surface_5 - p2_surface_5
        df.at[idx, "Surface_Form_Diff_10"] = p1_surface_10 - p2_surface_10

        # Store wins under each player's identity. Match order can reverse,
        # so counters named only P1/P2 would mix up the players' records.
        p1_h2h_wins = head_to_head.get(player_1, 0)
        p2_h2h_wins = head_to_head.get(player_2, 0)
        df.at[idx, "H2H_P1"] = p1_h2h_wins
        df.at[idx, "H2H_P2"] = p2_h2h_wins
        df.at[idx, "H2H_Diff"] = p1_h2h_wins - p2_h2h_wins

        player_1_won = int(row["Winner"] == player_1)
        player_2_won = int(row["Winner"] == player_2)

        p1_history.append(player_1_won)
        p2_history.append(player_2_won)
        p1_surface_history.append(player_1_won)
        p2_surface_history.append(player_2_won)

        head_to_head[player_1] = p1_h2h_wins + player_1_won
        head_to_head[player_2] = p2_h2h_wins + player_2_won

    return df


def prepareData():
    default_data = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "atp_tennis.csv")
    )
    data_path = os.environ.get("DATA_PATH", default_data)
    df = pd.read_csv(data_path)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date", kind="stable").reset_index(drop=True)

    df["Player_1_Wins"] = (df["Winner"] == df["Player_1"]).astype(int)
    df["Rank_Diff"] = df["Rank_2"] - df["Rank_1"]
    df["Pts_Diff"] = df["Pts_1"] - df["Pts_2"]
    df["Surface_Code"] = df["Surface"].map({
        "Hard": 0,
        "Clay": 1,
        "Grass": 2,
        "Carpet": 3,
    })
    df["Round_Code"] = df["Round"].map({
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
    }).fillna(0)

    df = add_recent_form_features(df)

    split_date = pd.Timestamp("2024-01-01")
    train = df[df["Date"] < split_date]
    test = df[df["Date"] >= split_date]

    features = [
        "Rank_Diff",
        "Pts_Diff",
        "Surface_Code",
        "Round_Code",
        "P1_Last_5",
        "P2_Last_5",
        "P1_Last_10",
        "P2_Last_10",
        "Form_Diff_5",
        "Form_Diff_10",
        "P1_Surface_5",
        "P2_Surface_5",
        "P1_Surface_10",
        "P2_Surface_10",
        "Surface_Form_Diff_5",
        "Surface_Form_Diff_10",
        "H2H_P1",
        "H2H_P2",
        "H2H_Diff",
    ]

    X_train = train[features]
    y_train = train["Player_1_Wins"]
    X_test = test[features]
    y_test = test["Player_1_Wins"]

    print("\nTraining matches:", len(train))
    print("Testing matches:", len(test))

    if train.empty or test.empty:
        raise ValueError(
            "The dataset must contain matches both before and on/after 2024-01-01 "
            "to create the configured chronological train/test split."
        )

    return X_train, X_test, y_train, y_test
