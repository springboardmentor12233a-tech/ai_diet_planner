# src/train_svm.py

from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

from data_preprocessing import load_and_preprocess_data


def main():
    # Load data
    X_train, X_test, y_train, y_test = load_and_preprocess_data()

    # Pipeline: Scaling + SVM
    svm_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("svm", SVC(
            kernel="rbf",
            C=1.0,
            gamma="scale",
            class_weight="balanced",
            random_state=42
        ))
    ])

    # Train
    svm_pipeline.fit(X_train, y_train)

    # Predict
    y_pred = svm_pipeline.predict(X_test)

    # Evaluation
    accuracy = accuracy_score(y_test, y_pred)
    print("\n=== Support Vector Machine (SVM) Results ===")
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))


if __name__ == "__main__":
    main()
