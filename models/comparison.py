"""
visualization/comparison.py
============================
Model comparison bar chart (Lift / AUC / KS) and confusion matrices.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix


def plot_model_comparison_bar(comparison_df, save_path: str = None):
    """
    Three-panel bar chart: Lift D1, AUC, KS Statistic for each model.

    Parameters:
    -----------
    comparison_df : pd.DataFrame
        From ModelEvaluator.get_comparison_df()
    save_path : str, optional
    """
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    models = comparison_df['Model'].values
    x = range(len(models))

    specs = [
        (axes[0], 'Lift_D1_Val',  'steelblue',    'Lift at Top Decile (Val)', 1.0),
        (axes[1], 'AUC_Val',      'forestgreen',   'AUC (Validation)',         0.5),
        (axes[2], 'KS_Val',       'darkorange',    'KS Statistic (Val)',       None),
    ]

    for ax, col, color, title, hline in specs:
        ax.bar(x, comparison_df[col].values, color=color)
        ax.set_xticks(list(x))
        ax.set_xticklabels(models, rotation=45, ha='right')
        ax.set_title(title, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        if hline is not None:
            ax.axhline(y=hline, color='red', linestyle='--', alpha=0.5)
        if col == 'AUC_Val':
            ax.set_ylim([0.45, 1.0])

    plt.suptitle('Model Comparison', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  ✓ Saved: {os.path.basename(save_path)}")

    plt.show()


def plot_confusion_matrices(models: dict, y_true, dataset_label: str = "Validation",
                            pred_key: str = 'y_val_pred', save_path: str = None):
    """
    One confusion matrix per model, shown side by side.

    Parameters:
    -----------
    models : dict
        {model_name: {y_val_pred, ...}} from ModelTrainer
    y_true : array-like
        True labels
    dataset_label : str
    pred_key : str
        'y_val_pred' or 'y_train_pred'
    save_path : str, optional
    """
    n = len(models)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    if n == 1:
        axes = [axes]

    for ax, (name, data) in zip(axes, models.items()):
        y_pred = data[pred_key]
        cm     = confusion_matrix(y_true, y_pred)
        cm_pct = cm.astype('float') / cm.sum() * 100
        labels = [[f'{cm[i,j]:,}\n({cm_pct[i,j]:.1f}%)' for j in range(2)]
                  for i in range(2)]

        sns.heatmap(cm, annot=labels, fmt='', cmap='Blues', ax=ax,
                    xticklabels=['Pred: 0', 'Pred: 1'],
                    yticklabels=['Actual: 0', 'Actual: 1'],
                    cbar=False)
        ax.set_title(name, fontsize=11, fontweight='bold')

    plt.suptitle(f'Confusion Matrices — {dataset_label} Data',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  ✓ Saved: {os.path.basename(save_path)}")

    plt.show()
