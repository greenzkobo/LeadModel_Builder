"""
export/scoring_code.py
=======================
Generates standalone Python scoring code (JMP-style).
The output file is self-contained — model is embedded as base64.
"""

import os
import pickle
import base64
from datetime import datetime


def _clean_name(model_name: str) -> str:
    return model_name.lower().replace(' ', '_')


def _header(model_name: str, client: str, target: str) -> str:
    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    return f'''"""
Scoring Code — {model_name}
{'='*50}
Client:    {client}
Target:    {target}
Created:   {ts}
Algorithm: {model_name}

Usage:
    from {_clean_name(model_name)}_scoring import score, getInputMetadata

    indata  = {{"feature1": value1, "feature2": value2, ...}}
    outdata = {{}}
    score(indata, outdata)

    print(outdata["Prob(IsTarget==1)"])   # Probability of positive class
    print(outdata["Prediction"])           # Predicted class (0 or 1)

    # Score a full dataframe
    df["Prob_1"] = df.apply(lambda row: score_row(row), axis=1)
"""

import numpy as np
import pickle
import base64

'''


def _metadata_functions(model_name: str, client: str, target: str,
                        numeric_cols: list, categorical_cols: list) -> str:
    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    input_meta = {c: "float" for c in numeric_cols}
    input_meta.update({c: "str" for c in categorical_cols})
    meta_str = "{\n" + "".join(f'        "{k}": "{v}",\n'
                                for k, v in input_meta.items()).rstrip(",\n") + "\n    }"
    return f'''
def getModelMetadata():
    return {{
        "creator":    "{model_name}",
        "modelName":  "{client}_{_clean_name(model_name)}",
        "predicted":  "{target}",
        "client":     "{client}",
        "timestamp":  "{ts}",
    }}

def getInputMetadata():
    return {meta_str}

def getOutputMetadata():
    return {{
        "Prob(IsTarget==1)": "float",
        "Prob(IsTarget==0)": "float",
        "Prediction":        "int",
    }}

'''


def _label_encoder_code(categorical_cols: list, label_encoders: dict) -> str:
    if not categorical_cols:
        return "\n# No categorical encoding required\n"

    code = "\n# Label encoding mappings\nLABEL_MAPPINGS = {\n"
    for col in categorical_cols:
        if col in label_encoders:
            le      = label_encoders[col]
            mapping = {str(cls): int(idx) for idx, cls in enumerate(le.classes_)}
            code   += f'    "{col}": {mapping},\n'
    code += "}\n\n"
    code += '''def encode_categorical(value, column):
    if column not in LABEL_MAPPINGS:
        return 0
    mapping  = LABEL_MAPPINGS[column]
    str_val  = str(value) if value is not None else "MISSING"
    return mapping.get(str_val, 0)

'''
    return code


def _model_serialization(model) -> str:
    model_b64 = base64.b64encode(pickle.dumps(model)).decode('utf-8')
    chunks    = [model_b64[i:i+80] for i in range(0, len(model_b64), 80)]
    code      = "\n# Serialized model (base64)\nMODEL_DATA = (\n"
    for chunk in chunks:
        code += f'    "{chunk}"\n'
    code += ")\n\n"
    code += '''def _load_model():
    return pickle.loads(base64.b64decode(MODEL_DATA))

_MODEL = _load_model()

'''
    return code


def _score_functions(feature_names: list,
                     numeric_cols: list, categorical_cols: list) -> str:
    feat_list = ", ".join(f'"{f}"' for f in feature_names)
    return f'''
FEATURE_NAMES         = [{feat_list}]
NUMERIC_FEATURES      = {numeric_cols}
CATEGORICAL_FEATURES  = {categorical_cols}


def prepare_input(indata):
    features = []
    for col in FEATURE_NAMES:
        value = indata.get(col, None)
        if col in CATEGORICAL_FEATURES:
            features.append(encode_categorical(value, col))
        else:
            try:
                v = float(value) if value is not None else 0.0
                features.append(0.0 if (v != v) else v)   # NaN check
            except (ValueError, TypeError):
                features.append(0.0)
    return np.array(features).reshape(1, -1)


def score(indata, outdata):
    X           = prepare_input(indata)
    prediction  = _MODEL.predict(X)[0]
    proba       = _MODEL.predict_proba(X)[0]
    outdata["Prob(IsTarget==0)"] = float(proba[0])
    outdata["Prob(IsTarget==1)"] = float(proba[1])
    outdata["Prediction"]        = int(prediction)
    return int(prediction)


def score_row(row):
    outdata = {{}}
    score(row.to_dict(), outdata)
    return outdata["Prob(IsTarget==1)"]


def score_dataframe(df):
    import pandas as pd
    results = []
    for _, row in df.iterrows():
        outdata = {{}}
        score(row.to_dict(), outdata)
        results.append(outdata)
    return pd.concat([df.reset_index(drop=True), pd.DataFrame(results)], axis=1)


if __name__ == "__main__":
    print(f"Model: {{getModelMetadata()['creator']}}")
    print(f"Features required: {{len(FEATURE_NAMES)}}")
'''


def generate_scoring_code(model, model_name: str, client: str, target: str,
                           feature_names: list, numeric_cols: list,
                           categorical_cols: list,
                           label_encoders: dict) -> str:
    """Assemble and return the full scoring Python file as a string."""
    return (
        _header(model_name, client, target)
        + _metadata_functions(model_name, client, target, numeric_cols, categorical_cols)
        + _label_encoder_code(categorical_cols, label_encoders)
        + _model_serialization(model)
        + _score_functions(feature_names, numeric_cols, categorical_cols)
    )


def save_scoring_code(code: str, scoring_path: str, model_name: str):
    """Write scoring code to file."""
    os.makedirs(scoring_path, exist_ok=True)
    filename = f"{_clean_name(model_name)}_scoring.py"
    path     = os.path.join(scoring_path, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print(f"  ✓ Saved: outputs/scoring_code/{filename}")
    return path
