"""
models/__init__.py
==================
Public API for the models package.

Usage (unchanged from old model_training.py / model_evaluation.py):
    from models import ModelTrainer, ModelEvaluator

    trainer = ModelTrainer(df, client="Humana", target="IsTarget")
    trainer.train_all()

    evaluator = ModelEvaluator(trainer, client="Humana")
    evaluator.evaluate_all()
    evaluator.show_comparison()
    print(evaluator.get_winner())
"""

from .trainer import ModelTrainer
from .evaluator import ModelEvaluator

__all__ = ['ModelTrainer', 'ModelEvaluator']
