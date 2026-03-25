"""
segmentation/dbscan.py
=======================
DBSCAN clustering — finds natural clusters without specifying count.
Noise points are labeled as cluster -1.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors


def plot_epsilon_curve(X: np.ndarray, min_samples: int = 5) -> plt.Figure:
    """
    K-distance graph to help choose epsilon.
    The elbow point is the recommended epsilon value.
    """
    sample = X[:min(10000, len(X))]
    nbrs   = NearestNeighbors(n_neighbors=min_samples).fit(sample)
    distances, _ = nbrs.kneighbors(sample)
    distances = np.sort(distances[:, -1])

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(distances, color="#2563eb", linewidth=1.5)
    ax.set_xlabel("Points sorted by distance", fontsize=11)
    ax.set_ylabel(f"{min_samples}-NN Distance (epsilon candidates)", fontsize=11)
    ax.set_title("K-Distance Graph — Choose epsilon at the elbow",
                 fontsize=13, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def run_dbscan(X: np.ndarray, eps: float, min_samples: int) -> np.ndarray:
    """
    Run DBSCAN. Returns cluster labels.
    Label -1 = noise/outlier points.
    """
    db = DBSCAN(eps=eps, min_samples=min_samples, n_jobs=-1)
    return db.fit_predict(X)


def get_dbscan_summary(labels: np.ndarray) -> dict:
    """Return cluster count, noise count, and label distribution."""
    unique   = set(labels)
    n_noise  = int((labels == -1).sum())
    n_clusters = len(unique - {-1})
    return {
        "n_clusters": n_clusters,
        "n_noise":    n_noise,
        "noise_pct":  round(n_noise / len(labels) * 100, 1),
    }


def preprocess(df: pd.DataFrame, feature_cols: list) -> np.ndarray:
    """Scale features for DBSCAN."""
    X = df[feature_cols].fillna(0).values
    scaler = StandardScaler()
    return scaler.fit_transform(X)
