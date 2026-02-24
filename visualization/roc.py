"""
visualization/roc.py
=====================
ROC curves for all models on a single chart.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc


def plot_roc_curves(models: dict, y_true, dataset_label: str = "Validation",
                    prob_key: str = 'y_val_prob', save_path: str = None):
    """
    Plot ROC curves for all models on one chart.

    Parameters:
    -----------
    models : dict
        {model_name: {y_val_prob, y_train_prob, ...}} from ModelTrainer
    y_true : array-like
        True labels for the chosen dataset
    dataset_label : str
        Label for the chart title ('Validation' or 'Training')
    prob_key : str
        Which probability key to use ('y_val_prob' or 'y_train_prob')
    save_path : str, optional
        Full file path to save the figure
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.Set1(np.linspace(0, 1, len(models)))

    for (name, data), color in zip(models.items(), colors):
        y_prob = data[prob_key]
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=color, lw=2, label=f'{name} (AUC = {roc_auc:.4f})')

    ax.plot([0, 1], [0, 1], 'k--', lw=1, label='Random (AUC = 0.5000)')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate (1 - Specificity)', fontsize=12)
    ax.set_ylabel('True Positive Rate (Sensitivity)', fontsize=12)
    ax.set_title(f'ROC Curves — {dataset_label} Data', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  ✓ Saved: {os.path.basename(save_path)}")

    pass  # plt.show() removed for Streamlit
