"""
export/__init__.py
===================
Public API for the export package.

Usage (unchanged from old scoring_code_export.py):
    from export import ScoringCodeExporter

    exporter = ScoringCodeExporter(trainer, client="Humana")
    exporter.export_winner(evaluator)
    exporter.export_model("XGBoost")
"""

import os
import pickle
from datetime import datetime
from config import get_paths, create_folder_structure
from . import scoring_code as sc_mod
from . import metadata as meta_mod


class ScoringCodeExporter:
    """
    Export trained models as standalone Python scoring files.
    Also saves a .pkl and a metadata JSON alongside each export.
    """

    def __init__(self, trainer, client: str):
        self.trainer          = trainer
        self.client           = client
        self.models           = trainer.get_trained_models()
        self.feature_names    = trainer.get_feature_names()
        self.target           = trainer.target
        self.categorical_cols = trainer.categorical_cols
        self.numeric_cols     = trainer.numeric_cols
        self.label_encoders   = trainer.label_encoders

        create_folder_structure(client)
        self.scoring_path = get_paths(client)['scoring_code']

        print(f"\n{'='*60}")
        print(f"SCORING CODE EXPORTER: {client}")
        print('='*60)
        print(f"  Models available: {list(self.models.keys())}")
        print(f"  Features: {len(self.feature_names)}")
        print(f"  Output: outputs/scoring_code/")
        print(f"{'='*60}\n")

    def export_model(self, model_name: str = None,
                     evaluator=None):
        """
        Export a model as:
          - <name>_scoring.py  (standalone, self-contained)
          - <name>_model.pkl   (model + metadata pickle)
          - <name>_metadata.json

        Parameters:
        -----------
        model_name : str
            Model to export. Defaults to first model in list.
        evaluator : ModelEvaluator, optional
            If provided, validation metrics are embedded in metadata.
        """
        if model_name is None:
            model_name = list(self.models.keys())[0]

        if model_name not in self.models:
            print(f"  Model '{model_name}' not found.")
            print(f"  Available: {list(self.models.keys())}")
            return

        print(f"  Exporting {model_name}...")
        model = self.models[model_name]['model']

        # 1. Scoring code
        code = sc_mod.generate_scoring_code(
            model=model,
            model_name=model_name,
            client=self.client,
            target=self.target,
            feature_names=self.feature_names,
            numeric_cols=self.numeric_cols,
            categorical_cols=self.categorical_cols,
            label_encoders=self.label_encoders,
        )
        sc_mod.save_scoring_code(code, self.scoring_path, model_name)

        # 2. Pickle
        self._export_pickle(model_name)

        # 3. Metadata
        metrics = {}
        if evaluator and evaluator.val_metrics.get(model_name):
            m = evaluator.val_metrics[model_name]
            metrics = {
                'lift_d1_val':   m.get('Lift_Decile_1'),
                'gains_d1_val':  m.get('Gains_Decile_1'),
                'auc_val':       m.get('AUC'),
                'ks_val':        m.get('KS_Statistic'),
                'misclass_val':  m.get('Misclass_Rate'),
            }

        md = meta_mod.build_metadata(
            model_name=model_name,
            client=self.client,
            target=self.target,
            feature_names=self.feature_names,
            numeric_cols=self.numeric_cols,
            categorical_cols=self.categorical_cols,
            metrics=metrics,
        )
        meta_mod.save_metadata(md, self.scoring_path, model_name)

    def _export_pickle(self, model_name: str):
        """Save model as pickle with full context for batch scoring."""
        data = {
            'model':            self.models[model_name]['model'],
            'feature_names':    self.feature_names,
            'categorical_cols': self.categorical_cols,
            'numeric_cols':     self.numeric_cols,
            'label_encoders':   self.label_encoders,
            'target':           self.target,
            'client':           self.client,
            'model_name':       model_name,
            'exported_at':      datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        fname = f"{model_name.lower().replace(' ', '_')}_model.pkl"
        path  = os.path.join(self.scoring_path, fname)
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        print(f"  ✓ Saved: outputs/scoring_code/{fname}")

    def export_winner(self, evaluator):
        """Export only the winning model."""
        winner = evaluator.get_winner()
        if winner:
            print(f"  Exporting winner: {winner}")
            self.export_model(winner, evaluator=evaluator)
        else:
            print("  No winner found — run evaluator.evaluate_all() first.")

    def export_all(self, evaluator=None):
        """Export all trained models."""
        print("Exporting all models...")
        print("-" * 40)
        for name in self.models:
            self.export_model(name, evaluator=evaluator)
        print("-" * 40)
        print(f"  All exports saved to: outputs/scoring_code/")


__all__ = ['ScoringCodeExporter']
