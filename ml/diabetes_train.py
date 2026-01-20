import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score



# Load dataset
df = pd.read_csv('../datasets/diabetes.csv')

# Replace zero values
cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
for col in cols:
    df[col] = df[col].replace(0, df[col].mean())

selected_features = [
    'Glucose',
    'BMI',
    'Age',
    'Insulin',
    'BloodPressure'
]

X = df[selected_features]
y = df['Outcome']

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Stratified split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Logistic Regression (baseline)
lr = LogisticRegression(max_iter=1000, class_weight='balanced')
lr.fit(X_train, y_train)
lr_train_pred = lr.predict(X_train)
lr_test_pred = lr.predict(X_test)
lr_train_acc = accuracy_score(y_train, lr_train_pred)
lr_test_acc = accuracy_score(y_test, lr_test_pred)

print("Logistic Regression - Train Accuracy:", lr_train_acc)
print("Logistic Regression - Test Accuracy:", lr_test_acc)

# Random Forest (improved)
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    random_state=42
)
rf.fit(X_train, y_train)
rf_train_pred = rf.predict(X_train)
rf_test_pred = rf.predict(X_test)
rf_train_acc = accuracy_score(y_train, rf_train_pred)
rf_test_acc = accuracy_score(y_test, rf_test_pred)

print("Random Forest - Train Accuracy:", rf_train_acc)
print("Random Forest - Test Accuracy:", rf_test_acc)

gb = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    random_state=42
)

gb.fit(X_train, y_train)

gb_train_pred = gb.predict(X_train)
gb_test_pred = gb.predict(X_test)

gb_train_acc = accuracy_score(y_train, gb_train_pred)
gb_test_acc = accuracy_score(y_test, gb_test_pred)

print("Gradient Boosting - Train Accuracy:", gb_train_acc)
print("Gradient Boosting - Test Accuracy:", gb_test_acc)
cv_scores = cross_val_score(
    gb,
    X_scaled,
    y,
    cv=5,
    scoring='accuracy'
)

print("Gradient Boosting CV Accuracy:", cv_scores.mean())


# Support Vector Machine (RBF kernel)
svm = SVC(
    kernel='rbf',
    C=1.0,
    gamma='scale',
    class_weight='balanced',
    random_state=42
)

svm.fit(X_train, y_train)

svm_train_pred = svm.predict(X_train)
svm_test_pred = svm.predict(X_test)

svm_train_acc = accuracy_score(y_train, svm_train_pred)
svm_test_acc = accuracy_score(y_test, svm_test_pred)

print("SVM - Train Accuracy:", svm_train_acc)
print("SVM - Test Accuracy:", svm_test_acc)

