"""
segmentation/kmeans.py
=======================
K-Means clustering with elbow method for optimal cluster count.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


def run_elbow(X: np.ndarray, max_k: int = 10) -> dict:
    """
    Run K-Means for k=2..max_k and compute inertia + silhouette scores.
    Returns dict with k_range, inertias, silhouettes.
    """
    k_range    = list(range(2, max_k + 1))
    inertias   = []
    silhouettes = []

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        inertias.append(km.inertia_)
        silhouettes.append(silhouette_score(X, labels, sample_size=min(5000, len(X))))

    return {"k_range": k_range, "inertias": inertias, "silhouettes": silhouettes}


def plot_elbow(elbow_data: dict) -> plt.Figure:
    """Plot inertia and silhouette score vs k."""
    k_range     = elbow_data["k_range"]
    inertias    = elbow_data["inertias"]
    silhouettes = elbow_data["silhouettes"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Elbow curve
    ax1.plot(k_range, inertias, "o-", color="#2563eb", linewidth=2, markersize=6)
    ax1.set_xlabel("Number of Clusters (k)", fontsize=11)
    ax1.set_ylabel("Inertia (Within-cluster Sum of Squares)", fontsize=11)
    ax1.set_title("Elbow Method", fontsize=13, fontweight="bold")
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.grid(True, alpha=0.3)

    # Silhouette score
    best_k = k_range[np.argmax(silhouettes)]
    ax2.plot(k_range, silhouettes, "o-", color="#16a34a", linewidth=2, markersize=6)
    ax2.axvline(best_k, color="#dc2626", linestyle="--", linewidth=1.5,
                label=f"Best k={best_k}")
    ax2.set_xlabel("Number of Clusters (k)", fontsize=11)
    ax2.set_ylabel("Silhouette Score", fontsize=11)
    ax2.set_title("Silhouette Score (higher = better)", fontsize=13, fontweight="bold")
    ax2.legend(fontsize=10)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def run_kmeans(X: np.ndarray, k: int) -> np.ndarray:
    """Fit K-Means with k clusters. Returns cluster labels."""
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    return km.fit_predict(X)


def preprocess(df: pd.DataFrame, feature_cols: list) -> np.ndarray:
    """Scale numeric features for clustering."""
    X = df[feature_cols].fillna(0).values
    scaler = StandardScaler()
    return scaler.fit_transform(X)
