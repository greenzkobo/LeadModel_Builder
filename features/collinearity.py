"""
features/collinearity.py
=========================
Find pairs of features that are highly correlated with each other.
Suggests which one to drop from each pair.
"""

import pandas as pd
import numpy as np


def find_collinear_pairs(df: pd.DataFrame, target: str,
                         threshold: float = 0.85) -> pd.DataFrame:
    """
    Find feature pairs with correlation above threshold.
    For each pair, suggests which feature to drop.

    Parameters:
    -----------
    df : pd.DataFrame
    target : str
        Target column name (excluded from features)
    threshold : float
        Correlation above which a pair is flagged (default 0.85)

    Returns:
    --------
    pd.DataFrame with columns:
        Column_1, Column_2, Correlation,
        Col1_Target_Corr, Col2_Target_Corr,
        Col1_Missing_Pct, Col2_Missing_Pct,
        Suggest_Drop, Reason
    Sorted by abs(Correlation) descending.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if target in numeric_cols:
        numeric_cols.remove(target)

    if len(numeric_cols) < 2:
        return pd.DataFrame()

    target_series = pd.to_numeric(df[target], errors='coerce')
    corr_matrix = df[numeric_cols].corr()

    pairs = []
    for i, col1 in enumerate(numeric_cols):
        for col2 in numeric_cols[i + 1:]:
            corr = corr_matrix.loc[col1, col2]
            if abs(corr) <= threshold:
                continue

            corr1_tgt = abs(df[col1].corr(target_series))
            corr2_tgt = abs(df[col2].corr(target_series))
            miss1 = df[col1].isnull().sum() / len(df) * 100
            miss2 = df[col2].isnull().sum() / len(df) * 100

            # Prefer to drop the one with lower target correlation
            if corr1_tgt < corr2_tgt:
                suggest_drop, reason = col1, "lower target correlation"
            elif miss1 > miss2:
                suggest_drop, reason = col1, "more missing values"
            else:
                suggest_drop, reason = col2, "lower target correlation"

            pairs.append({
                'Column_1':         col1,
                'Column_2':         col2,
                'Correlation':      round(corr, 4),
                'Col1_Target_Corr': round(corr1_tgt, 4),
                'Col2_Target_Corr': round(corr2_tgt, 4),
                'Col1_Missing_Pct': round(miss1, 2),
                'Col2_Missing_Pct': round(miss2, 2),
                'Suggest_Drop':     suggest_drop,
                'Reason':           reason,
            })

    result = pd.DataFrame(pairs)
    if len(result) > 0:
        result = result.sort_values('Correlation', key=abs, ascending=False).reset_index(drop=True)
    return result


def get_drop_suggestions(collinear_df: pd.DataFrame) -> list:
    """Return unique list of columns suggested for removal."""
    if collinear_df is None or len(collinear_df) == 0:
        return []
    return collinear_df['Suggest_Drop'].unique().tolist()


def show_collinear_pairs(collinear_df: pd.DataFrame, max_rows: int = 20):
    """Print the top collinear pairs."""
    if collinear_df is None or len(collinear_df) == 0:
        print("  No collinear pairs found.")
        return

    print(f"\n  Collinear Pairs (top {min(max_rows, len(collinear_df))}):")
    print(f"  {'Column 1':<30} {'Column 2':<30} {'Corr':>8}  {'Drop'}")
    print("  " + "-" * 80)

    for _, row in collinear_df.head(max_rows).iterrows():
        print(f"  {row['Column_1']:<30} {row['Column_2']:<30} "
              f"{row['Correlation']:>8.3f}  → {row['Suggest_Drop']}")
