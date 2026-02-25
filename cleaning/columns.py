"""
cleaning/columns.py
====================
Column drop and keep operations for DataCleaner.
All methods return (df, cols_dropped) for clean state management.
"""

import pandas as pd


def drop_by_name(df: pd.DataFrame, columns: list) -> tuple:
    """Drop specific columns by name. Returns (df, dropped_list)."""
    existing = [c for c in columns if c in df.columns]
    not_found = [c for c in columns if c not in df.columns]

    if not_found:
        print(f"  Warning: {len(not_found)} columns not found: {not_found[:5]}"
              f"{'...' if len(not_found) > 5 else ''}")

    if existing:
        df = df.drop(columns=existing)
        print(f"  ✓ Dropped {len(existing)} columns. "
              f"Shape: {df.shape[0]:,} × {df.shape[1]:,}")

    return df, existing


def drop_by_prefix(df: pd.DataFrame, prefixes: list, exclude: list = None) -> tuple:
    """Drop columns starting with any of the given prefixes."""
    exclude = exclude or []
    cols = []
    for prefix in prefixes:
        cols.extend(c for c in df.columns if c.startswith(prefix) and c not in exclude)
    cols = list(set(cols))

    if cols:
        df = df.drop(columns=cols)
        print(f"  ✓ Dropped {len(cols)} columns (prefixes: {prefixes}). "
              f"Shape: {df.shape[0]:,} × {df.shape[1]:,}")
    else:
        print(f"  No columns found with prefixes: {prefixes}")

    return df, cols


def drop_by_suffix(df: pd.DataFrame, suffixes: list) -> tuple:
    """Drop columns ending with any of the given suffixes."""
    cols = []
    for suffix in suffixes:
        cols.extend(c for c in df.columns if c.endswith(suffix))
    cols = list(set(cols))

    if cols:
        df = df.drop(columns=cols)
        print(f"  ✓ Dropped {len(cols)} columns (suffixes: {suffixes}). "
              f"Shape: {df.shape[0]:,} × {df.shape[1]:,}")
    else:
        print(f"  No columns found with suffixes: {suffixes}")

    return df, cols


def drop_by_pattern(df: pd.DataFrame, pattern: str) -> tuple:
    """Drop columns matching a regex pattern."""
    cols = df.columns[df.columns.str.contains(pattern, regex=True)].tolist()

    if cols:
        df = df.drop(columns=cols)
        print(f"  ✓ Dropped {len(cols)} columns (pattern: {pattern}). "
              f"Shape: {df.shape[0]:,} × {df.shape[1]:,}")
    else:
        print(f"  No columns matched pattern: {pattern}")

    return df, cols


def drop_by_missing(df: pd.DataFrame, threshold: float = 50.0,
                    exclude: list = None) -> tuple:
    """Drop columns with missing % above threshold."""
    exclude = exclude or []
    missing_pct = (df.isnull().sum() / len(df)) * 100

    cols = [
        c for c in df.columns
        if missing_pct[c] > threshold and c not in exclude
    ]

    if cols:
        df = df.drop(columns=cols)
        print(f"  ✓ Dropped {len(cols)} columns (>{threshold}% missing). "
              f"Shape: {df.shape[0]:,} × {df.shape[1]:,}")
    else:
        print(f"  No columns exceed {threshold}% missing threshold.")

    return df, cols


def drop_low_variance(df: pd.DataFrame, threshold: float = 0.01,
                      exclude: list = None) -> tuple:
    """Drop numeric columns with near-zero variance."""
    import numpy as np
    exclude = exclude or []
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    cols = []

    for col in numeric_cols:
        if col in exclude:
            continue
        col_data = df[col].dropna()
        if len(col_data) > 0 and col_data.var() < threshold:
            cols.append(col)

    if cols:
        df = df.drop(columns=cols)
        print(f"  ✓ Dropped {len(cols)} low-variance columns. "
              f"Shape: {df.shape[0]:,} × {df.shape[1]:,}")
    else:
        print(f"  No low-variance columns found (threshold={threshold}).")

    return df, cols


def keep_by_name(df: pd.DataFrame, columns: list,
                 always_keep: list = None) -> tuple:
    """Keep only the specified columns (plus always_keep list)."""
    always_keep = always_keep or []
    keep = list(dict.fromkeys(always_keep + [c for c in columns if c in df.columns]))
    dropped = [c for c in df.columns if c not in keep]
    df = df[keep]
    print(f"  ✓ Kept {len(keep)} columns, dropped {len(dropped)}. "
          f"Shape: {df.shape[0]:,} × {df.shape[1]:,}")
    return df, dropped


def add_column(df: pd.DataFrame, name: str, values) -> pd.DataFrame:
    """Add a new column."""
    df[name] = values
    print(f"  ✓ Added column '{name}'. Shape: {df.shape[0]:,} × {df.shape[1]:,}")
    return df


def add_column_formula(df: pd.DataFrame, name: str, formula: str) -> pd.DataFrame:
    """Add a column computed from a formula string (uses df.eval)."""
    try:
        df[name] = df.eval(formula)
        print(f"  ✓ Added '{name}' = {formula}. "
              f"Shape: {df.shape[0]:,} × {df.shape[1]:,}")
    except Exception as e:
        print(f"  Error creating column: {e}")
    return df
