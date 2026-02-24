"""
visualization/lift.py
======================
Lift curves — shows how each model performs decile by decile vs. random.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _lift_at_decile(y_true, y_prob, decile: int) -> float:
    df = pd.DataFrame({'actual': np.array(y_true), 'prob': np.array(y_prob)})
    df = df.sort_values('prob', ascending=False).reset_index(drop=True)
    cutoff = max(1, int(len(df) * decile / 10))
    rate_decile  = df.head(cutoff)['actual'].mean()
    rate_overall = df['actual'].mean()
    return rate_decile / rate_overall if rate_overall > 0 else 0.0


def plot_lift_curves(models: dict, y_true, dataset_label: str = "Validation",
                     prob_key: str = 'y_val_prob', save_path: str = None):
    """
    Plot lift curves for all models.

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
    fig, ax = plt.subplots(figsize=(10, 8))
    colors  = plt.cm.Set1(np.linspace(0, 1, len(models)))
    deciles = range(1, 11)

    for (name, data), color in zip(models.items(), colors):
        y_prob = data[prob_key]
        lifts  = [_lift_at_decile(y_true, y_prob, d) for d in deciles]
        ax.plot(deciles, lifts, color=color, lw=2, marker='o',
                label=f'{name} (D1 = {lifts[0]:.2f})')

    ax.axhline(y=1.0, color='black', linestyle='--', lw=1, label='Random (Lift = 1.0)')
    ax.set_xlim([0.5, 10.5])
    ax.set_xlabel('Decile', fontsize=12)
    ax.set_ylabel('Lift', fontsize=12)
    ax.set_title(f'Lift Curves — {dataset_label} Data', fontsize=14, fontweight='bold')
    ax.set_xticks(list(deciles))
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  ✓ Saved: {os.path.basename(save_path)}")

    pass  # plt.show() removed for Streamlit
