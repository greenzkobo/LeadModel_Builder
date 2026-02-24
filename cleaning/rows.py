"""
cleaning/rows.py
=================
Row filtering operations for DataCleaner.
All functions return (df, rows_dropped_count).
"""

import pandas as pd


def drop_by_condition(df: pd.DataFrame, condition: str) -> tuple:
    """
    Drop rows matching a condition string.
    Example: condition = "age < 0"
    """
    try:
        mask = df.eval(condition)
        count = int(mask.sum())
        df = df[~mask]
        print(f"  ✓ Dropped {count:,} rows where: {condition}. "
              f"Shape: {df.shape[0]:,} × {df.shape[1]:,}")
        return df, count
    except Exception as e:
        print(f"  Error evaluating condition: {e}")
        return df, 0


def drop_missing_target(df: pd.DataFrame, target: str = "IsTarget") -> tuple:
    """Drop rows where the target column is null."""
    if target not in df.columns:
        print(f"  Warning: Target '{target}' not found.")
        return df, 0

    count = int(df[target].isnull().sum())
    df = df.dropna(subset=[target])
    print(f"  ✓ Dropped {count:,} rows (missing {target}). "
          f"Shape: {df.shape[0]:,} × {df.shape[1]:,}")
    return df, count


def drop_duplicates(df: pd.DataFrame, subset: list = None) -> tuple:
    """Drop duplicate rows, optionally based on a subset of columns."""
    rows_before = len(df)
    df = df.drop_duplicates(subset=subset)
    count = rows_before - len(df)
    print(f"  ✓ Dropped {count:,} duplicate rows. "
          f"Shape: {df.shape[0]:,} × {df.shape[1]:,}")
    return df, count


def filter_by_value(df: pd.DataFrame, column: str, values: list,
                    keep: bool = True) -> tuple:
    """
    Keep or drop rows where column is in `values`.

    Parameters:
    -----------
    keep : bool
        If True, keep rows where column is in values (filter IN).
        If False, drop rows where column is in values (filter OUT).
    """
    if column not in df.columns:
        print(f"  Warning: Column '{column}' not found.")
        return df, 0

    rows_before = len(df)
    if keep:
        df = df[df[column].isin(values)]
    else:
        df = df[~df[column].isin(values)]

    count = rows_before - len(df)
    action = "Kept" if keep else "Dropped"
    print(f"  ✓ {action} rows where {column} in {values}. "
          f"Removed {count:,} rows. Shape: {df.shape[0]:,} × {df.shape[1]:,}")
    return df, count
