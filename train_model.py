import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_curve,
    roc_auc_score
)

from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier


# ===============================
# 1. Load Dataset
# ===============================
df = pd.read_csv("data/diabetes.csv")
print("Dataset Loaded")
print(df.head())


# ===============================
# 2. Data Cleaning
# ===============================
cols_with_zero = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']

for col in cols_with_zero:
    df[col] = df[col].replace(0, np.nan)
    df[col] = df[col].fillna(df[col].mean())


# ===============================
# 3. Split Features & Target
# ===============================
X = df.drop("Outcome", axis=1)
y = df["Outcome"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ===============================
# 4. Handle Class Imbalance (SMOTE)
# ===============================
smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)


# ===============================
# 5. Train XGBoost Model
# ===============================
xgb = XGBClassifier(
    n_estimators=500,
    max_depth=5,
    learning_rate=0.03,
    subsample=0.9,
    colsample_bytree=0.9,
    scale_pos_weight=len(y_train_smote[y_train_smote == 0]) /
                      len(y_train_smote[y_train_smote == 1]),
    eval_metric="logloss",
    random_state=42
)

xgb.fit(X_train_smote, y_train_smote)


# ===============================
# 6. Default Prediction
# ===============================
y_pred_default = xgb.predict(X_test)
default_acc = accuracy_score(y_test, y_pred_default)

print("\nXGBoost Accuracy (Default Threshold 0.5):", default_acc)


# ===============================
# 7. Threshold Optimization
# ===============================
y_probs = xgb.predict_proba(X_test)[:, 1]

fpr, tpr, thresholds = roc_curve(y_test, y_probs)
j_scores = tpr - fpr
best_threshold = thresholds[j_scores.argmax()]

y_pred_opt = (y_probs >= best_threshold).astype(int)
opt_acc = accuracy_score(y_test, y_pred_opt)

print("Best Threshold:", best_threshold)
print("Optimized Accuracy:", opt_acc)


# ===============================
# 8. ROC-AUC Score
# ===============================
auc = roc_auc_score(y_test, y_probs)
print("ROC-AUC Score:", auc)


# ===============================
# 9. Classification Report
# ===============================
print("\nClassification Report (Optimized Threshold):\n")
print(classification_report(y_test, y_pred_opt))


# ===============================
# 10. Cross-Validation Score
# ===============================
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(xgb, X, y, cv=cv, scoring="accuracy")

print("Cross-Validation Accuracy Scores:", cv_scores)
print("Mean CV Accuracy:", cv_scores.mean())
