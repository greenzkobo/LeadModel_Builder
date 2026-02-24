"""
evaluation/decile.py
=====================
Build a decile-by-decile performance breakdown table.
This is the industry-standard view for lead/responder model reporting.
"""

import numpy as np
import pandas as pd


def build_decile_table(y_true, y_prob) -> pd.DataFrame:
    """
    Create a 10-row decile analysis table sorted by score (high → low).

    Returns:
    --------
    pd.DataFrame with one row per decile and columns:
        decile, count, responders, response_rate,
        avg_prob, min_prob, max_prob,
        cum_responders, cum_gains, lift
    """
    df = pd.DataFrame({'actual': np.array(y_true), 'prob': np.array(y_prob)})
    df = df.sort_values('prob', ascending=False).reset_index(drop=True)
    df['decile'] = pd.qcut(range(len(df)), q=10, labels=range(1, 11))

    stats = df.groupby('decile', observed=True).agg(
        count=('actual', 'count'),
        responders=('actual', 'sum'),
        response_rate=('actual', 'mean'),
        avg_prob=('prob', 'mean'),
        min_prob=('prob', 'min'),
        max_prob=('prob', 'max')
    ).reset_index()

    total_responders = df['actual'].sum()
    overall_rate = df['actual'].mean()

    stats['cum_responders'] = stats['responders'].cumsum()
    stats['cum_gains'] = stats['cum_responders'] / total_responders if total_responders > 0 else 0
    stats['lift'] = stats['response_rate'] / overall_rate if overall_rate > 0 else 0

    # Round for readability
    for col in ['response_rate', 'avg_prob', 'min_prob', 'max_prob', 'cum_gains', 'lift']:
        stats[col] = stats[col].round(4)

    return stats


def show_decile_table(decile_df: pd.DataFrame, model_name: str = ""):
    """Print a formatted decile table to console."""
    title = f"DECILE ANALYSIS{f' — {model_name}' if model_name else ''}"
    print(f"\n{'='*75}")
    print(title)
    print('='*75)
    print(f"  {'Decile':<8} {'Count':>8} {'Resp':>8} {'Resp%':>8} "
          f"{'Lift':>8} {'Cum Gains':>10}")
    print("  " + "-" * 60)

    for _, row in decile_df.iterrows():
        print(f"  {int(row['decile']):<8} {int(row['count']):>8,} "
              f"{int(row['responders']):>8,} "
              f"{row['response_rate']*100:>7.2f}% "
              f"{row['lift']:>8.3f} "
              f"{row['cum_gains']*100:>9.1f}%")

    print(f"{'='*75}\n")
