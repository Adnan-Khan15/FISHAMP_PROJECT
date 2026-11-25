import os
import sys
import warnings
import pandas as pd
import numpy as np
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc, roc_auc_score
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

warnings.filterwarnings('ignore')

RANDOM_SEED = 42
DPI = 600
FIGSIZE = (8, 6)

HERE    = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "figures")
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update({
    "font.family":      "sans-serif",
    "font.sans-serif":  ["Arial", "Helvetica", "DejaVu Sans"],
    "axes.titlesize":   16,
    "axes.labelsize":   14,
    "xtick.labelsize":  12,
    "ytick.labelsize":  12,
    "legend.fontsize":  11,
    "figure.dpi":       DPI,
    "savefig.dpi":      DPI,
    "savefig.bbox":     "tight",
})

COLORS = {
    "known_amp":  "#2E86AB",
    "predicted":  "#A23B72",
    "non_amp":    "#F18F01",
    "xgb":        "#C73E1D",
    "rf":         "#2E86AB",
    "svm":        "#6A994E",
    "lr":         "#F2C14E",
    "dt":         "#A23B72",
    "novel":      "#2E86AB",
    "known":      "#6A994E",
    "variant":    "#F2C14E",
}

DATA_DIR  = os.path.join(HERE, "..", "data")
MICRO_DIR = os.path.join(HERE, "..", "microbiome_data")

FEATURES = ["length", "charge", "molecular_weight",
            "hydrophobicity", "aromaticity"]
TARGET   = "label"

amp_df       = pd.read_csv(os.path.join(DATA_DIR, "amp_features.csv"))
nonamp_df    = pd.read_csv(os.path.join(DATA_DIR, "non_amp_features_real.csv"))
cand_df      = pd.read_csv(os.path.join(MICRO_DIR, "candidate_amps.csv"))
db_df        = pd.read_csv(os.path.join(MICRO_DIR, "rohu_amp_database.csv"))
map_df       = pd.read_csv(os.path.join(MICRO_DIR, "rohu_amp_genome_map.csv"))
balance_df   = pd.read_csv(os.path.join(DATA_DIR, "balanced_amp_dataset.csv"))

for col in FEATURES:
    amp_df[col] = pd.to_numeric(amp_df[col], errors="coerce")
amp_df.dropna(subset=FEATURES, inplace=True)


def savefig(name):
    path = os.path.join(OUT_DIR, name)
    plt.savefig(path, dpi=DPI, bbox_inches="tight", format="pdf")
    print(f"  Saved: {path}")
    plt.close()


def fig_roc_curve():
    X = balance_df[FEATURES].astype(float)
    y = balance_df[TARGET]
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    classifiers = {
        "Logistic Regression": LogisticRegression(max_iter=10000, random_state=RANDOM_SEED),
        "Decision Tree":       DecisionTreeClassifier(random_state=RANDOM_SEED),
        "Random Forest":       RandomForestClassifier(n_estimators=200, random_state=RANDOM_SEED),
        "SVM (RBF)":           SVC(probability=True, random_state=RANDOM_SEED),
        "XGBoost":             XGBClassifier(n_estimators=200, learning_rate=0.05,
                                              max_depth=4, random_state=RANDOM_SEED),
    }
    colors = [COLORS["lr"], COLORS["dt"], COLORS["rf"], COLORS["svm"], COLORS["xgb"]]

    fig, ax = plt.subplots(figsize=FIGSIZE)
    for (name, clf), c in zip(classifiers.items(), colors):
        clf.fit(X_tr, y_tr)
        y_prob = clf.predict_proba(X_te)[:, 1]
        fpr, tpr, _ = roc_curve(y_te, y_prob)
        auroc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=c, lw=2.2,
                label=f"{name} (AUC = {auroc:.3f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1.2, alpha=0.6)
    ax.set_xlim(-0.01, 1.01)
    ax.set_ylim(-0.01, 1.01)
    ax.set_xlabel("False Positive Rate", fontweight="bold")
    ax.set_ylabel("True Positive Rate", fontweight="bold")
    ax.set_title("ROC Curves for AMP Classification Models", fontweight="bold")
    ax.legend(loc="lower right", framealpha=0.9)
    ax.grid(alpha=0.25)
    savefig("01_roc_curve.pdf")


def fig_feature_importance():
    X = balance_df[FEATURES].astype(float)
    y = balance_df[TARGET]
    model = XGBClassifier(n_estimators=200, learning_rate=0.05,
                           max_depth=4, random_state=RANDOM_SEED)
    model.fit(X, y)

    importance = model.feature_importances_
    indices    = np.argsort(importance)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(range(len(indices)), importance[indices],
                   color=[COLORS["xgb"]], height=0.6, edgecolor="white")
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([FEATURES[i] for i in indices], fontweight="bold")
    ax.set_xlabel("Feature Importance (Gain)", fontweight="bold")
    ax.set_title("XGBoost Feature Importance", fontweight="bold")
    ax.set_xlim(0, max(importance) * 1.15)
    for bar, val in zip(bars, importance[indices]):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
                f"{val:.3f}", va="center", fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.25)
    savefig("02_feature_importance.pdf")


def fig_shap_summary():
    try:
        import shap
    except ImportError:
        print("  SHAP not installed — skipping SHAP summary plot")
        return

    X = balance_df[FEATURES].astype(float)
    y = balance_df[TARGET]
    model = XGBClassifier(n_estimators=200, learning_rate=0.05,
                           max_depth=4, random_state=RANDOM_SEED)
    model.fit(X, y)

    explainer = shap.Explainer(model, X)
    shap_values = explainer(X)

    fig, ax = plt.subplots(figsize=(8, 5))
    shap.summary_plot(shap_values, X, show=False, max_display=5,
                      color_bar=True, plot_size=None)
    plt.title("SHAP Feature Importance", fontsize=16, fontweight="bold")
    savefig("03_shap_summary.pdf")


def fig_feature_distribution(feature, xlabel, filename):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    bins = 40

    ax.hist(amp_df[feature], bins=bins, alpha=0.65,
            color=COLORS["known_amp"],  label=f"Known AMPs (n={len(amp_df)})",
            edgecolor="white", linewidth=0.5)
    ax.hist(cand_df[feature], bins=bins, alpha=0.65,
            color=COLORS["predicted"], label=f"Predicted AMPs (n={len(cand_df)})",
            edgecolor="white", linewidth=0.5)
    ax.hist(nonamp_df[feature], bins=bins, alpha=0.40,
            color=COLORS["non_amp"],   label=f"Non-AMPs (n={len(nonamp_df)})",
            edgecolor="white", linewidth=0.5)

    ax.set_xlabel(xlabel, fontweight="bold")
    ax.set_ylabel("Frequency", fontweight="bold")
    ax.set_title(f"{xlabel} Distribution", fontweight="bold")
    ax.legend(framealpha=0.9)
    ax.grid(alpha=0.2, axis="y")
    savefig(filename)


def fig_charge_distribution():
    fig_feature_distribution("charge", "Net Charge (pH 7)", "04_charge_distribution.pdf")


def fig_hydrophobicity_distribution():
    fig_feature_distribution("hydrophobicity", "Hydrophobicity (GRAVY Index)", "05_hydrophobicity_distribution.pdf")


def fig_length_distribution():
    fig_feature_distribution("length", "Sequence Length (aa)", "06_length_distribution.pdf")


def fig_pca():
    combined = pd.concat([
        amp_df[FEATURES].assign(group="Known AMPs"),
        cand_df[FEATURES].assign(group="Predicted AMPs"),
    ], ignore_index=True)

    pca = PCA(n_components=2, random_state=RANDOM_SEED)
    coords = pca.fit_transform(combined[FEATURES])

    fig, ax = plt.subplots(figsize=FIGSIZE)
    for grp, color, marker in [("Known AMPs", COLORS["known_amp"], "o"),
                                ("Predicted AMPs", COLORS["predicted"], "^")]:
        mask = combined["group"] == grp
        ax.scatter(coords[mask, 0], coords[mask, 1], c=color,
                   label=grp, alpha=0.45, s=15, marker=marker, edgecolors="none")

    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)",
                  fontweight="bold")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)",
                  fontweight="bold")
    ax.set_title("PCA: Known AMPs vs Predicted Candidates", fontweight="bold")
    ax.legend(framealpha=0.9, markerscale=2)
    ax.grid(alpha=0.25)
    savefig("07_pca.pdf")


def fig_model_comparison():
    X = balance_df[FEATURES].astype(float)
    y = balance_df[TARGET]
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    classifiers = {
        "Logistic\nRegression": LogisticRegression(max_iter=10000, random_state=RANDOM_SEED),
        "Decision\nTree":       DecisionTreeClassifier(random_state=RANDOM_SEED),
        "Random\nForest":       RandomForestClassifier(n_estimators=200, random_state=RANDOM_SEED),
        "SVM\n(RBF)":           SVC(probability=True, random_state=RANDOM_SEED),
        "XGBoost":              XGBClassifier(n_estimators=200, learning_rate=0.05,
                                               max_depth=4, random_state=RANDOM_SEED),
    }
    colors = [COLORS["lr"], COLORS["dt"], COLORS["rf"], COLORS["svm"], COLORS["xgb"]]

    metrics = {"Accuracy": lambda c: c.score(X_te, y_te),
               "ROC-AUC":  lambda c: roc_auc_score(y_te, c.predict_proba(X_te)[:, 1])}
    scores = {m: [] for m in metrics}
    names = list(classifiers.keys())
    for name, clf in classifiers.items():
        clf.fit(X_tr, y_tr)
        for m_label, fn in metrics.items():
            scores[m_label].append(fn(clf))

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(names))
    w = 0.35
    for i, m_label in enumerate(metrics):
        offset = (i - 0.5) * w
        bars = ax.bar(x + offset, scores[m_label], w, label=m_label,
                      color=[COLORS["xgb"], COLORS["rf"]][i], edgecolor="white")
        for bar, val in zip(bars, scores[m_label]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(names, fontweight="bold")
    ax.set_ylabel("Score", fontweight="bold")
    ax.set_title("Model Performance Comparison (Test Set)", fontweight="bold")
    ax.set_ylim(0.5, 1.05)
    ax.legend(framealpha=0.9)
    ax.grid(axis="y", alpha=0.25)
    savefig("08_model_comparison.pdf")


def fig_novelty_distribution():
    counts = Counter(db_df["novelty_status"])
    labels = []
    sizes  = []
    colors_pie = []
    for status in ["Novel", "Known", "Variant"]:
        labels.append(f"{status}\n({counts.get(status, 0)} AMPs)")
        sizes.append(counts.get(status, 0))
        colors_pie.append(COLORS[status.lower()])
    total = sum(sizes)

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct="%1.1f%%",
        colors=colors_pie, startangle=90,
        textprops={"fontweight": "bold", "fontsize": 12},
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    for at in autotexts:
        at.set_fontweight("bold")
        at.set_fontsize(13)
        at.set_color("white")

    ax.set_title(f"Novelty Distribution of {total} Predicted AMPs",
                 fontweight="bold", pad=20)
    savefig("09_novelty_distribution.pdf")


def fig_blast_identity():
    hits = map_df[map_df["pident"].notna()]
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.hist(hits["pident"], bins=50, color=COLORS["known_amp"],
            edgecolor="white", linewidth=0.5, alpha=0.85)
    ax.axvline(50, color=COLORS["xgb"], ls="--", lw=2,
               label="Known/Variant threshold (50% identity)")
    ax.set_xlabel("BLASTP Identity (%)", fontweight="bold")
    ax.set_ylabel("Number of AMPs", fontweight="bold")
    ax.set_title(f"BLASTP Identity Distribution\n({len(hits)} mapped AMPs)",
                 fontweight="bold")
    ax.legend(framealpha=0.9)
    ax.grid(alpha=0.2, axis="y")
    savefig("10_blast_identity.pdf")


def fig_confidence_distribution():
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.hist(cand_df["amp_probability"], bins=40, color=COLORS["predicted"],
            edgecolor="white", linewidth=0.5, alpha=0.85)
    ax.axvline(0.8, color=COLORS["xgb"], ls="--", lw=2,
               label="Threshold (prob = 0.80)")
    ax.set_xlabel("AMP Probability", fontweight="bold")
    ax.set_ylabel("Number of Candidates", fontweight="bold")
    ax.set_title(f"Confidence Distribution of {len(cand_df)} Predicted AMPs",
                 fontweight="bold")
    ax.legend(framealpha=0.9)
    ax.grid(alpha=0.2, axis="y")
    savefig("11_confidence_distribution.pdf")


def fig_chromosomal_distribution():
    chrom_data = map_df[map_df["chromosome"] != "N/A"]
    chrom_counts = chrom_data["chromosome"].value_counts().head(12)

    labels = [c.replace("NC_", "Chr ").replace(".1", "") for c in chrom_counts.index]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(chrom_counts)), chrom_counts.values,
                  color=COLORS["known_amp"], edgecolor="white", width=0.6)
    ax.set_xticks(range(len(chrom_counts)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=10, fontweight="bold")
    ax.set_ylabel("Number of Mapped AMPs", fontweight="bold")
    ax.set_title("Chromosomal Distribution of BLAST-Mapped AMPs (Top 12)",
                 fontweight="bold")
    for bar, val in zip(bars, chrom_counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                str(val), ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.grid(axis="y", alpha=0.25)
    savefig("12_chromosomal_distribution.pdf")


def fig_probability_vs_charge():
    fig, ax = plt.subplots(figsize=FIGSIZE)
    sc = ax.scatter(cand_df["charge"], cand_df["amp_probability"],
                    c=cand_df["hydrophobicity"], cmap="RdYlBu",
                    alpha=0.6, s=15, edgecolors="none")
    cbar = plt.colorbar(sc, ax=ax, label="Hydrophobicity (GRAVY)")
    cbar.ax.tick_params(labelsize=11)
    ax.set_xlabel("Net Charge (pH 7)", fontweight="bold")
    ax.set_ylabel("AMP Probability", fontweight="bold")
    ax.set_title("AMP Probability vs Charge (colored by Hydrophobicity)",
                 fontweight="bold")
    ax.grid(alpha=0.25)
    savefig("13_probability_vs_charge.pdf")


if __name__ == "__main__":
    print("Generating publication-quality figures...\n")

    print("[1/13] ROC Curve")
    fig_roc_curve()

    print("[2/13] Feature Importance")
    fig_feature_importance()

    print("[3/13] SHAP Summary")
    fig_shap_summary()

    print("[4/13] Charge Distribution")
    fig_charge_distribution()

    print("[5/13] Hydrophobicity Distribution")
    fig_hydrophobicity_distribution()

    print("[6/13] Length Distribution")
    fig_length_distribution()

    print("[7/13] PCA Plot")
    fig_pca()

    print("[8/13] Model Comparison")
    fig_model_comparison()

    print("[9/13] Novelty Distribution")
    fig_novelty_distribution()

    print("[10/13] BLAST Identity Distribution")
    fig_blast_identity()

    print("[11/13] Confidence Distribution")
    fig_confidence_distribution()

    print("[12/13] Chromosomal Distribution")
    fig_chromosomal_distribution()

    print("[13/13] Probability vs Charge Scatter")
    fig_probability_vs_charge()

    print(f"\nAll figures saved to {OUT_DIR}/")
