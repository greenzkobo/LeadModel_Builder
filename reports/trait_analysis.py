"""
reports/trait_analysis.py
==========================
Trait analysis — compares feature means between responders and non-responders.
Shows which features are associated with positive outcomes and in which direction.
"""

import numpy as np
import pandas as pd


def calculate_trait_analysis(X_val: pd.DataFrame, y_val,
                              y_prob, feature_names: list,
                              top_n: int = 20) -> pd.DataFrame:
    """
    For each top feature, compare mean values between responders and non-responders.

    Parameters:
    -----------
    X_val : pd.DataFrame
        Validation features
    y_val : array-like
        True labels
    y_prob : array-like
        Predicted probabilities (for correlation)
    feature_names : list
        All feature names (will take top_n)
    top_n : int
        How many features to analyze

    Returns:
    --------
    pd.DataFrame with columns:
        Feature, Correlation_with_Score,
        Mean_Responders, Mean_Non_Responders,
        Difference, Trait_Direction
    """
    y_val   = np.array(y_val)
    y_prob  = np.array(y_prob)
    y_series = pd.Series(y_prob)
    resp_mask = y_val == 1

    features_to_check = [f for f in feature_names[:top_n] if f in X_val.columns]

    results = []
    for feature in features_to_check:
        col = X_val[feature]
        corr          = col.corr(y_series)
        mean_resp     = col[resp_mask].mean()
        mean_non_resp = col[~resp_mask].mean()
        diff          = mean_resp - mean_non_resp
        direction     = "Higher = More Likely" if diff > 0 else "Lower = More Likely"

        results.append({
            'Feature':               feature,
            'Correlation_with_Score': round(corr, 4),
            'Mean_Responders':        round(mean_resp, 4),
            'Mean_Non_Responders':    round(mean_non_resp, 4),
            'Difference':             round(diff, 4),
            'Trait_Direction':        direction,
        })

    return pd.DataFrame(results)


def get_top_insights(trait_df: pd.DataFrame, n: int = 3) -> dict:
    """
    Return the strongest positive and negative trait indicators.

    Returns:
    --------
    dict with keys 'positive' and 'negative', each a list of row dicts
    """
    positive = trait_df[trait_df['Difference'] > 0].nlargest(n, 'Difference')
    negative = trait_df[trait_df['Difference'] < 0].nsmallest(n, 'Difference')
    return {
        'positive': positive.to_dict('records'),
        'negative': negative.to_dict('records'),
    }
