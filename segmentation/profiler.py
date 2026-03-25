"""
segmentation/profiler.py
=========================
Cluster profiling — describes what makes each cluster different.
Compares feature means per cluster vs overall mean.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")


def build_profile(df: pd.DataFrame, labels: np.ndarray,
                  feature_cols: list, target: str = None) -> pd.DataFrame:
    """
    Build a cluster profile table.
    Shows mean of each feature per cluster vs overall mean.
    Includes cluster size and response rate if target provided.
    """
    df_work = df[feature_cols].copy()
    df_work["_cluster"] = labels

    # Exclude noise
    df_work = df_work[df_work["_cluster"] != -1]

    overall_mean = df_work[feature_cols].mean()
    profile_rows = []

    for cluster_id in sorted(df_work["_cluster"].unique()):
        cluster_df  = df_work[df_work["_cluster"] == cluster_id]
        cluster_mean = cluster_df[feature_cols].mean()
        row = {"Cluster": int(cluster_id), "Size": len(cluster_df)}

        # Response rate if target available
        if target and target in df.columns:
            cluster_idx = df.index[labels == cluster_id]
            resp_rate   = pd.to_numeric(
                df.loc[cluster_idx, target], errors="coerce"
            ).mean() * 100
            row["Response_Rate_%"] = round(resp_rate, 2)

        # Top differentiating features (largest deviation from overall mean)
        deviation = ((cluster_mean - overall_mean) / (overall_mean.abs() + 1e-9)) * 100
        top_pos   = deviation.nlargest(3)
        top_neg   = deviation.nsmallest(3)

        row["Higher_Than_Avg"] = ", ".join(
            [f"{c} (+{v:.0f}%)" for c, v in top_pos.items()]
        )
        row["Lower_Than_Avg"] = ", ".join(
            [f"{c} ({v:.0f}%)" for c, v in top_neg.items()]
        )
        profile_rows.append(row)

    return pd.DataFrame(profile_rows)


def plot_cluster_means(df: pd.DataFrame, labels: np.ndarray,
                       feature_cols: list, top_n: int = 10) -> plt.Figure:
    """Heatmap of top N features by cluster mean (normalized)."""
    df_work = df[feature_cols].copy()
    df_work["_cluster"] = labels
    df_work = df_work[df_work["_cluster"] != -1]

    cluster_means = df_work.groupby("_cluster")[feature_cols].mean()

    # Pick top N most variable features across clusters
    variance = cluster_means.var()
    top_cols  = variance.nlargest(top_n).index.tolist()

    # Normalize 0-1 per feature for heatmap
    normalized = cluster_means[top_cols].copy()
    for col in top_cols:
        col_range = normalized[col].max() - normalized[col].min()
        if col_range > 0:
            normalized[col] = (normalized[col] - normalized[col].min()) / col_range

    fig, ax = plt.subplots(figsize=(max(8, top_n * 0.8), max(4, len(cluster_means) * 0.7)))
    im = ax.imshow(normalized.values, aspect="auto", cmap="RdYlGn")
    ax.set_xticks(range(len(top_cols)))
    ax.set_xticklabels(top_cols, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(cluster_means)))
    ax.set_yticklabels([f"Cluster {i}" for i in cluster_means.index], fontsize=10)
    ax.set_title(f"Top {top_n} Differentiating Features by Cluster",
                 fontsize=13, fontweight="bold", pad=12)
    plt.colorbar(im, ax=ax, label="Normalized Mean (0=low, 1=high)")
    plt.tight_layout()
    return fig


def get_cluster_sizes(labels: np.ndarray) -> pd.DataFrame:
    """Return cluster size summary."""
    unique, counts = np.unique(labels, return_counts=True)
    df = pd.DataFrame({"Cluster": unique, "Count": counts})
    df["Pct"] = (df["Count"] / df["Count"].sum() * 100).round(1)
    df["Label"] = df["Cluster"].apply(
        lambda x: "Noise" if x == -1 else f"Cluster {x}"
    )
    return df[["Label", "Cluster", "Count", "Pct"]]
