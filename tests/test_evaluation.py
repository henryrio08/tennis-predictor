import unittest

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


class EvaluationMetricTests(unittest.TestCase):
    def test_metric_definitions_for_known_predictions(self):
        # Labels are 1 when Player 1 wins.
        actual = [1, 1, 0, 0]
        predicted = [1, 0, 0, 0]

        self.assertEqual(accuracy_score(actual, predicted), 0.75)
        self.assertEqual(precision_score(actual, predicted, zero_division=0), 1.0)
        self.assertEqual(recall_score(actual, predicted, zero_division=0), 0.5)
        self.assertAlmostEqual(f1_score(actual, predicted, zero_division=0), 2 / 3)


if __name__ == "__main__":
    unittest.main()
