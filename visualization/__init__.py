"""
visualization/__init__.py
==========================
Public API for the visualization package.

Usage:
    from visualization import ModelVisualizer

    viz = ModelVisualizer(trainer, evaluator, client="Humana")
    viz.plot_all()
"""

import os
import matplotlib.pyplot as plt
from config import get_paths, create_folder_structure


class ModelVisualizer:
    """
    Generate all model evaluation visualizations.
    Imports sub-modules lazily inside each method to avoid circular imports.
    """

    def __init__(self, trainer, evaluator, client: str):
        self.trainer       = trainer
        self.evaluator     = evaluator
        self.client        = client
        self.models        = trainer.get_trained_models()
        self.feature_names = trainer.get_feature_names()
        self.X_train, self.y_train = trainer.get_training_data()
        self.X_val,   self.y_val   = trainer.get_validation_data()

        create_folder_structure(client)
        self.viz_path = get_paths(client)['visualizations']

        plt.style.use('seaborn-v0_8-whitegrid')

    def _path(self, filename: str) -> str:
        return os.path.join(self.viz_path, filename)

    def _y(self, dataset: str):
        return self.y_val if dataset == 'val' else self.y_train

    def _label(self, dataset: str) -> str:
        return "Validation" if dataset == 'val' else "Training"

    def _prob_key(self, dataset: str) -> str:
        return 'y_val_prob' if dataset == 'val' else 'y_train_prob'

    def _pred_key(self, dataset: str) -> str:
        return 'y_val_pred' if dataset == 'val' else 'y_train_pred'

    def plot_roc_curves(self, dataset: str = 'val', save: bool = True):
        from visualization import roc
        roc.plot_roc_curves(
            self.models, self._y(dataset),
            dataset_label=self._label(dataset),
            prob_key=self._prob_key(dataset),
            save_path=self._path(f'roc_curves_{dataset}.png') if save else None
        )

    def plot_lift_curves(self, dataset: str = 'val', save: bool = True):
        from visualization import lift
        lift.plot_lift_curves(
            self.models, self._y(dataset),
            dataset_label=self._label(dataset),
            prob_key=self._prob_key(dataset),
            save_path=self._path(f'lift_curves_{dataset}.png') if save else None
        )

    def plot_gains_curves(self, dataset: str = 'val', save: bool = True):
        from visualization import gains
        gains.plot_gains_curves(
            self.models, self._y(dataset),
            dataset_label=self._label(dataset),
            prob_key=self._prob_key(dataset),
            save_path=self._path(f'gains_curves_{dataset}.png') if save else None
        )

    def plot_confusion_matrices(self, dataset: str = 'val', save: bool = True):
        from visualization import comparison
        comparison.plot_confusion_matrices(
            self.models, self._y(dataset),
            dataset_label=self._label(dataset),
            pred_key=self._pred_key(dataset),
            save_path=self._path(f'confusion_matrices_{dataset}.png') if save else None
        )

    def plot_feature_importance(self, model_name: str = None,
                                top_n: int = 20, save: bool = True):
        from visualization import importance
        if model_name is None:
            model_name = self.evaluator.get_winner()
        if model_name not in self.models:
            print(f"  Model '{model_name}' not found.")
            return
        model = self.models[model_name]['model']
        fname = model_name.lower().replace(' ', '_')
        importance.plot_feature_importance(
            model, self.feature_names, model_name=model_name, top_n=top_n,
            save_path=self._path(f'feature_importance_{fname}.png') if save else None
        )

    def plot_model_comparison_bar(self, save: bool = True):
        from visualization import comparison
        comp_df = self.evaluator.get_comparison_df()
        if comp_df is None:
            print("  Run evaluator.evaluate_all() first.")
            return
        comparison.plot_model_comparison_bar(
            comp_df,
            save_path=self._path('model_comparison_bar.png') if save else None
        )

    def plot_all(self, dataset: str = 'val'):
        """Generate and save every visualization."""
        self.plot_roc_curves(dataset)
        self.plot_lift_curves(dataset)
        self.plot_gains_curves(dataset)
        self.plot_confusion_matrices(dataset)
        self.plot_feature_importance()
        self.plot_model_comparison_bar()
        print(f"  All visualizations saved to: outputs/visualizations/")


__all__ = ['ModelVisualizer']