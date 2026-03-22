"""
visualization/importance.py
============================
Feature importance horizontal bar chart for a single model.
Works with any model that has feature_importances_ or coef_.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
try:
    from ui.chart_style import apply as _apply_style, get_colors
    _apply_style()
except Exception:
    pass


def get_model_importance(model, feature_names: list, top_n: int = 20) -> pd.DataFrame:
    """
    Extract feature importance from a trained model.

    Returns:
    --------
    pd.DataFrame with columns: Feature, Importance
    Sorted descending, top_n rows.
    Returns empty DataFrame if model doesn't support importance.
    """
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importance = np.abs(model.coef_[0])
    else:
        return pd.DataFrame()

    return (
        pd.DataFrame({'Feature': feature_names, 'Importance': importance})
        .sort_values('Importance', ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )


def plot_feature_importance(model, feature_names: list,
                            model_name: str = "", top_n: int = 20,
                            save_path: str = None) -> pd.DataFrame:
    """
    Plot horizontal bar chart of top N feature importances.

    Returns:
    --------
    pd.DataFrame of importance values (useful for reports)
    """
    importance_df = get_model_importance(model, feature_names, top_n)

    if importance_df.empty:
        print(f"  Model '{model_name}' does not support feature importance.")
        return importance_df

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(range(len(importance_df)), importance_df['Importance'].values,
            color='steelblue')
    ax.set_yticks(range(len(importance_df)))
    ax.set_yticklabels(importance_df['Feature'].values)
    ax.invert_yaxis()
    ax.set_xlabel('Importance', fontsize=12)
    ax.set_title(f'Top {top_n} Feature Importance — {model_name}',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  ✓ Saved: {os.path.basename(save_path)}")

    pass  # plt.show() removed for Streamlit
    return importance_df
