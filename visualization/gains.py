"""
visualization/gains.py
=======================
Cumulative gains curves — what % of responders are in the top N% of scored records.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _gains_at_pct(y_true, y_prob, pct: float) -> float:
    """pct is 0-100."""
    df = pd.DataFrame({'actual': np.array(y_true), 'prob': np.array(y_prob)})
    df = df.sort_values('prob', ascending=False).reset_index(drop=True)
    cutoff = max(1, int(len(df) * pct / 100))
    captured = df.head(cutoff)['actual'].sum()
    total    = df['actual'].sum()
    return captured / total if total > 0 else 0.0


def plot_gains_curves(models: dict, y_true, dataset_label: str = "Validation",
                      prob_key: str = 'y_val_prob', save_path: str = None):
    """
    Plot cumulative gains curves for all models.

    Parameters:
    -----------
    models : dict
        {model_name: {y_val_prob, ...}} from ModelTrainer
    y_true : array-like
        True labels
    dataset_label : str
        'Validation' or 'Training'
    prob_key : str
        'y_val_prob' or 'y_train_prob'
    save_path : str, optional
        Full file path to save
    """
    y_arr = np.array(y_true)
    percentages = np.arange(0, 101, 10)

    fig, ax = plt.subplots(figsize=(10, 8))
    colors  = plt.cm.Set1(np.linspace(0, 1, len(models)))

    for (name, data), color in zip(models.items(), colors):
        y_prob = data[prob_key]
        gains  = [0.0] + [_gains_at_pct(y_arr, y_prob, p) for p in percentages[1:]]
        ax.plot(percentages, gains, color=color, lw=2, marker='o', label=name)

    # Reference lines
    ax.plot(percentages, percentages / 100, 'k--', lw=1, label='Random')
    response_rate = y_arr.mean()
    perfect = [min(p / 100 / response_rate, 1.0) for p in percentages]
    ax.plot(percentages, perfect, 'g--', lw=1, alpha=0.5, label='Perfect Model')

    ax.set_xlim([0, 100])
    ax.set_ylim([0, 1.05])
    ax.set_xlabel('% of Population Targeted', fontsize=12)
    ax.set_ylabel('% of Responders Captured', fontsize=12)
    ax.set_title(f'Cumulative Gains — {dataset_label} Data', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  ✓ Saved: {os.path.basename(save_path)}")

    pass  # plt.show() removed for Streamlit
