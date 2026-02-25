"""
features/quality.py
====================
Data quality analyses used by FeatureSelector:
  - High missing values
  - Low variance / near-constant columns
  - High cardinality categorical columns
  - Single-value (constant) columns
"""

import numpy as np
import pandas as pd


def analyze_missing(df: pd.DataFrame, threshold: float = 50) -> pd.DataFrame:
    """Find columns with missing % above threshold."""
    pct = (df.isnull().sum() / len(df)) * 100
    high = pct[pct > threshold].sort_values(ascending=False)
    if len(high) > 0:
        result = pd.DataFrame({'Column': high.index, 'Missing_Pct': high.values}).reset_index(drop=True)
    else:
        result = pd.DataFrame(columns=['Column', 'Missing_Pct'])
    print(f"  ✓ Missing analysis: {len(result)} columns above {threshold}%")
    return result


def analyze_variance(df: pd.DataFrame, target: str,
                     threshold: float = 0.01) -> pd.DataFrame:
    """Find numeric columns with near-zero variance or >95% mode dominance."""
    numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns
                    if c != target]
    results = []
    for col in numeric_cols:
        data = df[col].dropna()
        if len(data) == 0:
            continue
        var = data.var()
        mode_pct = data.value_counts().iloc[0] / len(data) * 100
        if var < threshold or mode_pct > 95:
            results.append({
                'Column':   col,
                'Variance': round(var, 6),
                'Zero_Pct': round((data == 0).sum() / len(data) * 100, 2),
                'Mode_Pct': round(mode_pct, 2),
            })
    if results:
        result = pd.DataFrame(results).sort_values('Variance').reset_index(drop=True)
    else:
        result = pd.DataFrame(columns=['Column', 'Variance', 'Zero_Pct', 'Mode_Pct'])
    print(f"  ✓ Variance analysis: {len(result)} low-variance columns")
    return result


def analyze_cardinality(df: pd.DataFrame, threshold: int = 100) -> pd.DataFrame:
    """Find categorical columns with unique values above threshold."""
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    results = [
        {'Column': c,
         'Unique_Values': df[c].nunique(),
         'Pct_of_Rows': round(df[c].nunique() / len(df) * 100, 2)}
        for c in cat_cols if df[c].nunique() > threshold
    ]
    if results:
        result = (
            pd.DataFrame(results)
            .sort_values('Unique_Values', ascending=False)
            .reset_index(drop=True)
        )
    else:
        result = pd.DataFrame(columns=['Column', 'Unique_Values', 'Pct_of_Rows'])
    print(f"  ✓ Cardinality analysis: {len(result)} high-cardinality columns")
    return result


def analyze_single_value(df: pd.DataFrame, target: str) -> pd.DataFrame:
    """Find columns with only one unique non-null value."""
    results = []
    for col in df.columns:
        if col == target:
            continue
        n_unique = df[col].nunique(dropna=True)
        if n_unique <= 1:
            val = df[col].dropna().unique()[0] if n_unique == 1 else None
            results.append({'Column': col, 'Unique_Value': val})
    result = pd.DataFrame(results) if results else pd.DataFrame(columns=['Column', 'Unique_Value'])
    print(f"  ✓ Single-value analysis: {len(result)} constant columns")
    return result
