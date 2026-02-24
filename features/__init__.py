"""
features/__init__.py
=====================
Public API for the features package.

Usage (unchanged from old feature_selection.py):
    from features import FeatureSelector

    selector = FeatureSelector(df, client="Humana", target="IsTarget")
    selector.run_analysis()
    selector.show_suggestions()
    selector.plot_importance_cutoff()
"""

import os
import pandas as pd
from config import get_paths, create_folder_structure
from . import importance as imp_mod
from . import collinearity as col_mod
from . import suggestions as sug_mod
from . import plots as plot_mod
from . import quality


class FeatureSelector:
    """
    Analyze features and provide data-driven suggestions for dimension reduction.
    Delegates each analysis type to a focused sub-module.
    """

    def __init__(self, df: pd.DataFrame, client: str, target: str = "IsTarget"):
        self.df = df.copy()
        self.client = client
        self.target = target

        create_folder_structure(client)
        paths = get_paths(client)
        self.viz_path = paths['visualizations']
        self.reports_path = paths['reports']

        # Results (populated by analyze_* methods)
        self.high_missing = None
        self.low_variance = None
        self.high_cardinality = None
        self.single_value = None
        self.collinear_pairs = None
        self.importance_df = None

        print(f"\n{'='*60}")
        print(f"FEATURE SELECTOR: {client}")
        print('='*60)
        print(f"  Data shape: {self.df.shape[0]:,} rows × {self.df.shape[1]:,} columns")
        print(f"  Target: {target}")
        print(f"{'='*60}\n")

    # ------------------------------------------------------------------
    # Analysis methods (each calls a focused sub-module)
    # ------------------------------------------------------------------

    def analyze_importance(self) -> pd.DataFrame:
        """Rank features by correlation with target."""
        print("  Analyzing feature importance...", end=" ")
        self.importance_df = imp_mod.calculate_importance(self.df, self.target)
        print(f"✓ ({len(self.importance_df)} features ranked)")
        return self.importance_df

    def analyze_missing(self, threshold: float = 50) -> pd.DataFrame:
        self.high_missing = quality.analyze_missing(self.df, threshold)
        return self.high_missing

    def analyze_variance(self, threshold: float = 0.01) -> pd.DataFrame:
        self.low_variance = quality.analyze_variance(self.df, self.target, threshold)
        return self.low_variance

    def analyze_cardinality(self, threshold: int = 100) -> pd.DataFrame:
        self.high_cardinality = quality.analyze_cardinality(self.df, threshold)
        return self.high_cardinality

    def analyze_single_value(self) -> pd.DataFrame:
        self.single_value = quality.analyze_single_value(self.df, self.target)
        return self.single_value

    def analyze_collinearity(self, threshold: float = 0.85) -> pd.DataFrame:
        """Find highly correlated feature pairs."""
        print("  Analyzing collinearity...", end=" ")
        self.collinear_pairs = col_mod.find_collinear_pairs(self.df, self.target, threshold)
        print(f"✓ ({len(self.collinear_pairs)} pairs above {threshold})")
        return self.collinear_pairs

    def run_analysis(self, missing_threshold: float = 50,
                     collinearity_threshold: float = 0.85) -> dict:
        """Run all analyses in sequence. Returns suggestions dict."""
        print("Running full feature analysis...")
        print("-" * 40)
        self.analyze_importance()
        self.analyze_missing(missing_threshold)
        self.analyze_variance()
        self.analyze_cardinality()
        self.analyze_single_value()
        self.analyze_collinearity(collinearity_threshold)
        print("-" * 40)
        print("  ✓ Analysis complete.\n")
        return self.get_suggestions()

    # ------------------------------------------------------------------
    # Suggestions
    # ------------------------------------------------------------------

    def get_suggestions(self) -> dict:
        return sug_mod.build_suggestions(
            self.high_missing, self.single_value, self.low_variance,
            self.high_cardinality, self.collinear_pairs
        )

    def show_suggestions(self):
        sug_mod.show_suggestions(self.get_suggestions())

    def show_top_features(self, n: int = 20):
        if self.importance_df is None:
            print("  Run analyze_importance() first.")
            return
        imp_mod.show_top_features(self.importance_df, n)

    def get_top_features(self, n: int = 50) -> list:
        return imp_mod.get_top_features(self.importance_df, n)

    def get_pareto_cutoff(self, threshold: float = 0.80) -> int:
        return imp_mod.get_pareto_cutoff(self.importance_df, threshold)

    # ------------------------------------------------------------------
    # Plots
    # ------------------------------------------------------------------

    def plot_importance_cutoff(self, save: bool = True):
        path = os.path.join(self.viz_path, 'feature_importance_cutoff.png') if save else None
        plot_mod.plot_importance_cutoff(self.importance_df, path)

    def plot_correlation_heatmap(self, top_n: int = 30, save: bool = True):
        path = os.path.join(self.viz_path, 'correlation_heatmap.png') if save else None
        plot_mod.plot_correlation_heatmap(self.df, self.importance_df, self.target, top_n, path)

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------

    def save_report(self):
        """Save full analysis to Excel."""
        report_path = os.path.join(self.reports_path, 'feature_selection_report.xlsx')
        with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
            for sheet, df in [
                ('High_Missing',    self.high_missing),
                ('Single_Value',    self.single_value),
                ('Low_Variance',    self.low_variance),
                ('High_Cardinality',self.high_cardinality),
                ('Collinear_Pairs', self.collinear_pairs),
                ('Feature_Importance', self.importance_df),
            ]:
                if df is not None and len(df) > 0:
                    df.to_excel(writer, sheet_name=sheet, index=False)
        print(f"  ✓ Report saved: reports/feature_selection_report.xlsx")


__all__ = ['FeatureSelector']
