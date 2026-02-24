"""
reports/generator.py
=====================
Assembles the full model summary report from template sections.
Saves a .txt report and an .xlsx workbook with all tables.
"""

import os
import numpy as np
import pandas as pd
from config import get_paths, create_folder_structure
from visualization.importance import get_model_importance
from reports.trait_analysis import calculate_trait_analysis, get_top_insights
from reports import templates


class ReportGenerator:
    """
    Generate text + Excel model summary report.
    Pulls data from trainer, evaluator, and optional selector.
    """

    def __init__(self, trainer, evaluator, selector=None, client: str = None):
        self.trainer       = trainer
        self.evaluator     = evaluator
        self.selector      = selector
        self.client        = client
        self.models        = trainer.get_trained_models()
        self.feature_names = trainer.get_feature_names()
        self.target        = trainer.target
        self.winner_name   = evaluator.get_winner()

        create_folder_structure(client)
        self.reports_path = get_paths(client)['reports']

        print(f"\n{'='*60}")
        print(f"REPORT GENERATOR: {client}")
        print('='*60)
        print(f"  Winner: {self.winner_name}")
        print(f"{'='*60}\n")

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------

    def _feature_importance_df(self, top_n: int = 30) -> pd.DataFrame:
        model = self.models[self.winner_name]['model']
        df = get_model_importance(model, self.feature_names, top_n)
        if df.empty:
            return df
        df['Rank']    = range(1, len(df) + 1)
        df['Portion'] = df['Importance'] / df['Importance'].sum()
        return df

    def _decile_df(self):
        return self.evaluator.get_decile_table(self.winner_name, 'val')

    def _trait_df(self, top_n: int = 20) -> pd.DataFrame:
        X_val, y_val = self.trainer.get_validation_data()
        y_prob = self.models[self.winner_name]['y_val_prob']
        return calculate_trait_analysis(X_val, y_val, y_prob,
                                        self.feature_names, top_n)

    # ------------------------------------------------------------------
    # Text report
    # ------------------------------------------------------------------

    def generate_text_report(self) -> str:
        """Build and return the full text report as a string."""
        winner_metrics = self.evaluator.val_metrics[self.winner_name]
        comparison_df  = self.evaluator.get_comparison_df()
        decile_df      = self._decile_df()
        importance_df  = self._feature_importance_df(30)
        trait_df       = self._trait_df(20)
        insights       = get_top_insights(trait_df)

        sections = (
            templates.header(self.client)
            + templates.executive_summary(self.winner_name, winner_metrics)
            + templates.model_comparison(comparison_df)
            + templates.decile_analysis(decile_df, self.winner_name)
            + (templates.feature_importance_section(importance_df)
               if not importance_df.empty else [])
            + templates.trait_analysis_section(trait_df, insights)
            + templates.model_explanation(self.winner_name)
            + templates.recommendations(decile_df)
        )

        return "\n".join(sections)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def generate_full_report(self, save: bool = True) -> str:
        """Generate text report + Excel workbook. Returns report text."""
        report_text = self.generate_text_report()

        if save:
            # Text report
            txt_path = os.path.join(self.reports_path, 'model_summary_report.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"  ✓ Saved: reports/model_summary_report.txt")

            # Excel workbook
            xlsx_path = os.path.join(self.reports_path, 'model_summary_data.xlsx')
            importance_df = self._feature_importance_df(50)
            trait_df      = self._trait_df(30)
            decile_df     = self._decile_df()

            winner_metrics_df = pd.DataFrame([
                {'Metric': k, 'Value': v}
                for k, v in self.evaluator.val_metrics[self.winner_name].items()
            ])

            with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
                self.evaluator.get_comparison_df().to_excel(
                    writer, sheet_name='Model_Comparison', index=False)
                if not importance_df.empty:
                    importance_df.to_excel(
                        writer, sheet_name='Feature_Importance', index=False)
                decile_df.to_excel(
                    writer, sheet_name='Decile_Analysis', index=False)
                trait_df.to_excel(
                    writer, sheet_name='Trait_Analysis', index=False)
                winner_metrics_df.to_excel(
                    writer, sheet_name='Winner_Metrics', index=False)

            print(f"  ✓ Saved: reports/model_summary_data.xlsx")

        return report_text

    def print_report(self):
        """Print report to console."""
        print(self.generate_text_report())
