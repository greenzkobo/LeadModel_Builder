"""
models/configs.py
==================
Default hyperparameter configurations for each model.
Edit here to tune defaults without touching trainer logic.
"""

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

# Optional imports
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False


def get_model_configs(random_state: int = 42) -> dict:
    """
    Return a dict of model configs.

    Each value is:
        {'model': <sklearn estimator or None>, 'available': bool}
    """
    configs = {
        'Random Forest': {
            'model': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=random_state,
                n_jobs=-1
            ),
            'available': True
        },
        'Gradient Boosting': {
            'model': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=random_state
            ),
            'available': True
        },
        'Logistic Regression': {
            'model': LogisticRegression(
                max_iter=1000,
                random_state=random_state,
                n_jobs=-1
            ),
            'available': True
        },
        'XGBoost': {
            'model': xgb.XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=random_state,
                n_jobs=-1,
                eval_metric='logloss'
            ) if XGB_AVAILABLE else None,
            'available': XGB_AVAILABLE
        },
        'CatBoost': {
            'model': CatBoostClassifier(
                iterations=100,
                depth=6,
                learning_rate=0.1,
                random_state=random_state,
                verbose=False
            ) if CATBOOST_AVAILABLE else None,
            'available': CATBOOST_AVAILABLE
        },
    }
    return configs


# Which models are available (for informational display)
AVAILABLE_MODELS = ['Random Forest', 'Gradient Boosting', 'Logistic Regression']
if XGB_AVAILABLE:
    AVAILABLE_MODELS.append('XGBoost')
if CATBOOST_AVAILABLE:
    AVAILABLE_MODELS.append('CatBoost')
