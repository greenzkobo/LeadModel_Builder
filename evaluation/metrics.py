"""
evaluation/metrics.py
======================
Industry-standard metrics for lead/responder model evaluation.
All functions operate on numpy arrays or pandas Series.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score, accuracy_score, precision_score,
    recall_score, f1_score, confusion_matrix
)


def lift_at_decile(y_true, y_prob, decile: int = 1) -> float:
    """
    Lift at top N deciles.
    Answers: "How much better than random are we in the top 10%?"

    Parameters:
    -----------
    decile : int
        1 = top 10%, 2 = top 20%, etc.
    """
    df = pd.DataFrame({'actual': np.array(y_true), 'prob': np.array(y_prob)})
    df = df.sort_values('prob', ascending=False).reset_index(drop=True)
    cutoff = max(1, int(len(df) * decile / 10))
    rate_decile = df.head(cutoff)['actual'].mean()
    rate_overall = df['actual'].mean()
    return rate_decile / rate_overall if rate_overall > 0 else 0.0


def gains_at_decile(y_true, y_prob, decile: int = 1) -> float:
    """
    Cumulative gains at top N deciles.
    Answers: "What % of all responders are in the top 10%?"
    """
    df = pd.DataFrame({'actual': np.array(y_true), 'prob': np.array(y_prob)})
    df = df.sort_values('prob', ascending=False).reset_index(drop=True)
    cutoff = max(1, int(len(df) * decile / 10))
    captured = df.head(cutoff)['actual'].sum()
    total = df['actual'].sum()
    return captured / total if total > 0 else 0.0


def ks_statistic(y_true, y_prob) -> float:
    """
    Kolmogorov-Smirnov statistic.
    Maximum separation between cumulative distributions of responders vs non-responders.
    Higher = better separation.
    """
    df = pd.DataFrame({'actual': np.array(y_true), 'prob': np.array(y_prob)})
    df = df.sort_values('prob', ascending=False).reset_index(drop=True)
    total_r = df['actual'].sum()
    total_nr = len(df) - total_r
    if total_r == 0 or total_nr == 0:
        return 0.0
    df['cum_r']  = df['actual'].cumsum() / total_r
    df['cum_nr'] = (1 - df['actual']).cumsum() / total_nr
    return float((df['cum_r'] - df['cum_nr']).abs().max())


def calculate_all_metrics(y_true, y_prob, y_pred) -> dict:
    """
    Calculate the full set of metrics used in model comparison.

    Returns:
    --------
    dict with keys:
        AUC, Lift_Decile_1, Lift_Decile_2,
        Gains_Decile_1, Gains_Decile_2,
        KS_Statistic, Accuracy, Misclass_Rate,
        Precision, Recall, F1
    """
    yt = np.array(y_true)
    yp = np.array(y_prob)
    yd = np.array(y_pred)

    return {
        'AUC':           roc_auc_score(yt, yp),
        'Lift_Decile_1': lift_at_decile(yt, yp, 1),
        'Lift_Decile_2': lift_at_decile(yt, yp, 2),
        'Gains_Decile_1':gains_at_decile(yt, yp, 1),
        'Gains_Decile_2':gains_at_decile(yt, yp, 2),
        'KS_Statistic':  ks_statistic(yt, yp),
        'Accuracy':      accuracy_score(yt, yd),
        'Misclass_Rate': 1 - accuracy_score(yt, yd),
        'Precision':     precision_score(yt, yd, zero_division=0),
        'Recall':        recall_score(yt, yd, zero_division=0),
        'F1':            f1_score(yt, yd, zero_division=0),
    }


def get_confusion_matrix(y_true, y_pred) -> pd.DataFrame:
    """Return confusion matrix as a labeled DataFrame."""
    cm = confusion_matrix(y_true, y_pred)
    return pd.DataFrame(
        cm,
        index=['Actual: 0', 'Actual: 1'],
        columns=['Predicted: 0', 'Predicted: 1']
    )
