import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from xgboost import XGBClassifier

# Load datasets
amp = pd.read_csv("../data/amp_features.csv")
non_amp = pd.read_csv("../data/non_amp_features.csv")

# Combine datasets
data = pd.concat([amp, non_amp], ignore_index=True)

print("Total dataset size:", len(data))

# Features and labels
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
    random_state=42
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# Train model
model = XGBClassifier()

model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)

# Evaluation
accuracy = accuracy_score(y_test, predictions)

print("\nModel Accuracy:", accuracy)

print("\nClassification Report:\n")
print(classification_report(y_test, predictions))