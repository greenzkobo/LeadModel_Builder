"""
features/screener.py
=====================
Column screening engine — scores every feature across 4 signals:
  1. P-value         (pointbiserial correlation with target)
  2. Importance      (quick Random Forest on sample)
  3. Max collinearity (highest Pearson r with any other feature)
  4. Variance        (normalized variance)

Returns a single DataFrame with one row per feature + suggestion.
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder


# ── Thresholds ────────────────────────────────────────────────────────────────
P_VALUE_THRESH       = 0.05    # p > threshold → weak predictor
IMPORTANCE_PCTILE    = 20      # bottom 20% by importance → weak
COLLINEARITY_THRESH  = 0.85    # r > threshold → collinear
VARIANCE_PCTILE      = 5       # bottom 5% by variance → low variance
SAMPLE_SIZE          = 15_000  # rows to use for quick RF importance


def score_features(df: pd.DataFrame, target: str) -> pd.DataFrame:
    """
    Score all features across 4 signals.
    Returns DataFrame with columns:
      Feature, P_Value, Importance, Max_Collinearity,
      Correlated_With, Variance, Missing_Pct, Zero_Pct,
      Weak_Predictor, Low_Importance, Collinear, Low_Variance,
      Flag_Count, Suggestion, Reason
    """
    feature_cols = [c for c in df.columns if c != target]
    numeric_cols = df[feature_cols].select_dtypes(include=[np.number]).columns.tolist()

    print(f"  Screening {len(feature_cols)} features...")

    # ── Signal 1: P-values ────────────────────────────────────
    p_values = _calc_p_values(df, numeric_cols, target)

    # ── Signal 2: Importance ──────────────────────────────────
    importance = _calc_importance(df, numeric_cols, target)

    # ── Signal 3: Collinearity ────────────────────────────────
    collinearity = _calc_collinearity(df, numeric_cols)

    # ── Signal 4: Variance + quality ─────────────────────────
    quality = _calc_quality(df, numeric_cols, target)

    # ── Assemble ──────────────────────────────────────────────
    rows = []
    imp_threshold = np.percentile(list(importance.values()), IMPORTANCE_PCTILE) if importance else 0
    var_threshold = np.percentile([q['variance'] for q in quality.values()], VARIANCE_PCTILE) if quality else 0

    for col in feature_cols:
        if col not in numeric_cols:
            # Skip non-numeric for now
            rows.append(_non_numeric_row(col))
            continue

        p_val   = p_values.get(col, 1.0)
        imp     = importance.get(col, 0.0)
        coll    = collinearity.get(col, {})
        qual    = quality.get(col, {})

        max_corr   = coll.get('max_corr', 0.0)
        corr_with  = coll.get('corr_with', '')
        variance   = qual.get('variance', 0.0)
        missing    = qual.get('missing_pct', 0.0)
        zero_pct   = qual.get('zero_pct', 0.0)

        # ── Flags ─────────────────────────────────────────────
        weak_pred  = p_val > P_VALUE_THRESH
        low_imp    = imp < imp_threshold
        collinear  = max_corr > COLLINEARITY_THRESH
        low_var    = variance < var_threshold

        flag_count = sum([weak_pred, low_imp, collinear, low_var])

        # ── Suggestion + reason ───────────────────────────────
        suggestion, reason = _suggest(
            flag_count, weak_pred, low_imp, collinear, low_var,
            p_val, max_corr, corr_with, variance
        )

        rows.append({
            'Feature':          col,
            'P_Value':          round(p_val, 4),
            'Importance':       round(imp, 6),
            'Max_Collinearity': round(max_corr, 3),
            'Correlated_With':  corr_with,
            'Variance':         round(variance, 6),
            'Missing_Pct':      round(missing, 1),
            'Zero_Pct':         round(zero_pct, 1),
            'Weak_Predictor':   weak_pred,
            'Low_Importance':   low_imp,
            'Collinear':        collinear,
            'Low_Variance':     low_var,
            'Flag_Count':       flag_count,
            'Suggestion':       suggestion,
            'Reason':           reason,
        })

    result = pd.DataFrame(rows).sort_values('Flag_Count', ascending=False)
    return result.reset_index(drop=True)


def get_drop_candidates(scored_df: pd.DataFrame) -> list:
    """Return list of column names suggested for dropping (flag_count >= 2)."""
    return scored_df[scored_df['Suggestion'] == '🔴 Drop']['Feature'].tolist()


def get_review_candidates(scored_df: pd.DataFrame) -> list:
    """Return list of column names flagged for review (flag_count == 1)."""
    return scored_df[scored_df['Suggestion'] == '🟡 Review']['Feature'].tolist()


# ── Private helpers ────────────────────────────────────────────────────────────

def _calc_p_values(df, cols, target):
    """Pointbiserial correlation p-value between each feature and target."""
    y = pd.to_numeric(df[target], errors='coerce')
    result = {}
    for col in cols:
        try:
            x = pd.to_numeric(df[col], errors='coerce')
            mask = ~(x.isna() | y.isna())
            if mask.sum() < 30:
                result[col] = 1.0
                continue
            _, p = stats.pointbiserialr(y[mask], x[mask])
            result[col] = float(p)
        except Exception:
            result[col] = 1.0
    return result


def _calc_importance(df, cols, target):
    """Quick Random Forest importance on a sample."""
    if not cols:
        return {}
    try:
        sample = df[cols + [target]].dropna().sample(
            min(SAMPLE_SIZE, len(df)), random_state=42
        )
        X = sample[cols].fillna(0)
        y = sample[target]
        rf = RandomForestClassifier(n_estimators=30, max_depth=6,
                                    random_state=42, n_jobs=-1)
        rf.fit(X, y)
        return dict(zip(cols, rf.feature_importances_))
    except Exception:
        return {c: 0.0 for c in cols}


def _calc_collinearity(df, cols):
    """Find max Pearson correlation with any other feature per column."""
    if len(cols) < 2:
        return {}
    try:
        corr = df[cols].fillna(0).corr().abs()
        np.fill_diagonal(corr.values, 0)
        result = {}
        for col in cols:
            max_corr = corr[col].max()
            corr_with = corr[col].idxmax() if max_corr > 0 else ''
            result[col] = {'max_corr': max_corr, 'corr_with': corr_with}
        return result
    except Exception:
        return {}


def _calc_quality(df, cols, target):
    """Variance, missing %, zero % per column."""
    result = {}
    for col in cols:
        data = pd.to_numeric(df[col], errors='coerce')
        missing_pct = data.isna().sum() / len(df) * 100
        clean = data.dropna()
        variance = float(clean.var()) if len(clean) > 1 else 0.0
        zero_pct = (clean == 0).sum() / len(clean) * 100 if len(clean) > 0 else 0.0
        result[col] = {
            'variance':    variance,
            'missing_pct': missing_pct,
            'zero_pct':    zero_pct,
        }
    return result


def _suggest(flag_count, weak_pred, low_imp, collinear, low_var,
             p_val, max_corr, corr_with, variance):
    """Return (suggestion_label, reason_string)."""
    if flag_count == 0:
        return '✅ Keep', ''

    reasons = []
    if weak_pred:
        reasons.append(f"weak predictor (p={p_val:.3f})")
    if low_imp:
        reasons.append("low importance score")
    if collinear:
        reasons.append(f"collinear with {corr_with} (r={max_corr:.2f})")
    if low_var:
        reasons.append(f"low variance ({variance:.5f})")

    reason = ' + '.join(reasons)

    if flag_count >= 2:
        return '🔴 Drop', reason
    return '🟡 Review', reason


def _non_numeric_row(col):
    return {
        'Feature': col, 'P_Value': None, 'Importance': None,
        'Max_Collinearity': None, 'Correlated_With': '',
        'Variance': None, 'Missing_Pct': None, 'Zero_Pct': None,
        'Weak_Predictor': False, 'Low_Importance': False,
        'Collinear': False, 'Low_Variance': False,
        'Flag_Count': 0, 'Suggestion': '⬜ Categorical', 'Reason': '',
    }
