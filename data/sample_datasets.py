"""
data/sample_datasets.py
========================
Curated sample datasets for testing the pipeline.
Downloads from public URLs — no credentials needed.
Each dataset is pre-mapped to match the toolkit's expected format.
"""

import io
import requests
import pandas as pd
import numpy as np


# ── Dataset registry ───────────────────────────────────────────────────────────
DATASETS = {
    "Bank Marketing — Lead Conversion": {
        "description": (
            "Real direct marketing dataset from a Portuguese bank. "
            "Predicts whether a client will subscribe to a term deposit. "
            "Binary target, 17 features, ~45k rows. "
            "Very similar to lead/responder modeling."
        ),
        "url": "https://archive.ics.uci.edu/ml/machine-learning-databases/00222/bank-additional.zip",
        "zip": True,
        "zip_file": "bank-additional/bank-additional-full.csv",
        "delimiter": ";",
        "target_col": "y",
        "target_map": {"yes": 1, "no": 0},
        "recommended_rows": 10_000,
        "tags": ["marketing", "binary", "mixed features"],
    },
    "Titanic — Survival Prediction": {
        "description": (
            "Classic ML dataset. Predicts passenger survival on the Titanic. "
            "Binary target, 11 features, 891 rows. "
            "Good for quick pipeline testing."
        ),
        "url": "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv",
        "zip": False,
        "delimiter": ",",
        "target_col": "Survived",
        "target_map": None,
        "recommended_rows": 891,
        "tags": ["classic", "binary", "small"],
    },
}


def list_datasets() -> list:
    """Return list of available dataset names."""
    return list(DATASETS.keys())


def get_dataset_info(name: str) -> dict:
    """Return metadata for a dataset."""
    return DATASETS.get(name, {})


def load_dataset(name: str, n_rows: int = None) -> pd.DataFrame:
    """
    Download and prepare a sample dataset.

    Parameters
    ----------
    name    : dataset name from DATASETS registry
    n_rows  : number of rows to return (None = all rows)

    Returns
    -------
    pd.DataFrame with IsTarget column mapped to 0/1
    """
    if name not in DATASETS:
        raise ValueError(f"Unknown dataset: {name}. Choose from {list_datasets()}")

    cfg = DATASETS[name]

    # ── Download ───────────────────────────────────────────────
    response = requests.get(cfg["url"], timeout=30)
    response.raise_for_status()

    # ── Parse ──────────────────────────────────────────────────
    if cfg["zip"]:
        import zipfile
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            with z.open(cfg["zip_file"]) as f:
                df = pd.read_csv(f, sep=cfg["delimiter"])
    else:
        df = pd.read_csv(io.BytesIO(response.content), sep=cfg["delimiter"])

    # ── Map target to IsTarget (0/1) ───────────────────────────
    target_col = cfg["target_col"]
    if cfg["target_map"]:
        df["IsTarget"] = df[target_col].map(cfg["target_map"])
    else:
        df["IsTarget"] = pd.to_numeric(df[target_col], errors="coerce")

    # Drop original target if different name
    if target_col != "IsTarget":
        df = df.drop(columns=[target_col])

    # ── Encode categoricals to numeric ─────────────────────────
    for col in df.select_dtypes(include=["object"]).columns:
        if col != "IsTarget":
            df[col] = pd.Categorical(df[col]).codes

    # ── Sample ─────────────────────────────────────────────────
    if n_rows and n_rows < len(df):
        # Stratified sample to preserve class balance
        pos = df[df["IsTarget"] == 1]
        neg = df[df["IsTarget"] == 0]
        ratio     = len(pos) / len(df)
        n_pos     = max(1, int(n_rows * ratio))
        n_neg     = n_rows - n_pos
        df = pd.concat([
            pos.sample(min(n_pos, len(pos)), random_state=42),
            neg.sample(min(n_neg, len(neg)), random_state=42),
        ]).sample(frac=1, random_state=42).reset_index(drop=True)

    df = df.reset_index(drop=True)
    return df
