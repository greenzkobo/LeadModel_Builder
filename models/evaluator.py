"""
models/evaluator.py
====================
Evaluate and compare multiple trained models.
Delegates metric calculations to evaluation/metrics.py and evaluation/decile.py.
"""

import os
import pandas as pd
from config import get_paths, create_folder_structure
from evaluation.metrics import calculate_all_metrics, get_confusion_matrix
from evaluation.decile import build_decile_table, show_decile_table


class ModelEvaluator:
    """
    Evaluate and compare multiple trained ModelTrainer models.
    Uses Lift at Top Decile as the primary ranking metric.
    """

    def __init__(self, trainer, client: str):
        self.trainer = trainer
        self.client = client
        self.models = trainer.get_trained_models()
        self.X_train, self.y_train = trainer.get_training_data()
        self.X_val,   self.y_val   = trainer.get_validation_data()

        create_folder_structure(client)
        self.reports_path = get_paths(client)['reports']

        self.train_metrics = {}
        self.val_metrics   = {}
        self.comparison_df = None

        print(f"\n{'='*60}")
        print(f"MODEL EVALUATOR: {client}")
        print('='*60)
        print(f"  Models to evaluate: {len(self.models)}")
        print(f"  Validation set:     {len(self.y_val):,} rows")
        print(f"{'='*60}\n")

    def evaluate_model(self, name: str) -> dict:
        """Evaluate a single model on train and val sets."""
        if name not in self.models:
            print(f"  Model '{name}' not found.")
            return {}

        d = self.models[name]
        try:
            train_m = calculate_all_metrics(self.y_train, d['y_train_prob'], d['y_train_pred'])
            val_m   = calculate_all_metrics(self.y_val,   d['y_val_prob'],   d['y_val_pred'])
            return {'train': train_m, 'val': val_m}
        except Exception as e:
            print(f"  Error evaluating {name}: {e}")
            return {}

    def evaluate_all(self):
        """Evaluate all trained models and build comparison table."""
        print("Evaluating models...")
        print("-" * 40)
        for name in self.models:
            print(f"  Evaluating {name}...", end=" ")
            result = self.evaluate_model(name)
            if result:
                self.train_metrics[name] = result['train']
                self.val_metrics[name]   = result['val']
                print("✓")
        self._build_comparison_table()
        print("-" * 40)
        print(f"  Evaluated {len(self.val_metrics)} models.\n")

    def _build_comparison_table(self):
        """Build DataFrame sorted by Lift at Top Decile (val)."""
        rows = []
        for name in self.val_metrics:
            v = self.val_metrics[name]
            t = self.train_metrics[name]
            rows.append({
                'Model':         name,
                'Lift_D1_Val':   v['Lift_Decile_1'],
                'Lift_D1_Train': t['Lift_Decile_1'],
                'Gains_D1_Val':  v['Gains_Decile_1'],
                'AUC_Val':       v['AUC'],
                'AUC_Train':     t['AUC'],
                'KS_Val':        v['KS_Statistic'],
                'Misclass_Val':  v['Misclass_Rate'],
                'Misclass_Train':t['Misclass_Rate'],
                'Precision_Val': v['Precision'],
                'Recall_Val':    v['Recall'],
            })
        self.comparison_df = pd.DataFrame(rows).sort_values(
            'Lift_D1_Val', ascending=False
        ).reset_index(drop=True)
        self.comparison_df['Rank'] = range(1, len(self.comparison_df) + 1)

    def show_comparison(self):
        """Print comparison table to console."""
        if self.comparison_df is None:
            print("  Run evaluate_all() first.")
            return

        print(f"\n{'='*90}")
        print("MODEL COMPARISON  (sorted by Lift at Top Decile — Validation)")
        print('='*90)
        print(f"\n{'Rank':<6} {'Model':<22} {'Lift D1':>10} {'Gains D1':>10} "
              f"{'AUC':>10} {'KS':>10} {'Misclass':>10}")
        print(f"{'':6} {'':22} {'(Val)':>10} {'(Val)':>10} "
              f"{'(Val)':>10} {'(Val)':>10} {'(Val)':>10}")
        print("-" * 90)

        for _, row in self.comparison_df.iterrows():
            print(f"{row['Rank']:<6} {row['Model']:<22} "
                  f"{row['Lift_D1_Val']:>10.3f} {row['Gains_D1_Val']:>10.3f} "
                  f"{row['AUC_Val']:>10.4f} {row['KS_Val']:>10.4f} "
                  f"{row['Misclass_Val']:>10.4f}")

        w = self.comparison_df.iloc[0]
        print("-" * 90)
        print(f"\n  🏆 WINNER: {w['Model']}")
        print(f"     Lift D1: {w['Lift_D1_Val']:.3f}  |  "
              f"Captures {w['Gains_D1_Val']*100:.1f}% of responders in top 10%")
        print(f"     AUC: {w['AUC_Val']:.4f}  |  KS: {w['KS_Val']:.4f}")

        print(f"\n  Overfitting Check (Train vs Val):")
        for _, row in self.comparison_df.iterrows():
            auc_diff  = row['AUC_Train']    - row['AUC_Val']
            lift_diff = row['Lift_D1_Train'] - row['Lift_D1_Val']
            flag = "⚠️" if auc_diff > 0.05 else "✓"
            print(f"    {flag} {row['Model']:<20}  AUC diff: {auc_diff:+.4f}  "
                  f"Lift diff: {lift_diff:+.3f}")
        print(f"{'='*90}\n")

    def get_winner(self) -> str:
        if self.comparison_df is None:
            return None
        return self.comparison_df.iloc[0]['Model']

    def get_comparison_df(self) -> pd.DataFrame:
        return self.comparison_df

    def get_decile_table(self, model_name: str, dataset: str = 'val') -> pd.DataFrame:
        if model_name not in self.models:
            return None
        d = self.models[model_name]
        if dataset == 'val':
            return build_decile_table(self.y_val.values, d['y_val_prob'])
        return build_decile_table(self.y_train.values, d['y_train_prob'])

    def show_decile_table(self, model_name: str, dataset: str = 'val'):
        dt = self.get_decile_table(model_name, dataset)
        if dt is not None:
            show_decile_table(dt, model_name)

    def get_confusion_matrix(self, model_name: str, dataset: str = 'val') -> pd.DataFrame:
        if model_name not in self.models:
            return None
        d = self.models[model_name]
        y_true = self.y_val  if dataset == 'val' else self.y_train
        y_pred = d['y_val_pred'] if dataset == 'val' else d['y_train_pred']
        return get_confusion_matrix(y_true, y_pred)

    def save_report(self):
        """Save evaluation report to Excel."""
        if self.comparison_df is None:
            print("  Run evaluate_all() first.")
            return
        path = os.path.join(self.reports_path, 'model_evaluation_report.xlsx')
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            self.comparison_df.to_excel(writer, sheet_name='Model_Comparison', index=False)
            for name in self.models:
                dt = self.get_decile_table(name, 'val')
                if dt is not None:
                    sheet = f"Decile_{name.replace(' ', '_')[:20]}"
                    dt.to_excel(writer, sheet_name=sheet, index=False)
        print(f"  ✓ Report saved: reports/model_evaluation_report.xlsx")
