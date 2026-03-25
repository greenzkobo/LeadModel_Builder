"""
segmentation/splitter.py
=========================
Split the dataset by cluster label and save each subset as a parquet file.
Each subset is ready to go through the full modeling pipeline independently.
"""

import os
import numpy as np
import pandas as pd


def split_by_cluster(
    df: pd.DataFrame,
    labels: np.ndarray,
    client: str,
    algorithm: str = "kmeans",
    exclude_noise: bool = True,
) -> dict:
    """
    Split df by cluster labels and save each as a parquet file.

    Returns dict: {cluster_id: {"path": str, "shape": tuple, "response_rate": float}}
    """
    from config import get_paths, create_folder_structure

    create_folder_structure(client)
    base_path = get_paths(client)["data_versions"]

    seg_dir = os.path.join(os.path.dirname(base_path), "segments")
    os.makedirs(seg_dir, exist_ok=True)

    df_work = df.copy()
    df_work["_cluster"] = labels

    results = {}
    unique_clusters = sorted(set(labels))

    for cluster_id in unique_clusters:
        if exclude_noise and cluster_id == -1:
            continue

        cluster_df = df_work[df_work["_cluster"] == cluster_id].drop(
            columns=["_cluster"]
        ).reset_index(drop=True)

        label    = f"cluster_{cluster_id}"
        filename = f"{algorithm}_{label}.parquet"
        filepath = os.path.join(seg_dir, filename)
        cluster_df.to_parquet(filepath, index=False)

        results[cluster_id] = {
            "path":    filepath,
            "shape":   cluster_df.shape,
            "label":   label,
            "filename": filename,
        }

    print(f"  ✓ Saved {len(results)} cluster datasets to {seg_dir}")
    return results


def load_cluster_dataset(client: str, algorithm: str,
                         cluster_id: int) -> pd.DataFrame:
    """Load a previously saved cluster dataset."""
    from config import get_paths

    paths    = get_paths(client)
    base     = os.path.dirname(paths["data_versions"])
    seg_dir  = os.path.join(base, "segments")
    filename = f"{algorithm}_cluster_{cluster_id}.parquet"
    filepath = os.path.join(seg_dir, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Cluster file not found: {filepath}")

    return pd.read_parquet(filepath)


def list_cluster_datasets(client: str) -> list:
    """List all saved cluster datasets for a client."""
    from config import get_paths

    paths   = get_paths(client)
    base    = os.path.dirname(paths["data_versions"])
    seg_dir = os.path.join(base, "segments")

    if not os.path.exists(seg_dir):
        return []

    return [f for f in os.listdir(seg_dir) if f.endswith(".parquet")]
