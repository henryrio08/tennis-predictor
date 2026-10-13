import unittest
from unittest.mock import Mock, patch

from backend.app import app


class PredictionApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.valid_payload = {
            "player1": "Sinner",
            "player2": "Alcaraz",
            "surface": "Hard",
            "round": "Final",
            "rank1": 1,
            "rank2": 2,
            "pts1": 12000,
            "pts2": 9800,
            "match_date": "2026-10-20",
        }

    def test_health_check_does_not_require_model_training(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")
        self.assertIn("dataset_matches", response.get_json())

    def test_rejects_non_json_request(self):
        response = self.client.post("/predict", data="not json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("JSON object", response.get_json()["error"])

    def test_rejects_missing_fields(self):
        response = self.client.post("/predict", json={"player1": "Sinner"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required fields", response.get_json()["error"])

    def test_rejects_same_player_even_with_different_case(self):
        payload = {**self.valid_payload, "player2": "sInNeR"}
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("different players", response.get_json()["error"])

    def test_rejects_invalid_surface(self):
        payload = {**self.valid_payload, "surface": "Moon"}
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("surface", response.get_json()["error"])

    def test_rejects_non_finite_numeric_values(self):
        payload = {**self.valid_payload, "rank1": "NaN"}
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("finite", response.get_json()["error"])

    def test_rejects_invalid_match_date(self):
        payload = {**self.valid_payload, "match_date": "2026-2-3"}
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("YYYY-MM-DD", response.get_json()["error"])

    def test_returns_winner_for_valid_request(self):
        fake_model = Mock()
        fake_model.predict.return_value = [1]
        with patch("backend.app.get_model", return_value=fake_model):
            response = self.client.post("/predict", json=self.valid_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"winner": "Sinner"})
        fake_model.predict.assert_called_once()

    def test_prediction_uses_only_matches_before_requested_date(self):
        fake_model = Mock()
        fake_model.predict.return_value = [0]
        with patch("backend.app.get_model", return_value=fake_model):
            response = self.client.post(
                "/predict",
                json={**self.valid_payload, "match_date": "2023-01-01"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"winner": "Alcaraz"})
        features = fake_model.predict.call_args.args[0][0]
        self.assertEqual(features[4:8], [0.5, 0.5, 0.5, 0.5])
        self.assertEqual(features[16:19], [0, 0, 0])


if __name__ == "__main__":
    unittest.main()
