"""Evaluate the classifier on the held-out chronological test period."""

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

try:
    from .model import build_model
    from .prepare_data import prepareData
except ImportError:  # Support running this file from the backend directory.
    from model import build_model
    from prepare_data import prepareData


def evaluate():
    X_train, X_test, y_train, y_test = prepareData()

    model = build_model()
    model.fit(X_train, y_train)
    model_predictions = model.predict(X_test)

    # Baseline: predict Player 1 only when their ranking number is better.
    rank_predictions = (X_test["Rank_Diff"] > 0).astype(int)

    results = {
        "model": {
            "accuracy": accuracy_score(y_test, model_predictions),
            "precision": precision_score(y_test, model_predictions, zero_division=0),
            "recall": recall_score(y_test, model_predictions, zero_division=0),
            "f1": f1_score(y_test, model_predictions, zero_division=0),
            "confusion_matrix": confusion_matrix(
                y_test, model_predictions, labels=[0, 1]
            ).tolist(),
        },
        "ranking_baseline": {
            "accuracy": accuracy_score(y_test, rank_predictions),
            "precision": precision_score(y_test, rank_predictions, zero_division=0),
            "recall": recall_score(y_test, rank_predictions, zero_division=0),
            "f1": f1_score(y_test, rank_predictions, zero_division=0),
            "confusion_matrix": confusion_matrix(
                y_test, rank_predictions, labels=[0, 1]
            ).tolist(),
        },
        "test_matches": int(len(y_test)),
    }

    print(f"Chronological held-out matches: {results['test_matches']}")
    for name in ("model", "ranking_baseline"):
        print(f"\n{name.replace('_', ' ').title()}")
        for metric in ("accuracy", "precision", "recall", "f1"):
            print(f"  {metric.title()}: {results[name][metric]:.3f}")
        print("  Confusion matrix (rows=true 0/1, columns=predicted 0/1):")
        print(f"  {results[name]['confusion_matrix']}")
    print("\nModel classification report:")
    print(classification_report(y_test, model_predictions, zero_division=0))
    return results


if __name__ == "__main__":
    evaluate()
