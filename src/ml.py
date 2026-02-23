import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import xgboost as xgb
from xgboost import XGBClassifier



# Load dataset

df = pd.read_csv(r"C:\Users\parth\Documents\virtual intern\diabetes.csv")


# 2. Replace zero values with mean

cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
for col in cols:
    df[col] = df[col].replace(0, df[col].mean())


# 3. Select features

selected_features = ['Glucose', 'BMI', 'Age', 'Insulin', 'BloodPressure']
X = df[selected_features]
y = df['Outcome']


# 4. Scale features


scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# 5. Stratified train-test split

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# 6. Random Forest baseline

rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    random_state=42,
    class_weight='balanced'   # handle class imbalance
)
rf.fit(X_train, y_train)
rf_train_acc = accuracy_score(y_train, rf.predict(X_train))
rf_test_acc = accuracy_score(y_test, rf.predict(X_test))

print("Random Forest - Train Accuracy:", rf_train_acc)
print("Random Forest - Test Accuracy:", rf_test_acc)


# 7. Gradient Boosting baseline

gb = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    random_state=42
)
gb.fit(X_train, y_train)
gb_train_acc = accuracy_score(y_train, gb.predict(X_train))
gb_test_acc = accuracy_score(y_test, gb.predict(X_test))

print("Gradient Boosting - Train Accuracy:", gb_train_acc)
print("Gradient Boosting - Test Accuracy:", gb_test_acc)


# 8. Cross-validation

cv_scores = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
gb_cv = GradientBoostingClassifier(random_state=42)
cv_results = GridSearchCV(
    gb_cv,
    param_grid={
        'n_estimators': [200, 400, 600],
        'learning_rate': [0.01, 0.05, 0.1],
        'max_depth': [2, 3, 4]
    },
    cv=cv_scores,
    scoring='accuracy',
    n_jobs=-1
)
cv_results.fit(X_scaled, y)

print("Best Gradient Boosting Params:", cv_results.best_params_)
print("Best Gradient Boosting CV Accuracy:", cv_results.best_score_)


from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

best_gb = cv_results.best_estimator_

# Train/Test Accuracy
best_train_acc = accuracy_score(y_train, best_gb.predict(X_train))
best_test_acc = accuracy_score(y_test, best_gb.predict(X_test))

print("Tuned Gradient Boosting - Train Accuracy:", best_train_acc)
print("Tuned Gradient Boosting - Test Accuracy:", best_test_acc)

# ROC-AUC (use predicted probabilities for class 1)
y_proba = best_gb.predict_proba(X_test)[:, 1]
roc_auc = roc_auc_score(y_test, y_proba)

print("Tuned Gradient Boosting - ROC-AUC:", roc_auc)

# Optional: classification report for more detail
print("\nClassification Report:\n", classification_report(y_test, best_gb.predict(X_test)))



# XGBoost Classifier
xgb_model = XGBClassifier(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)

xgb_model.fit(X_train, y_train)

xgb_train_acc = accuracy_score(y_train, xgb_model.predict(X_train))
xgb_test_acc = accuracy_score(y_test, xgb_model.predict(X_test))

print("XGBoost - Train Accuracy:", xgb_train_acc)
print("XGBoost - Test Accuracy:", xgb_test_acc)
