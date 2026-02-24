"""
export/metadata.py
===================
Build and save model metadata alongside scoring code.
Records everything needed to reproduce or audit a model export.
"""

import os
import json
from datetime import datetime


def build_metadata(model_name: str, client: str, target: str,
                   feature_names: list, numeric_cols: list,
                   categorical_cols: list, metrics: dict = None) -> dict:
    """
    Build a metadata dict for a model export.

    Parameters:
    -----------
    metrics : dict, optional
        Validation metrics from ModelEvaluator (lift, auc, ks, etc.)

    Returns:
    --------
    dict ready to be JSON-serialised
    """
    return {
        'model_name':       model_name,
        'client':           client,
        'target':           target,
        'exported_at':      datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        'feature_count':    len(feature_names),
        'feature_names':    feature_names,
        'numeric_cols':     numeric_cols,
        'categorical_cols': categorical_cols,
        'metrics':          metrics or {},
    }


def save_metadata(metadata: dict, scoring_path: str, model_name: str):
    """Save metadata as a JSON file next to the scoring code."""
    filename = f"{model_name.lower().replace(' ', '_')}_metadata.json"
    path     = os.path.join(scoring_path, filename)
    with open(path, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    print(f"  ✓ Saved: outputs/scoring_code/{filename}")
