"""
pages/ingestion.py
===================
Data ingestion page — drag-and-drop file upload or load from client folder.
"""

import os
import streamlit as st
import pandas as pd
from ui.components import page_header, divider, success, warn, error


def render():
    page_header("Data Ingestion", "Upload your CSV or TXT file to get started")

    if not st.session_state.client:
        warn("Please select a client on the Home page first.")
        return

    client      = st.session_state.client
    client_path = st.session_state.client_path

    # ── Option 1: File upload ──────────────────────────────────
    st.markdown("#### Upload File")
    uploaded = st.file_uploader(
        "Drag and drop your data file here",
        type=["csv", "txt"],
        help="Accepts CSV or tab-delimited TXT files",
    )

    if uploaded:
        # Save to client folder
        save_dir  = os.path.join(client_path, "data", "raw")
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, uploaded.name)

        with open(save_path, "wb") as f:
            f.write(uploaded.getbuffer())

        st.caption(f"Saved to: data/raw/{uploaded.name}")

        if st.button("Load Uploaded File", type="primary"):
            _load_file(save_path, client)

    divider()

    # ── Option 2: Load from folder ─────────────────────────────
    st.markdown("#### Or Load Existing File")

    raw_path = os.path.join(client_path, "data", "raw")
    files    = []

    # Scan client root and data/raw
    for scan_path in [client_path, raw_path]:
        if os.path.exists(scan_path):
            for f in os.listdir(scan_path):
                if f.lower().endswith((".csv", ".txt")):
                    files.append(os.path.join(scan_path, f))

    if files:
        file_labels = [os.path.basename(f) for f in files]
        chosen_label = st.selectbox("Available files", file_labels)
        chosen_path  = files[file_labels.index(chosen_label)]

        if st.button("Load Selected File", type="secondary"):
            _load_file(chosen_path, client)
    else:
        st.caption("No files found in client folder yet. Upload one above.")

    # ── Current data summary ───────────────────────────────────
    if st.session_state.df is not None:
        divider()
        st.markdown("#### Loaded Data")
        df = st.session_state.df

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Rows",       f"{len(df):,}")
        col2.metric("Columns",    f"{len(df.columns):,}")
        col3.metric("Numeric",    f"{len(df.select_dtypes('number').columns):,}")
        col4.metric("Categorical",f"{len(df.select_dtypes('object').columns):,}")

        st.markdown("**Column preview**")
        st.dataframe(
            df.head(5),
            use_container_width=True,
            height=200,
        )

        # Target distribution
        target = st.session_state.target
        if target in df.columns:
            st.markdown(f"**Target distribution — `{target}`**")
            dist = df[target].value_counts().reset_index()
            dist.columns = [target, "Count"]
            dist["Pct"] = (dist["Count"] / len(df) * 100).round(1)
            st.dataframe(dist, use_container_width=True, hide_index=True)
        else:
            st.caption(f"Target column `{target}` not found. Check Settings.")

        if st.button("▶  Proceed to Data Cleaning", type="primary"):
            st.session_state.page = "cleaning"
            st.rerun()


def _load_file(file_path: str, client: str):
    """Load a file using existing data.ingestion module."""
    try:
        from data.ingestion import detect_delimiter
        import pandas as pd

        with st.spinner("Loading data..."):
            delimiter = detect_delimiter(file_path)
            try:
                df = pd.read_csv(file_path, delimiter=delimiter,
                                 low_memory=False, encoding="utf-8",
                                 on_bad_lines="warn")
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, delimiter=delimiter,
                                 low_memory=False, encoding="latin-1",
                                 on_bad_lines="warn")

        st.session_state.df       = df
        st.session_state.df_clean = df.copy()
        st.session_state.cleaner  = None

        _add_log(f"Loaded {os.path.basename(file_path)} — "
                 f"{len(df):,} rows × {len(df.columns):,} cols")
        success(f"Loaded {len(df):,} rows × {len(df.columns):,} columns")
        st.rerun()

    except Exception as e:
        error(f"Could not load file: {e}")


def _add_log(msg: str):
    import datetime
    st.session_state.log.append(
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    )
