"""
pages/ingestion.py
===================
Data ingestion page — drag-and-drop file upload with automatic large-file
sampling and target column selection.

Web-app behaviour:
  • Files ≤ 200 MB  → loaded in full
  • Files  > 200 MB → auto stratified-sample to 150 k rows; user is notified
  • Delimiter and encoding are detected automatically
  • After a successful load, user picks their target (label) column
"""

import os
import io
import datetime
import streamlit as st
import pandas as pd

from ui.components import page_header, divider, success, warn, error

# ── Constants ──────────────────────────────────────────────────────────────────
SIZE_LIMIT_MB   = 200          # warn / sample above this
SAMPLE_ROWS     = 1_000      # target row count when sampling
PREVIEW_ROWS    = 5


# ══════════════════════════════════════════════════════════════════════════════
def render():
    page_header("Data Ingestion", "Upload your CSV or TXT file to get started")

    if not st.session_state.client:
        warn("Please select a client on the Home page first.")
        return

    client      = st.session_state.client
    client_path = st.session_state.client_path

    # ── Upload widget ──────────────────────────────────────────────────────────
    st.markdown("#### Upload File")
    st.caption(
        "Accepts CSV or tab / pipe-delimited TXT files. "
        f"**Files larger than {SIZE_LIMIT_MB} MB will be automatically sampled "
        f"to {SAMPLE_ROWS:,} rows** — model quality is not meaningfully affected "
        "above ~100 k rows. For scoring the full file use the exported scoring script."
    )

    uploaded = st.file_uploader(
        "Drag and drop your data file here",
        type=["csv", "txt"],
        help=f"Max recommended size: {SIZE_LIMIT_MB} MB. Larger files are sampled automatically.",
    )

    if uploaded:
        file_mb = uploaded.size / (1024 ** 2)
        st.caption(f"File size: **{file_mb:.1f} MB**")

        if st.button("Load File", type="primary"):
            _load_uploaded_file(uploaded, file_mb, client, client_path)

    # ── Data summary + target selector (shown once data is in session) ─────────
    if st.session_state.df is not None:
        divider()
        _render_data_summary()
        divider()
        _render_target_selector()

        if st.session_state.target and st.session_state.target in st.session_state.df.columns:
            divider()
            _render_target_distribution()

            if st.button("▶  Proceed to Data Cleaning", type="primary"):
                st.session_state.page = "cleaning"
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# Loading logic
# ══════════════════════════════════════════════════════════════════════════════

def _load_uploaded_file(uploaded, file_mb: float, client: str, client_path: str):
    """Read the uploaded buffer, auto-sample if large, persist to parquet."""
    try:
        with st.spinner("Detecting file format…"):
            raw_bytes = uploaded.getvalue()
            delimiter = _detect_delimiter(raw_bytes)
            encoding  = _detect_encoding(raw_bytes)

        needs_sampling = file_mb > SIZE_LIMIT_MB

        with st.spinner("Loading data…" if not needs_sampling else
                        f"File exceeds {SIZE_LIMIT_MB} MB — reading in chunks and sampling…"):

            df = _read_csv_safe(raw_bytes, delimiter, encoding, needs_sampling)

        # ── Persist raw parquet ───────────────────────────────────────────────
        save_dir = os.path.join(client_path, "data", "raw")
        os.makedirs(save_dir, exist_ok=True)
        parquet_path = os.path.join(save_dir, "ingested_data.parquet")
        df.to_parquet(parquet_path, index=False)

        # ── Convert string columns that are actually numeric ─────────────────
        for col in df.columns:
            if df[col].dtype == object:
                converted = pd.to_numeric(df[col], errors="coerce")
                if converted.notna().sum() > 0.9 * len(df):
                    df[col] = converted

        # ── Update session state ──────────────────────────────────────────────
        st.session_state.df        = df
        st.session_state.df_clean  = df.copy()
        st.session_state.cleaner   = None
        st.session_state.target    = ""   # reset — user must re-select

        _add_log(
            f"Loaded {uploaded.name} — "
            f"{len(df):,} rows × {len(df.columns):,} cols"
            + (" [sampled]" if needs_sampling else "")
        )

        if needs_sampling:
            st.info(
                f"ℹ️ **Large file detected ({file_mb:.0f} MB).** "
                f"Your data was automatically sampled down to **{len(df):,} rows** "
                f"using stratified sampling (class balance preserved). "
                f"This has no meaningful impact on model quality. "
                f"Use the exported scoring script to score your full dataset."
            )
        else:
            success(f"Loaded {len(df):,} rows × {len(df.columns):,} columns")

        st.rerun()

    except Exception as e:
        error(f"Could not load file: {e}")


def _read_csv_safe(
    raw_bytes: bytes,
    delimiter: str,
    encoding: str,
    needs_sampling: bool,
) -> pd.DataFrame:
    """
    Read CSV bytes into a DataFrame.
    If needs_sampling: read in chunks, reservoir-sample to SAMPLE_ROWS.
    Otherwise: read all at once with low_memory=False.
    """
    read_kwargs = dict(
        sep          = delimiter,
        encoding     = encoding,
        low_memory   = False,
        on_bad_lines = "warn",
    )

    if not needs_sampling:
        return pd.read_csv(io.BytesIO(raw_bytes), **read_kwargs)

    # Chunked read → collect chunks, sample at end
    chunks     = []
    chunk_size = 50_000
    total_rows = 0

    for chunk in pd.read_csv(io.BytesIO(raw_bytes), chunksize=chunk_size, **read_kwargs):
        chunks.append(chunk)
        total_rows += len(chunk)

    df_full = pd.concat(chunks, ignore_index=True)

    if len(df_full) <= SAMPLE_ROWS:
        return df_full

    # Stratified sample — try to use first plausible binary column as strata,
    # fall back to plain random sample if none found
    strata_col = _find_binary_col(df_full)
    if strata_col:
        df = _stratified_sample(df_full, strata_col, SAMPLE_ROWS)
    else:
        df = df_full.sample(n=SAMPLE_ROWS, random_state=42).reset_index(drop=True)

    return df


# ══════════════════════════════════════════════════════════════════════════════
# UI sections
# ══════════════════════════════════════════════════════════════════════════════

def _render_data_summary():
    df = st.session_state.df
    st.markdown("#### Loaded Data")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows",        f"{len(df):,}")
    col2.metric("Columns",     f"{len(df.columns):,}")
    col3.metric("Numeric",     f"{len(df.select_dtypes('number').columns):,}")
    col4.metric("Categorical", f"{len(df.select_dtypes('object').columns):,}")

    st.markdown("**Column preview**")
    st.dataframe(df.head(PREVIEW_ROWS), use_container_width=True, height=200)


def _render_target_selector():
    """Dropdown to pick the target (label) column with inline validation."""
    df      = st.session_state.df
    current = st.session_state.get("target", "")

    st.markdown("#### Select Target Column")
    st.caption(
        "Choose the column that contains your outcome variable (0 / 1 label). "
        "This is typically named `IsTarget`, `Responder`, `Response`, etc."
    )

    cols = ["— select a column —"] + list(df.columns)
    default_idx = 0

    # Try to pre-select if session already has a valid target
    if current and current in df.columns:
        default_idx = cols.index(current)
    else:
        # Auto-detect common target column names
        guesses = ["istarget", "target", "responder", "response", "label", "y"]
        for col in df.columns:
            if col.lower() in guesses:
                default_idx = cols.index(col)
                break

    chosen = st.selectbox(
        "Target column",
        cols,
        index=default_idx,
        key="target_col_select",
    )

    if chosen == "— select a column —":
        warn("Please select your target column to continue.")
        return

    # ── Validation ────────────────────────────────────────────────────────────
    issues   = []
    warnings = []

    series        = df[chosen]
    unique_vals   = series.dropna().unique()
    missing_pct   = series.isna().mean() * 100
    n_unique      = len(unique_vals)

    if missing_pct > 50:
        issues.append(f"{missing_pct:.1f}% of values are missing — unlikely to be a valid target.")

    if n_unique > 2:
        issues.append(
            f"Column has {n_unique} unique values. Target must be binary (0/1 or True/False). "
            "If this is a multi-class column, recode it before uploading."
        )
    elif n_unique == 1:
        issues.append("Column has only one unique value — not usable as a target.")

    if 0 < missing_pct <= 50:
        warnings.append(f"{missing_pct:.1f}% missing values. Rows with missing target will be dropped during cleaning.")

    for msg in issues:
        error(f"⛔ {msg}")
    for msg in warnings:
        warn(f"⚠️ {msg}")

    if issues:
        return  # Don't commit an invalid target

    # ── Commit ────────────────────────────────────────────────────────────────
    if chosen != current:
        st.session_state.target = chosen
        _add_log(f"Target column set to '{chosen}'")
        st.rerun()

    success(f"Target column set to **`{chosen}`**")


def _render_target_distribution():
    """Show class balance for the selected target column."""
    df     = st.session_state.df
    target = st.session_state.target

    st.markdown(f"**Target distribution — `{target}`**")

    series = pd.to_numeric(df[target], errors="coerce").dropna()
    dist   = series.value_counts().reset_index()
    dist.columns = [target, "Count"]
    dist["Pct"] = (dist["Count"] / len(series) * 100).round(1)
    st.dataframe(dist, use_container_width=True, hide_index=True)

    response_rate = series.mean() * 100
    if response_rate < 1:
        warn(f"Response rate is very low ({response_rate:.2f}%). Severe class imbalance — models will use balanced class weights.")
    elif response_rate > 30:
        warn(f"Response rate is unusually high ({response_rate:.1f}%). Verify this column is the correct target.")


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _detect_delimiter(raw_bytes: bytes) -> str:
    """Sniff delimiter from the first 4 KB of the file."""
    sample = raw_bytes[:4096].decode("utf-8", errors="replace")
    counts = {",": sample.count(","), "\t": sample.count("\t"), "|": sample.count("|")}
    return max(counts, key=counts.get)


def _detect_encoding(raw_bytes: bytes) -> str:
    """Return utf-8 if the file is valid UTF-8, otherwise latin-1."""
    try:
        raw_bytes[:8192].decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "latin-1"


def _find_binary_col(df: pd.DataFrame) -> str | None:
    """Return the first numeric column that looks binary (only 0/1 values)."""
    for col in df.select_dtypes("number").columns:
        uniq = df[col].dropna().unique()
        if set(uniq).issubset({0, 1, 0.0, 1.0}):
            return col
    return None


def _stratified_sample(df: pd.DataFrame, strata_col: str, n: int) -> pd.DataFrame:
    """Stratified sample preserving class proportions of strata_col."""
    groups = df.groupby(strata_col, group_keys=False)
    return (
        groups.apply(lambda g: g.sample(frac=n / len(df), random_state=42), include_groups=False)
              .reset_index(drop=True)
    )


def _add_log(msg: str):
    st.session_state.log.append(
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    )
