# Best performing model based on highest accuracy among tested models
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

from data_preprocessing import load_and_preprocess_data


def main():
    import pandas as pd
    import os

    # Load raw dataset
    project_root = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(project_root, "data", "diabetes.csv")
    df = pd.read_csv(data_path)

    X = df.drop("Outcome", axis=1)
    y = df["Outcome"]

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Create Pipeline
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('model', RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42
        ))
    ])

    # Train pipeline
    pipeline.fit(X_train, y_train)

    # Save entire pipeline
    model_save_path = os.path.join(os.path.dirname(__file__), "models", "random_forest_model.pkl")
    joblib.dump(pipeline, model_save_path)

    print("Pipeline model saved successfully!")


if __name__ == "__main__":
    main()
