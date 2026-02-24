"""
features/suggestions.py
========================
Aggregate drop suggestions from all analysis results.
Provides a single list the user can pass to DataCleaner.
"""

import pandas as pd


def build_suggestions(high_missing: pd.DataFrame = None,
                      single_value: pd.DataFrame = None,
                      low_variance: pd.DataFrame = None,
                      high_cardinality: pd.DataFrame = None,
                      collinear_pairs: pd.DataFrame = None) -> dict:
    """
    Combine results from all analyses into categorized drop lists.

    Returns:
    --------
    dict with keys:
        high_missing, single_value, low_variance,
        high_cardinality, collinear_drop, all_combined
    """
    def safe_list(df, col):
        if df is not None and len(df) > 0 and col in df.columns:
            return df[col].tolist()
        return []

    suggestions = {
        'high_missing':    safe_list(high_missing, 'Column'),
        'single_value':    safe_list(single_value, 'Column'),
        'low_variance':    safe_list(low_variance, 'Column'),
        'high_cardinality':safe_list(high_cardinality, 'Column'),
        'collinear_drop':  safe_list(collinear_pairs, 'Suggest_Drop'),
    }

    all_drops = set()
    for cols in suggestions.values():
        all_drops.update(cols)
    suggestions['all_combined'] = list(all_drops)

    return suggestions


def show_suggestions(suggestions: dict):
    """Print a summary of all drop suggestions."""
    total = len(suggestions.get('all_combined', []))

    print(f"\n{'='*60}")
    print("DROP SUGGESTIONS")
    print('='*60)
    print(f"  High missing (>50%):    {len(suggestions['high_missing'])} columns")
    print(f"  Single value:           {len(suggestions['single_value'])} columns")
    print(f"  Low variance:           {len(suggestions['low_variance'])} columns")
    print(f"  High cardinality:       {len(suggestions['high_cardinality'])} columns")
    print(f"  Collinear (suggested):  {len(suggestions['collinear_drop'])} columns")
    print(f"  {'─'*40}")
    print(f"  Total unique to drop:   {total} columns")
    print(f"\n  To drop all: cleaner.drop_columns(suggestions['all_combined'])")
    print(f"{'='*60}\n")


def filter_suggestions(suggestions: dict, category: str) -> list:
    """
    Return drop list for a specific category.

    Categories: 'high_missing', 'single_value', 'low_variance',
                'high_cardinality', 'collinear_drop', 'all_combined'
    """
    return suggestions.get(category, [])
