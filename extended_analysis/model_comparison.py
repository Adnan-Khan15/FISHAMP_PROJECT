import os
import time
import warnings
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

warnings.filterwarnings('ignore')

HERE          = os.path.dirname(os.path.abspath(__file__))
DATA_PATH     = os.path.join(HERE, "..", "data", "balanced_amp_dataset.csv")
OUT_CSV_PATH  = os.path.join(HERE, "model_comparison.csv")

FEATURES = ["length", "charge", "molecular_weight",
            "hydrophobicity", "aromaticity"]
TARGET   = "label"
RANDOM_SEED = 42

models = {
    "Logistic Regression": LogisticRegression(max_iter=10000, random_state=RANDOM_SEED),
    "Decision Tree":       DecisionTreeClassifier(random_state=RANDOM_SEED),
    "Random Forest":       RandomForestClassifier(n_estimators=200, random_state=RANDOM_SEED),
    "SVM (RBF)":           SVC(probability=True, random_state=RANDOM_SEED),
    "XGBoost":             XGBClassifier(n_estimators=200, learning_rate=0.05,
                                          max_depth=4, random_state=RANDOM_SEED),
}

results = []

data = pd.read_csv(DATA_PATH)
print(f"Dataset: {len(data)} samples ({data[TARGET].sum():.0f} AMPs, "
      f"{(1 - data[TARGET]).sum():.0f} non-AMPs)\n")

X = data[FEATURES].astype(float)
y = data[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
)

print(f"{'Model':<22} {'Acc':<8} {'Prec':<8} {'Recall':<8} {'F1':<8} "
      f"{'AUC':<8} {'CV AUC':<8} {'Train(s)':<8}")
print("-" * 86)

for name, clf in models.items():
    start = time.perf_counter()
    clf.fit(X_train, y_train)
    elapsed = time.perf_counter() - start

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    cv_auc = cross_val_score(clf, X, y, cv=5, scoring="roc_auc")

    acc    = accuracy_score(y_test, y_pred)
    prec   = precision_score(y_test, y_pred)
    rec    = recall_score(y_test, y_pred)
    f1     = f1_score(y_test, y_pred)
    auc    = roc_auc_score(y_test, y_prob)

    results.append({
        "Model": name,
        "Accuracy":  round(acc, 4),
        "Precision": round(prec, 4),
        "Recall":    round(rec, 4),
        "F1":        round(f1, 4),
        "ROC-AUC":   round(auc, 4),
        "CV-AUC":    f"{cv_auc.mean():.4f} ± {cv_auc.std():.4f}",
        "Train(s)":  round(elapsed, 4),
    })

    print(f"{name:<22} {acc:<8.4f} {prec:<8.4f} {rec:<8.4f} {f1:<8.4f} "
          f"{auc:<8.4f} {cv_auc.mean():<8.4f} {elapsed:<8.4f}")

df_out = pd.DataFrame(results)
df_out.to_csv(OUT_CSV_PATH, index=False)
print(f"\nSaved comparison table to {OUT_CSV_PATH}")
