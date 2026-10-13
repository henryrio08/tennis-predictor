from functools import lru_cache

from sklearn.ensemble import RandomForestClassifier

try:
    from .prepare_data import prepareData
except ImportError:  # Support running this file from the backend directory.
    from prepare_data import prepareData


def build_model():
    """Create an unfitted classifier with reproducible settings."""
    return RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        max_depth=8,
        min_samples_leaf=5,
        max_features="sqrt",
    )


def train_model():
    """Fit on the chronological training split and return the fitted estimator."""
    X_train, _X_test, y_train, _y_test = prepareData()
    estimator = build_model()
    estimator.fit(X_train, y_train)
    return estimator


@lru_cache(maxsize=1)
def get_model():
    """Train once per backend process, on the first prediction request."""
    return train_model()


if __name__ == "__main__":
    trained_model = get_model()
    print(f"Model trained on {trained_model.n_features_in_} features.")
