# pima_diabetes_final_regularized.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# ---------------------------
# 1. Load Dataset
# ---------------------------
df = pd.read_csv('data/diabetes.csv')

# ---------------------------
# 2. Advanced Imputation
# ---------------------------
cols_to_fix = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
for col in cols_to_fix:
    df[col] = df[col].replace(0, np.nan)
    df[col] = df[col].fillna(df.groupby('Outcome')[col].transform('median'))

# ---------------------------
# 3. Features & Target
# ---------------------------
features = [
    'Pregnancies','Glucose','BloodPressure','SkinThickness',
    'Insulin','BMI','DiabetesPedigreeFunction','Age'
]
X = df[features]
y = df['Outcome']

# ---------------------------
# 4. Scaling
# ---------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ---------------------------
# 5. Train-Test Split
# ---------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y,
    test_size=0.25,
    stratify=y,
    random_state=42
)

# ---------------------------
# 6. Baseline Models
# ---------------------------
lr = LogisticRegression(max_iter=1000, class_weight='balanced')
lr.fit(X_train, y_train)

svm = SVC(kernel='rbf', C=50, gamma=0.01, class_weight='balanced', probability=True)
svm.fit(X_train, y_train)

rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=6,
    min_samples_leaf=3,
    random_state=42
)
rf.fit(X_train, y_train)

# ---------------------------
# 7. Regularized XGBoost
# ---------------------------
xgb = XGBClassifier(
    eval_metric='logloss',
    random_state=42,
    reg_alpha=0.5,
    reg_lambda=1.0,
    min_child_weight=3
)

param_grid = {
    'n_estimators': [120, 150, 180],
    'max_depth': [3, 4],
    'learning_rate': [0.03, 0.05],
    'subsample': [0.7, 0.8],
    'colsample_bytree': [0.7, 0.8]
}

grid = GridSearchCV(
    xgb,
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)

grid.fit(X_train, y_train)
best_xgb = grid.best_estimator_

# ---------------------------
# 8. Evaluation
# ---------------------------
train_acc = accuracy_score(y_train, best_xgb.predict(X_train))
test_acc = accuracy_score(y_test, best_xgb.predict(X_test))
roc_auc = roc_auc_score(y_test, best_xgb.predict_proba(X_test)[:, 1])

print("\n----- Baseline Models -----")
print(f"Logistic Regression Test Accuracy: {accuracy_score(y_test, lr.predict(X_test)):.3f}")
print(f"SVM Test Accuracy: {accuracy_score(y_test, svm.predict(X_test)):.3f}")
print(f"Random Forest Test Accuracy: {accuracy_score(y_test, rf.predict(X_test)):.3f}")

print("\n----- Regularized XGBoost Results -----")
print(f"Best Parameters: {grid.best_params_}")
print(f"Training Accuracy: {train_acc:.3f}")
print(f"Testing Accuracy: {test_acc:.3f}")
print(f"ROC-AUC Score: {roc_auc:.3f}")

print("\nClassification Report:\n")
print(classification_report(y_test, best_xgb.predict(X_test)))

# ---------------------------
# 9. Feature Importance
# ---------------------------
importances = pd.Series(
    best_xgb.feature_importances_,
    index=features
).sort_values(ascending=False)

print("\nFeature Importance:\n")
print(importances)
