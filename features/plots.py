"""
features/plots.py
==================
Visualizations for feature selection:
  - Pareto/cumulative importance curve
  - Elbow detection chart
  - Correlation heatmap
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_importance_cutoff(importance_df: pd.DataFrame,
                           save_path: str = None) -> None:
    """
    Two-panel chart:
      Left:  Cumulative importance (Pareto) with 80% line
      Right: Per-feature importance bar chart with elbow detection
    """
    if importance_df is None or len(importance_df) == 0:
        print("  No importance data to plot.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    x = range(1, len(importance_df) + 1)

    # --- Left: Pareto ---
    ax1 = axes[0]
    y = importance_df['Cumulative_Portion'].values
    ax1.plot(x, y, 'b-', linewidth=2)
    ax1.axhline(y=0.80, color='r', linestyle='--', label='80% threshold')

    pareto_idx = np.argmax(y >= 0.80)
    if pareto_idx > 0:
        ax1.axvline(x=pareto_idx + 1, color='g', linestyle='--', alpha=0.7)
        ax1.scatter([pareto_idx + 1], [y[pareto_idx]], color='g', s=100, zorder=5)
        ax1.annotate(
            f'80% at {pareto_idx + 1} features',
            xy=(pareto_idx + 1, y[pareto_idx]),
            xytext=(pareto_idx + 20, max(y[pareto_idx] - 0.1, 0.05)),
            arrowprops=dict(arrowstyle='->', color='green'),
            fontsize=10, color='green'
        )

    ax1.set_xlabel('Number of Features')
    ax1.set_ylabel('Cumulative Importance')
    ax1.set_title('Pareto: Cumulative Feature Importance')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # --- Right: Elbow ---
    ax2 = axes[1]
    y2 = importance_df['Abs_Correlation'].values
    ax2.bar(x, y2, color='steelblue', alpha=0.7)

    if len(y2) > 10:
        diffs = np.abs(np.diff(y2))
        elbow_idx = np.argmax(diffs[9:]) + 10
        ax2.axvline(x=elbow_idx, color='r', linestyle='--',
                    label=f'Elbow at {elbow_idx}')
        ax2.legend()

    ax2.set_xlabel('Feature Rank')
    ax2.set_ylabel('Absolute Correlation with Target')
    ax2.set_title('Feature Importance (Elbow Detection)')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  ✓ Saved: {save_path}")

    plt.show()


def plot_correlation_heatmap(df: pd.DataFrame, importance_df: pd.DataFrame,
                             target: str, top_n: int = 30,
                             save_path: str = None) -> None:
    """
    Heatmap of top N features + target correlation matrix.
    """
    if importance_df is None or len(importance_df) == 0:
        print("  No importance data — run analyze_importance() first.")
        return

    top_features = importance_df.head(top_n)['Column'].tolist()
    if target in df.columns:
        top_features = [target] + top_features

    # Keep only numeric-convertible columns
    valid = []
    for col in top_features:
        if col in df.columns:
            try:
                pd.to_numeric(df[col], errors='raise')
                valid.append(col)
            except (ValueError, TypeError):
                pass

    if len(valid) < 2:
        print("  Not enough numeric features for heatmap.")
        return

    corr = df[valid].apply(pd.to_numeric, errors='coerce').corr()

    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(corr, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
    plt.colorbar(im, ax=ax).set_label('Correlation')

    ax.set_xticks(range(len(valid)))
    ax.set_yticks(range(len(valid)))
    ax.set_xticklabels(valid, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(valid, fontsize=8)
    ax.set_title(f'Correlation Matrix: Top {top_n} Features + Target')

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  ✓ Saved: {save_path}")

    plt.show()
