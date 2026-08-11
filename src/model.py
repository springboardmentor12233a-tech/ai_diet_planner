import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from .preprocess import preprocess_data


def train_logistic_regression(csv_path):
    """
    Trains and evaluates a Logistic Regression model on the diabetes dataset.

    Args:
        csv_path (str): Path to diabetes CSV file

    Returns:
        accuracy (float)
        classification_report (str)
    """

    # Load dataset
    df = pd.read_csv(csv_path)

    # Preprocess data
    X, y = preprocess_data(df)

    # Stratified split to preserve class distribution
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # Initialize Logistic Regression model
    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        solver="lbfgs"
    )

    # Train model
    model.fit(X_train, y_train)

    # Predict
    y_pred = model.predict(X_test)

    # Evaluate
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    matrix = confusion_matrix(y_test, y_pred)

    # Console output
    print("\n--- TRAINING LOGISTIC REGRESSION MODEL ---")
    print(f"Model Accuracy: {accuracy:.4f}\n")
    print("Classification Report:\n", report)
    print("Confusion Matrix:\n", matrix)

    return accuracy, report
