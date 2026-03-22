"""
ui/chart_style.py
==================
Apply consistent professional chart styling across all matplotlib figures.
Call apply() before any plt.subplots() call.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl


def apply():
    """Apply professional light theme to all matplotlib charts."""
    plt.rcParams.update({
        # Figure
        "figure.facecolor":     "white",
        "figure.edgecolor":     "white",
        "axes.facecolor":       "white",
        "axes.edgecolor":       "#E2E8F0",
        "axes.linewidth":       0.8,
        "axes.grid":            True,
        "axes.axisbelow":       True,

        # Grid
        "grid.color":           "#F1F5F9",
        "grid.linewidth":       0.8,
        "grid.linestyle":       "-",

        # Text
        "text.color":           "#0B1F3A",
        "axes.labelcolor":      "#475569",
        "axes.titlecolor":      "#0B1F3A",
        "xtick.color":          "#94A3B8",
        "ytick.color":          "#94A3B8",
        "axes.labelsize":       10,
        "axes.titlesize":       13,
        "axes.titleweight":     "bold",
        "axes.titlepad":        12,
        "xtick.labelsize":      9,
        "ytick.labelsize":      9,

        # Font
        "font.family":          "sans-serif",
        "font.sans-serif":      ["DM Sans", "Helvetica Neue", "Arial"],

        # Lines
        "lines.linewidth":      2.0,
        "lines.markersize":     6,

        # Legend
        "legend.frameon":       True,
        "legend.framealpha":    0.95,
        "legend.edgecolor":     "#E2E8F0",
        "legend.fontsize":      9,

        # Spines
        "axes.spines.top":      False,
        "axes.spines.right":    False,
    })


# Professional color palette for multi-line charts
COLORS = [
    "#0B1F3A",   # Navy
    "#059669",   # Emerald
    "#2563EB",   # Blue
    "#D97706",   # Amber
    "#DC2626",   # Red
    "#7C3AED",   # Purple
    "#0891B2",   # Cyan
    "#DB2777",   # Pink
]


def get_colors(n: int) -> list:
    """Return n colors from the professional palette."""
    return [COLORS[i % len(COLORS)] for i in range(n)]
