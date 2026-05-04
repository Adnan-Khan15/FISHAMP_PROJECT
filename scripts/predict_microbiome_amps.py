import pandas as pd
from xgboost import XGBClassifier

# Load training dataset
train = pd.read_csv("../data/balanced_amp_dataset.csv")

X_train = train[[
    "length",
    "charge",
    "molecular_weight",
    "hydrophobicity",
    "aromaticity"
]]

y_train = train["label"]

# Train model
model = XGBClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=4,
    random_state=42
)

model.fit(X_train, y_train)

# Load microbiome features
micro = pd.read_csv("../microbiome_data/microbiome_features.csv")

X_test = micro[[
    "length",
    "charge",
    "molecular_weight",
    "hydrophobicity",
    "aromaticity"
]]

# Predict probability
micro["amp_probability"] = model.predict_proba(X_test)[:, 1]

# Filter strong candidates
candidates = micro[micro["amp_probability"] > 0.8]

candidates.to_csv("../microbiome_data/candidate_amps.csv", index=False)

print("Total candidate AMPs:", len(candidates))
print(candidates.head())