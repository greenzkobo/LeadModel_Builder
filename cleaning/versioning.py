"""
cleaning/versioning.py
=======================
Save and load named snapshots of the dataframe.
Versions are stored as parquet files in the client's data/versions/ folder.
"""

import os
import pandas as pd


def save_version(df: pd.DataFrame, versions_path: str, name: str):
    """
    Save current dataframe as a named version.

    Parameters:
    -----------
    df : pd.DataFrame
    versions_path : str
        Full path to the client's data/versions/ directory
    name : str
        Version label, e.g. "v1_cleaned"
    """
    os.makedirs(versions_path, exist_ok=True)
    path = os.path.join(versions_path, f"{name}.parquet")
    df.to_parquet(path, index=False)
    print(f"  ✓ Saved version '{name}' ({df.shape[0]:,} × {df.shape[1]:,})")


def load_version(versions_path: str, name: str) -> pd.DataFrame:
    """
    Load a named version from disk.

    Returns:
    --------
    pd.DataFrame or None if not found
    """
    path = os.path.join(versions_path, f"{name}.parquet")

    if not os.path.exists(path):
        available = list_versions(versions_path)
        print(f"  Error: Version '{name}' not found.")
        print(f"  Available: {available}")
        return None

    df = pd.read_parquet(path)
    print(f"  ✓ Loaded version '{name}' ({df.shape[0]:,} × {df.shape[1]:,})")
    return df


def list_versions(versions_path: str) -> list:
    """Return sorted list of saved version names (without .parquet extension)."""
    if not os.path.exists(versions_path):
        return []
    return sorted(
        f.replace('.parquet', '')
        for f in os.listdir(versions_path)
        if f.endswith('.parquet')
    )


def show_versions(versions_path: str):
    """Print all saved versions with their shapes."""
    versions = list_versions(versions_path)
    print(f"\n  Saved versions ({versions_path}):")
    if versions:
        for v in versions:
            path = os.path.join(versions_path, f"{v}.parquet")
            df_tmp = pd.read_parquet(path)
            print(f"    - {v}: {df_tmp.shape[0]:,} × {df_tmp.shape[1]:,}")
    else:
        print("    (none saved yet)")
