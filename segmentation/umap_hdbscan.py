"""
segmentation/umap_hdbscan.py
=============================
UMAP dimensionality reduction + HDBSCAN clustering.
Most powerful approach for complex real-world customer segments.
UMAP preserves non-linear structure; HDBSCAN finds variable-density clusters.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
from sklearn.preprocessing import StandardScaler


def run_umap_hdbscan(
    X: np.ndarray,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
    min_cluster_size: int = 50,
    n_components: int = 2,
) -> tuple:
    """
    Run UMAP reduction then HDBSCAN clustering.
    Returns (labels, embedding) where embedding is the 2D UMAP coordinates.
    """
    try:
        import umap
        import hdbscan
    except ImportError:
        raise ImportError(
            "umap-learn and hdbscan are required. "
            "Run: pip install umap-learn hdbscan"
        )

    # Sample for speed on large datasets
    sample_size = min(50_000, len(X))
    if len(X) > sample_size:
        idx = np.random.choice(len(X), sample_size, replace=False)
        X_fit = X[idx]
    else:
        X_fit = X
        idx   = None

    # UMAP reduction
    reducer   = umap.UMAP(
        n_neighbors  = n_neighbors,
        min_dist     = min_dist,
        n_components = n_components,
        random_state = 42,
        verbose      = False,
    )
    embedding = reducer.fit_transform(X_fit)

    # HDBSCAN clustering on the embedding
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size = min_cluster_size,
        prediction_data  = True,
    )
    labels = clusterer.fit_predict(embedding)

    return labels, embedding, idx


def plot_umap_clusters(embedding: np.ndarray, labels: np.ndarray) -> plt.Figure:
    """2D scatter plot of UMAP embedding colored by cluster."""
    unique_labels = sorted(set(labels))
    cmap = plt.cm.get_cmap("tab10", max(len(unique_labels), 1))

    fig, ax = plt.subplots(figsize=(10, 7))

    for i, label in enumerate(unique_labels):
        mask  = labels == label
        color = "#aaaaaa" if label == -1 else cmap(i)
        name  = "Noise" if label == -1 else f"Cluster {label}"
        ax.scatter(
            embedding[mask, 0], embedding[mask, 1],
            c=[color], s=3, alpha=0.5, label=f"{name} (n={mask.sum():,})"
        )

    ax.set_title("UMAP Projection — Clusters", fontsize=14, fontweight="bold")
    ax.set_xlabel("UMAP Dimension 1", fontsize=11)
    ax.set_ylabel("UMAP Dimension 2", fontsize=11)
    ax.legend(loc="upper right", fontsize=9, markerscale=4)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    return fig


def preprocess(df: pd.DataFrame, feature_cols: list) -> np.ndarray:
    """Scale features."""
    X = df[feature_cols].fillna(0).values
    return StandardScaler().fit_transform(X)
