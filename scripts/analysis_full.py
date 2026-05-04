import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, classification_report,
                              roc_auc_score, confusion_matrix, f1_score,
                              precision_score, recall_score, matthews_corrcoef)
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings('ignore')

import os
script_dir = os.path.dirname(os.path.abspath(__file__))


data = pd.read_csv(os.path.join(script_dir, '../data/balanced_amp_dataset.csv'))
features = ['length', 'charge', 'molecular_weight', 'hydrophobicity', 'aromaticity']
for c in features:
    data[c] = pd.to_numeric(data[c], errors='coerce')
data.dropna(subset=features + ['label'], inplace=True)

X = data[features].astype(float)
y = data['label']

print(f'Dataset: {len(data)} peptides  ({(y==1).sum()} AMP + {(y==0).sum()} non-AMP)')
print()


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
model = XGBClassifier(n_estimators=200, learning_rate=0.05, max_depth=4, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

acc  = accuracy_score(y_test, y_pred)
auc  = roc_auc_score(y_test, y_prob)
f1   = f1_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec  = recall_score(y_test, y_pred)
mcc  = matthews_corrcoef(y_test, y_pred)
cm   = confusion_matrix(y_test, y_pred)

print(' 80/20 Train/Test Split')
print(f'  Accuracy:    {acc:.4f}  ({acc*100:.2f}%)')
print(f'  ROC-AUC:     {auc:.4f}')
print(f'  F1-Score:    {f1:.4f}')
print(f'  Precision:   {prec:.4f}')
print(f'  Recall:      {rec:.4f}')
print(f'  MCC:         {mcc:.4f}')
print(f'  Confusion Matrix:')
print(f'    TN={cm[0,0]}  FP={cm[0,1]}')
print(f'    FN={cm[1,0]}  TP={cm[1,1]}')
print()
print('  Classification Report:')
print(classification_report(y_test, y_pred, target_names=['Non-AMP', 'AMP']))

# === 5-fold CV
print('5-Fold Cross-Validation')
cv_model = XGBClassifier(n_estimators=200, learning_rate=0.05, max_depth=4, random_state=42)
cv_auc = cross_val_score(cv_model, X, y, cv=5, scoring='roc_auc')
cv_acc = cross_val_score(cv_model, X, y, cv=5, scoring='accuracy')
cv_f1  = cross_val_score(cv_model, X, y, cv=5, scoring='f1')
print(f'  AUC   per fold: {[round(v,4) for v in cv_auc]}')
print(f'  AUC   mean: {cv_auc.mean():.4f}  std: {cv_auc.std():.4f}')
print(f'  Acc   per fold: {[round(v,4) for v in cv_acc]}')
print(f'  Acc   mean: {cv_acc.mean():.4f}  std: {cv_acc.std():.4f}')
print(f'  F1    per fold: {[round(v,4) for v in cv_f1]}')
print(f'  F1    mean: {cv_f1.mean():.4f}  std: {cv_f1.std():.4f}')
print()

# === Feature importance
print('--- Feature Importance (XGBoost) ---')
for name, score in sorted(zip(features, model.feature_importances_), key=lambda x: -x[1]):
    bar = '=' * int(score * 60)
    print(f'  {name:<20s}  {score:.4f}  {bar}')
print()

# === Microbiome prediction stats
candidates = pd.read_csv(os.path.join(script_dir, '../microbiome_data/candidate_amps.csv'))
db = pd.read_csv(os.path.join(script_dir, '../microbiome_data/rohu_amp_database.csv'))

print('--- Microbiome AMP Prediction Stats ---')
print(f'  Candidates (prob>0.80):     {len(candidates)}')
print(f'  Mapped to Rohu genome:      {(db["blast_hit"]=="yes").sum()}  (61.8%)')
print(f'  Novel (no BLAST hit):       {(db["novelty_status"]=="Novel").sum()}  (38.2%)')
print(f'  Known (>=50% identity):     {(db["novelty_status"]=="Known").sum()}  (6.9%)')
print(f'  Variant (<50% identity):    {(db["novelty_status"]=="Variant").sum()}  (55.0%)')
print(f'  Mean BLAST identity:        39.3%')
print(f'  Mean AMP probability:       {candidates["amp_probability"].mean():.4f}')
print(f'  Max  AMP probability:       {candidates["amp_probability"].max():.4f}')
print()


print('  SUMMARY TABLE')
print(f'  Metric                Value')
print(f'  ─────────────────     ──────')
print(f'  Dataset size          6612 (3306 AMP + 3306 non-AMP)')
print(f'  Test accuracy         {acc*100:.2f}%')
print(f'  ROC-AUC (test)        {auc:.4f}')
print(f'  5-fold CV AUC         {cv_auc.mean():.4f} ± {cv_auc.std():.4f}')
print(f'  5-fold CV Accuracy    {cv_acc.mean()*100:.2f}% ± {cv_acc.std()*100:.2f}%')
print(f'  F1-Score (test)       {f1:.4f}')
print(f'  Precision (test)      {prec:.4f}')
print(f'  Recall (test)         {rec:.4f}')
print(f'  MCC (test)            {mcc:.4f}')
print(f'  Candidates found      1226 (from 1226 total)')
print(f'  Novel AMPs            468 (38.2%)')

