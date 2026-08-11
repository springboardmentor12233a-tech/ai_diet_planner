from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import pandas as pd

def train_svm_model(dataset_path):
    # Load dataset
    df = pd.read_csv(dataset_path)

    # Preprocess features and target
    from preprocess import preprocess_data
    X_scaled, y = preprocess_data(df)

    # Optional: Handle class imbalance with SMOTE
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X_scaled, y)

    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X_res, y_res, test_size=0.2, random_state=42, stratify=y_res
    )

    # Train SVM classifier
    svm_model = SVC(
        kernel='rbf',       # Radial Basis Function kernel
        C=1.0,              # Regularization parameter
        gamma='scale',      # Kernel coefficient
        class_weight='balanced',  # Handle class imbalance
        random_state=42
    )

    svm_model.fit(X_train, y_train)

    # Make predictions
    y_pred = svm_model.predict(X_test)

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    print("\n--- MODEL PERFORMANCE (SVM) ---")
    print(f"Model Accuracy: {accuracy:.4f}")
    print("\nClassification Report:\n", report)
    print("\nConfusion Matrix:\n", cm)

    return accuracy, report

