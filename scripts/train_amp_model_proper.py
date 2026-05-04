import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from xgboost import XGBClassifier

# Load balanced dataset
data = pd.read_csv("../data/balanced_amp_dataset.csv")

print("Dataset size:", len(data))

# Features (exclude sequence + label)
X = data[[
    "length",
    "charge",
    "molecular_weight",
    "hydrophobicity",
    "aromaticity"
]]

y = data["label"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# Train model
model = XGBClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=4,
    random_state=42
)

model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:,1]

# Evaluation metrics
accuracy = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_prob)

print("\nAccuracy:", accuracy)
print("ROC-AUC:", roc_auc)

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# Cross-validation
print("\nRunning 5-fold cross-validation...")

cv_scores = cross_val_score(model, X, y, cv=5, scoring="roc_auc")

print("Cross-validation ROC-AUC scores:", cv_scores)
print("Mean ROC-AUC:", cv_scores.mean())

# Feature importance
importance = model.feature_importances_

feature_names = X.columns

print("\nFeature Importance:")
for name, score in zip(feature_names, importance):
    print(f"{name}: {score:.4f}")