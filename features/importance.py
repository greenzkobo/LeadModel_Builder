"""
features/importance.py
=======================
Calculate feature importance using correlation with the target variable.
Fast approach that works before model training.
"""

import pandas as pd
import numpy as np


def calculate_importance(df: pd.DataFrame, target: str) -> pd.DataFrame:
    """
    Rank features by absolute correlation with the target.

    Returns:
    --------
    pd.DataFrame with columns:
        Column, Abs_Correlation, Correlation, Cumulative_Portion, Rank
    Sorted from most to least important.
    """
    if target not in df.columns:
        raise ValueError(f"Target '{target}' not found in dataframe.")

    target_series = pd.to_numeric(df[target], errors='coerce')
    feature_cols = [c for c in df.columns if c != target]

    results = []
    for col in feature_cols:
        try:
            col_numeric = pd.to_numeric(df[col], errors='coerce')
            corr = col_numeric.corr(target_series)
            if pd.notna(corr):
                results.append({'Column': col, 'Correlation': corr, 'Abs_Correlation': abs(corr)})
        except Exception:
            pass

    if not results:
        return pd.DataFrame(columns=['Column', 'Correlation', 'Abs_Correlation',
                                     'Cumulative_Portion', 'Rank'])

    importance_df = (
        pd.DataFrame(results)
        .sort_values('Abs_Correlation', ascending=False)
        .reset_index(drop=True)
    )

    total = importance_df['Abs_Correlation'].sum()
    importance_df['Cumulative_Portion'] = (
        importance_df['Abs_Correlation'].cumsum() / total if total > 0 else 0
    )
    importance_df['Rank'] = range(1, len(importance_df) + 1)

    return importance_df


def get_top_features(importance_df: pd.DataFrame, n: int = 50) -> list:
    """Return column names of the top N features by importance."""
    if importance_df is None or len(importance_df) == 0:
        return []
    return importance_df.head(n)['Column'].tolist()


def get_pareto_cutoff(importance_df: pd.DataFrame,
                      threshold: float = 0.80) -> int:
    """
    Return the number of features needed to reach `threshold` of total importance.
    Useful for deciding how many features to keep.
    """
    if importance_df is None or len(importance_df) == 0:
        return 0
    idx = importance_df[importance_df['Cumulative_Portion'] >= threshold].index
    return int(idx[0]) + 1 if len(idx) > 0 else len(importance_df)


def show_top_features(importance_df: pd.DataFrame, n: int = 20):
    """Print top N features to console."""
    print(f"\n  Top {n} Features by Importance:")
    print(f"  {'Rank':<6} {'Column':<35} {'Abs Corr':<12} {'Cumul %'}")
    print("  " + "-" * 65)

    for _, row in importance_df.head(n).iterrows():
        print(f"  {row['Rank']:<6} {row['Column']:<35} "
              f"{row['Abs_Correlation']:<12.4f} {row['Cumulative_Portion']*100:.1f}%")
