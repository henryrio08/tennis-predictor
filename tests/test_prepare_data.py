import unittest

import pandas as pd

from backend.prepare_data import add_recent_form_features


class RecentFormFeatureTests(unittest.TestCase):
    def setUp(self):
        self.matches = pd.DataFrame(
            [
                {"Date": "2024-01-01", "Player_1": "A", "Player_2": "B", "Surface": "Hard", "Winner": "A"},
                {"Date": "2024-01-02", "Player_1": "B", "Player_2": "A", "Surface": "Clay", "Winner": "B"},
                {"Date": "2024-01-03", "Player_1": "A", "Player_2": "B", "Surface": "Hard", "Winner": "B"},
            ]
        )

    def test_head_to_head_tracks_player_identity_when_order_reverses(self):
        featured = add_recent_form_features(self.matches)
        final_match = featured.iloc[2]

        self.assertEqual(final_match["H2H_P1"], 1)
        self.assertEqual(final_match["H2H_P2"], 1)
        self.assertEqual(final_match["H2H_Diff"], 0)

    def test_form_features_only_use_earlier_matches(self):
        featured = add_recent_form_features(self.matches)

        # B lost the first match, so B's form before the second match is zero.
        self.assertEqual(featured.iloc[1]["P1_Last_5"], 0)
        # The first match has no prior history and uses the documented neutral prior.
        self.assertEqual(featured.iloc[0]["P1_Last_5"], 0.5)

    def test_same_day_results_do_not_leak_between_matches(self):
        same_day = pd.DataFrame(
            [
                {"Date": "2024-01-01", "Player_1": "A", "Player_2": "B", "Surface": "Hard", "Winner": "A"},
                {"Date": "2024-01-01", "Player_1": "A", "Player_2": "C", "Surface": "Hard", "Winner": "A"},
            ]
        )
        featured = add_recent_form_features(same_day)

        self.assertEqual(featured.iloc[0]["P1_Last_5"], 0.5)
        self.assertEqual(featured.iloc[1]["P1_Last_5"], 0.5)

    def test_input_dataframe_is_not_mutated(self):
        original = self.matches.copy(deep=True)
        add_recent_form_features(self.matches)
        pd.testing.assert_frame_equal(self.matches, original)


if __name__ == "__main__":
    unittest.main()
