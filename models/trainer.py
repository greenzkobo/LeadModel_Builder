"""
models/trainer.py
==================
Train multiple models with automatic data preparation.
Handles numeric imputation, categorical encoding, and train/val split.
"""

import os
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from config import get_paths, create_folder_structure
from models.configs import get_model_configs, CATBOOST_AVAILABLE


class ModelTrainer:
    """
    Prepare data and train multiple sklearn-compatible classifiers.
    """

    def __init__(self, df: pd.DataFrame, client: str,
                 target: str = "IsTarget",
                 test_size: float = 0.30,
                 random_state: int = 42):
        self.client = client
        self.target = target
        self.test_size = test_size
        self.random_state = random_state

        create_folder_structure(client)
        self.models_path = get_paths(client)['models']

        self._prepare_data(df)
        self.models = {}     # {name: {model, y_train_pred, y_val_pred, ...}}

        print(f"\n{'='*60}")
        print(f"MODEL TRAINER: {client}")
        print('='*60)
        print(f"  Training set:    {len(self.X_train):,} rows")
        print(f"  Validation set:  {len(self.X_val):,} rows")
        print(f"  Features:        {len(self.feature_names):,}")
        print(f"  Target:          {target}")
        dist = dict(pd.Series(self.y_train).value_counts())
        print(f"  Target dist (train): {dist}")
        print(f"{'='*60}\n")

    def _prepare_data(self, df: pd.DataFrame):
        """Impute, encode, and split data."""
        if self.target not in df.columns:
            raise ValueError(f"Target '{self.target}' not in data.")

        df = df.copy()
        df[self.target] = pd.to_numeric(df[self.target], errors='coerce')
        dropped = len(df) - df[self.target].notna().sum()
        df = df.dropna(subset=[self.target])
        if dropped > 0:
            print(f"  Note: Dropped {dropped:,} rows with missing target.")

        feature_cols = [c for c in df.columns if c != self.target]
        self.numeric_cols   = df[feature_cols].select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df[feature_cols].select_dtypes(include=['object', 'category']).columns.tolist()

        X = df[feature_cols].copy()
        y = df[self.target].copy()

        # Numeric: fill with median
        for col in self.numeric_cols:
            X[col] = pd.to_numeric(X[col], errors='coerce').fillna(X[col].median())

        # Categorical: fill mode, label-encode
        self.label_encoders = {}
        for col in self.categorical_cols:
            mode = X[col].mode()
            X[col] = X[col].fillna(mode.iloc[0] if len(mode) > 0 else 'MISSING')
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            self.label_encoders[col] = le

        self.feature_names = feature_cols
        self.cat_feature_indices = [feature_cols.index(c) for c in self.categorical_cols]

        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(
            X, y, test_size=self.test_size,
            random_state=self.random_state, stratify=y
        )

    def train_model(self, name: str, model) -> bool:
        """Train a single model and store predictions."""
        print(f"  Training {name}...", end=" ")
        t0 = datetime.now()
        try:
            if name == 'CatBoost' and CATBOOST_AVAILABLE:
                model.fit(
                    self.X_train, self.y_train,
                    cat_features=self.cat_feature_indices,
                    eval_set=(self.X_val, self.y_val),
                    verbose=False
                )
            else:
                model.fit(self.X_train, self.y_train)

            elapsed = (datetime.now() - t0).total_seconds()
            self.models[name] = {
                'model':        model,
                'y_train_pred': model.predict(self.X_train),
                'y_val_pred':   model.predict(self.X_val),
                'y_train_prob': model.predict_proba(self.X_train)[:, 1],
                'y_val_prob':   model.predict_proba(self.X_val)[:, 1],
                'train_time':   elapsed,
            }
            print(f"✓ ({elapsed:.1f}s)")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def train_all(self, models: list = None):
        """Train all available models (or a named subset)."""
        configs = get_model_configs(self.random_state)
        if models is None:
            models = list(configs.keys())

        print("Training models:")
        print("-" * 40)
        for name in models:
            cfg = configs.get(name)
            if cfg is None:
                print(f"  {name}: Unknown model, skipping.")
            elif not cfg['available']:
                print(f"  {name}: Not available (install required package).")
            else:
                self.train_model(name, cfg['model'])
        print("-" * 40)
        print(f"  Trained {len(self.models)} models.\n")

    # ------------------------------------------------------------------
    # Accessors (used by ModelEvaluator)
    # ------------------------------------------------------------------

    def get_trained_models(self) -> dict:
        return self.models

    def get_feature_names(self) -> list:
        return self.feature_names

    def get_validation_data(self) -> tuple:
        return self.X_val, self.y_val

    def get_training_data(self) -> tuple:
        return self.X_train, self.y_train

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_models(self):
        """Save all trained models as .joblib files."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        for name, data in self.models.items():
            fname = name.lower().replace(' ', '_')
            path = os.path.join(self.models_path, f"{fname}_{ts}.joblib")
            joblib.dump({
                'model':            data['model'],
                'feature_names':    self.feature_names,
                'target':           self.target,
                'label_encoders':   self.label_encoders,
                'categorical_cols': self.categorical_cols,
                'numeric_cols':     self.numeric_cols,
            }, path)
            print(f"  ✓ Saved: models/{fname}_{ts}.joblib")
        print(f"\n  All models saved to: {self.models_path}")

    def show_summary(self):
        print(f"\n{'='*60}")
        print("TRAINING SUMMARY")
        print('='*60)
        print(f"  Training rows:   {len(self.X_train):,}")
        print(f"  Validation rows: {len(self.X_val):,}")
        print(f"  Features:        {len(self.feature_names):,}")
        print(f"\n  Models trained:")
        for name, data in self.models.items():
            print(f"    - {name} ({data['train_time']:.1f}s)")
        print(f"{'='*60}\n")
