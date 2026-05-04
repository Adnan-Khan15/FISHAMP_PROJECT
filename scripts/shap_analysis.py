import pandas as pd
import shap
from xgboost import XGBClassifier

# load dataset
data = pd.read_csv("../data/balanced_amp_dataset.csv")

X = data[[
    "length",
    "charge",
    "molecular_weight",
    "hydrophobicity",
    "aromaticity"
]]

y = data["label"]

# train model again
model = XGBClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=4,
    random_state=42
)

model.fit(X, y)

# SHAP explainer
explainer = shap.Explainer(model)
shap_values = explainer(X)

# summary plot
shap.summary_plot(shap_values, X)