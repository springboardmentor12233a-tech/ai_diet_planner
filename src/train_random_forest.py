# random_forest.py

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

from data_preprocessing import load_and_preprocess_data


def main():
    # Load data
    X_train, X_test, y_train, y_test = load_and_preprocess_data()

    # Random Forest model
    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42
    )

    # Train
    rf.fit(X_train, y_train)

    # Predict
    y_pred = rf.predict(X_test)

    # Evaluation
    accuracy = accuracy_score(y_test, y_pred)
    print("\n=== Random Forest Results ===")
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))


if __name__ == "__main__":
    main()
