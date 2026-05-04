import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, ks_2samp
from sklearn.metrics import roc_curve, auc
from sklearn.decomposition import PCA
from xgboost import XGBClassifier

# =========================
# LOAD DATA
# =========================
amp = pd.read_csv("../data/amp_features.csv")
candidates = pd.read_csv("../microbiome_data/candidate_amps.csv")
non_amp = pd.read_csv("../data/non_amp_features_real.csv")

print("Known AMPs:", len(amp))
print("Predicted AMPs:", len(candidates))
print("Non-AMPs:", len(non_amp))

# =========================
# BASIC STATS
# =========================
print("\n--- Candidate Summary ---")
print(candidates.describe())

print("\nMean Charge:", candidates["charge"].mean())
print("Mean Length:", candidates["length"].mean())
print("Mean Hydrophobicity:", candidates["hydrophobicity"].mean())

# =========================
# DISTRIBUTION PLOTS
# =========================
plt.figure()
plt.hist(amp["charge"], bins=30, alpha=0.5, label="Known AMPs")
plt.hist(candidates["charge"], bins=30, alpha=0.5, label="Predicted AMPs")
plt.hist(non_amp["charge"], bins=30, alpha=0.3, label="Non-AMPs")
plt.legend()
plt.title("Charge Distribution")
plt.xlabel("Charge")
plt.ylabel("Frequency")
plt.show()

plt.figure()
plt.hist(amp["hydrophobicity"], bins=30, alpha=0.5, label="Known AMPs")
plt.hist(candidates["hydrophobicity"], bins=30, alpha=0.5, label="Predicted AMPs")
plt.legend()
plt.title("Hydrophobicity Distribution")
plt.show()

plt.figure()
plt.hist(amp["length"], bins=30, alpha=0.5, label="Known AMPs")
plt.hist(candidates["length"], bins=30, alpha=0.5, label="Predicted AMPs")
plt.legend()
plt.title("Length Distribution")
plt.show()

# =========================
# STATISTICAL TESTS
# =========================
print("\n--- Statistical Tests ---")

t_stat, p_val = ttest_ind(amp["charge"], candidates["charge"])
print("T-test (charge) p-value:", p_val)

ks_stat, ks_p = ks_2samp(amp["charge"], candidates["charge"])
print("KS-test (charge) p-value:", ks_p)

# Effect size (Cohen's d)
def cohens_d(x, y):
    return (x.mean() - y.mean()) / np.sqrt((x.std()**2 + y.std()**2)/2)

print("Cohen's d (charge):", cohens_d(amp["charge"], candidates["charge"]))

# =========================
# MODEL DISCRIMINATION
# =========================
print("\n--- Model Discrimination ---")

combined = pd.concat([
    amp.assign(label=1),
    non_amp.assign(label=0)
])

features = ["length","charge","molecular_weight","hydrophobicity","aromaticity"]

X = combined[features]
y = combined["label"]

model = XGBClassifier(n_estimators=200, learning_rate=0.05, max_depth=4)
model.fit(X, y)

combined["score"] = model.predict_proba(X)[:,1]

plt.figure()
plt.hist(combined[combined["label"]==1]["score"], bins=30, alpha=0.5, label="AMP")
plt.hist(combined[combined["label"]==0]["score"], bins=30, alpha=0.5, label="Non-AMP")
plt.legend()
plt.title("Model Score Distribution")
plt.show()

# =========================
# ROC CURVE
# =========================
fpr, tpr, _ = roc_curve(y, combined["score"])
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.2f}")
plt.plot([0,1],[0,1],'--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend()
plt.show()

print("ROC-AUC:", roc_auc)

# =========================
# CANDIDATE CONFIDENCE
# =========================
print("\n--- Candidate Confidence ---")

print("Mean AMP probability:", candidates["amp_probability"].mean())
print("Top 10 mean probability:",
      candidates.nlargest(10, "amp_probability")["amp_probability"].mean())

# =========================
# RANDOM BASELINE
# =========================
print("\n--- Random Baseline ---")

random_sample = non_amp.sample(n=len(candidates))

print("Random peptides mean charge:", random_sample["charge"].mean())
print("Candidate mean charge:", candidates["charge"].mean())

# =========================
# PCA VISUALIZATION
# =========================
print("\n--- PCA Visualization ---")

X_pca_data = pd.concat([
    amp[features],
    candidates[features]
])

labels = ["AMP"]*len(amp) + ["Predicted"]*len(candidates)

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_pca_data)

plt.figure()
for lab in ["AMP","Predicted"]:
    idx = [i for i,l in enumerate(labels) if l==lab]
    plt.scatter(X_pca[idx,0], X_pca[idx,1], label=lab, alpha=0.5)

plt.legend()
plt.title("PCA Comparison (AMP vs Predicted)")
plt.show()

# =========================
# TOP CANDIDATES
# =========================
print("\n--- Top 10 Candidate AMPs ---")
top = candidates.sort_values("amp_probability", ascending=False).head(10)
print(top[["sequence", "amp_probability"]])