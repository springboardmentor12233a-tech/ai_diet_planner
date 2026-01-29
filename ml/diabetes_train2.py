import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split, RepeatedStratifiedKFold, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier

# 1. Load data
df = pd.read_csv('../datasets/diabetes.csv')

# 2. Imputation (Keeping your logic for zeros)
cols_to_fix = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
for col in cols_to_fix:
    df[col] = df[col].replace(0, np.nan)
    df[col] = df[col].fillna(df.groupby('Outcome')[col].transform('median'))

# 3. FEATURE ENGINEERING: Creating interactions
df['Glucose_BMI'] = df['Glucose'] * df['BMI']
df['Age_Glucose'] = df['Age'] * df['Glucose']
df['Insulin_Efficiency'] = df['Insulin'] / (df['Glucose'] + 1)

X = df.drop('Outcome', axis=1)
y = df['Outcome']

# 4. Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 5. Use RobustScaler (Better for data with outliers like Insulin)
# Scale only on training data to avoid data leakage
scaler = RobustScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 6. Advanced Cross-Validation
# Repeated K-Fold ensures the 86% isn't just a "lucky" split
cv_strategy = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=42)

# 7. Fine-Tuned XGBoost
xgb = XGBClassifier(eval_metric='logloss', random_state=42)

param_grid = {
    'n_estimators': [200, 400],
    'max_depth': [3, 4],
    'learning_rate': [0.01, 0.03],
    'gamma': [0.1, 0.2],         # Minimum loss reduction to make a split
    'reg_lambda': [1, 5],        # L2 regularization
    'scale_pos_weight': [1.8]    # High weight for the minority class (Diabetes cases)
}

grid = GridSearchCV(xgb, param_grid, cv=cv_strategy, scoring='accuracy', n_jobs=-1)
grid.fit(X_train, y_train)

# 8. Final Results
best_model = grid.best_estimator_
test_acc = accuracy_score(y_test, best_model.predict(X_test))

print(f"New Test Accuracy: {test_acc:.4f}")
print("\nTop Parameters:", grid.best_params_)