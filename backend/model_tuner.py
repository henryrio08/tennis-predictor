from scipy.stats import randint
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit

try:
    from .prepare_data import prepareData
except ImportError:  # Support running this file from the backend directory.
    from prepare_data import prepareData


def tune_model():
    X_train, X_test, y_train, y_test = prepareData()

    param_distributions = {
        "n_estimators": randint(100, 1000),
        "max_depth": randint(1, 20),
        "min_samples_split": randint(2, 20),
        "min_samples_leaf": randint(1, 20),
        "max_features": ["sqrt", "log2", None],
        "class_weight": ["balanced", "balanced_subsample", None],
    }

    search = RandomizedSearchCV(
        RandomForestClassifier(random_state=42),
        param_distributions,
        n_iter=50,
        cv=TimeSeriesSplit(n_splits=5),
        scoring="accuracy",
        random_state=42,
        n_jobs=-1,
    )
    search.fit(X_train, y_train)

    test_predictions = search.best_estimator_.predict(X_test)
    print("Best parameters:", search.best_params_)
    print("Best chronological CV accuracy:", round(search.best_score_, 4))
    print("Held-out test accuracy:", round(accuracy_score(y_test, test_predictions), 4))
    return search.best_estimator_


if __name__ == "__main__":
    tune_model()
