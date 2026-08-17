from sklearn.ensemble import RandomForestClassifier
from prepare_data import prepareData
from sklearn.metrics import accuracy_score, precision_score


def train_model():
    X_train, X_test, y_train, y_test = prepareData()

    model = RandomForestClassifier(
        n_estimators=500,
        random_state=42,
        max_depth=8,
        min_samples_leaf=5,
        max_features='sqrt'
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions)
    feature_importances = model.feature_importances_

    for feature, importance in sorted(zip(X_train.columns, feature_importances), key=lambda x: x[1], reverse=True):
        print(feature, round(importance, 4))
    print("Accuracy:", accuracy)
    print("Precision:", precision)

    return model


model = train_model()


if __name__ == "__main__":
    print("Model is trained and ready.")