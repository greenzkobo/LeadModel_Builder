"""
pages/segmentation.py
======================
Segmentation page — cluster your dataset before modeling.
Supports K-Means, DBSCAN, and UMAP+HDBSCAN.
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ui.components import page_header, divider, warn


def render():
    page_header("Segmentation", "Divide your dataset into customer segments before modeling")

    if st.session_state.df_clean is None:
        warn("Clean your data first on the Cleaning page.")
        return

    df     = st.session_state.df_clean
    target = st.session_state.target
    client = st.session_state.client

    # ── Persistent message ─────────────────────────────────────
    if st.session_state.get("seg_msg"):
        msg, detail = st.session_state.seg_msg
        st.success(f"✓ {msg}")
        if detail:
            st.caption(detail)
        st.session_state.seg_msg = None

    # ── Shape + feature selector ───────────────────────────────
    numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns
                    if c != target]

    col1, col2 = st.columns(2)
    col1.metric("Rows",     f"{df.shape[0]:,}")
    col2.metric("Features", f"{len(numeric_cols):,}")

    st.markdown("#### Select Features for Clustering")
    st.caption("Choose which columns to use. Fewer focused features = better clusters.")

    feature_cols = st.multiselect(
        "Features", numeric_cols,
        default=numeric_cols[:min(20, len(numeric_cols))],
        key="seg_features",
        label_visibility="collapsed",
    )

    if not feature_cols:
        warn("Select at least 2 features.")
        return

    divider()

    # ── Algorithm tabs ─────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔵 K-Means", "🟠 DBSCAN",
        "🟣 UMAP + HDBSCAN", "📊 Results & Export"
    ])

    with tab1:
        _render_kmeans(df, feature_cols, target)
    with tab2:
        _render_dbscan(df, feature_cols, target)
    with tab3:
        _render_umap(df, feature_cols, target)
    with tab4:
        _render_results(df, target, client)


# ── K-Means ────────────────────────────────────────────────────

def _render_kmeans(df, feature_cols, target):
    st.markdown("**K-Means** — fast, works well on large data, equal-sized clusters.")

    max_k = st.slider("Max k to evaluate", 3, 15, 8, key="km_maxk")

    if st.button("▶  Run Elbow Analysis", type="primary", key="km_elbow"):
        try:
            from segmentation.kmeans import preprocess, run_elbow, plot_elbow
            with st.spinner("Running elbow analysis..."):
                X    = preprocess(df, feature_cols)
                data = run_elbow(X, max_k)
                fig  = plot_elbow(data)
            st.session_state.km_elbow_data = data
            st.pyplot(fig, use_container_width=True)
            plt.close()
            best_k = data["k_range"][int(np.argmax(data["silhouettes"]))]
            st.info(f"💡 Suggested k = **{best_k}** based on silhouette score")
        except Exception as e:
            st.error(f"Elbow analysis failed: {e}")

    k = st.slider("Number of clusters (k)", 2, 15, 3, key="km_k")

    if st.button("▶  Run K-Means", type="primary", key="km_run"):
        _run_algorithm("kmeans", df, feature_cols, target, k=k)


# ── DBSCAN ─────────────────────────────────────────────────────

def _render_dbscan(df, feature_cols, target):
    st.markdown("**DBSCAN** — finds natural clusters, handles outliers as noise.")

    min_samples = st.slider("Min samples", 3, 50, 5, key="db_minsamp")

    if st.button("▶  Show Epsilon Guide", key="db_eps_btn"):
        try:
            from segmentation.dbscan import preprocess, plot_epsilon_curve
            with st.spinner("Computing k-distance graph..."):
                X   = preprocess(df, feature_cols)
                fig = plot_epsilon_curve(X, min_samples)
            st.pyplot(fig, use_container_width=True)
            plt.close()
            st.caption("Choose epsilon at the elbow point of the curve above.")
        except Exception as e:
            st.error(f"Failed: {e}")

    eps = st.number_input("Epsilon", min_value=0.01, max_value=10.0,
                          value=0.5, step=0.05, key="db_eps")

    if st.button("▶  Run DBSCAN", type="primary", key="db_run"):
        _run_algorithm("dbscan", df, feature_cols, target, eps=eps,
                       min_samples=min_samples)


# ── UMAP + HDBSCAN ─────────────────────────────────────────────

def _render_umap(df, feature_cols, target):
    st.markdown("**UMAP + HDBSCAN** — best for complex real-world customer segments.")
    st.caption("UMAP reduces dimensions preserving structure. HDBSCAN finds variable-density clusters.")

    col1, col2, col3 = st.columns(3)
    with col1:
        n_neighbors = st.slider("UMAP neighbors", 5, 50, 15, key="um_nbrs")
    with col2:
        min_dist = st.slider("UMAP min dist", 0.0, 0.9, 0.1, 0.05, key="um_dist")
    with col3:
        min_cluster = st.slider("Min cluster size", 10, 500, 50, key="um_mcs")

    if st.button("▶  Run UMAP + HDBSCAN", type="primary", key="um_run"):
        _run_algorithm("umap_hdbscan", df, feature_cols, target,
                       n_neighbors=n_neighbors, min_dist=min_dist,
                       min_cluster_size=min_cluster)


# ── Results & Export ───────────────────────────────────────────

def _render_results(df, target, client):
    labels = st.session_state.get("seg_labels")
    algo   = st.session_state.get("seg_algo", "")

    if labels is None:
        st.info("Run a clustering algorithm first (K-Means, DBSCAN, or UMAP+HDBSCAN).")
        return

    from segmentation.profiler import (
        get_cluster_sizes, build_profile, plot_cluster_means
    )

    feature_cols = st.session_state.get("seg_features", [])

    # ── Cluster sizes ──────────────────────────────────────────
    st.markdown(f"#### Results — {algo.upper()}")
    sizes = get_cluster_sizes(labels)
    col1, col2, col3 = st.columns(3)
    n_clusters = (sizes["Cluster"] != -1).sum()
    n_noise    = int((labels == -1).sum())
    col1.metric("Clusters Found", n_clusters)
    col2.metric("Total Records",  f"{len(labels):,}")
    col3.metric("Noise Points",   f"{n_noise:,}")
    st.dataframe(sizes, use_container_width=True, hide_index=True)

    divider()

    # ── Profile ────────────────────────────────────────────────
    st.markdown("#### Cluster Profiles")
    if feature_cols:
        try:
            profile = build_profile(df, labels, feature_cols, target)
            st.dataframe(profile, use_container_width=True, hide_index=True)
            fig = plot_cluster_means(df, labels, feature_cols)
            st.pyplot(fig, use_container_width=True)
            plt.close()
        except Exception as e:
            st.caption(f"Profile unavailable: {e}")

    divider()

    # ── Export ─────────────────────────────────────────────────
    st.markdown("#### Split & Save for Modeling")
    st.caption(
        "Save each cluster as a separate dataset. "
        "Each can then be loaded as a new client and modeled independently."
    )

    exclude_noise = st.checkbox("Exclude noise points (cluster -1)", value=True)

    if st.button("💾  Save Cluster Datasets", type="primary", key="seg_save"):
        try:
            from segmentation.splitter import split_by_cluster
            results = split_by_cluster(df, labels, client, algo, exclude_noise)
            st.session_state.seg_msg = (
                f"Saved {len(results)} cluster datasets",
                "Go to Home → create a new client → load each cluster file to model separately"
            )
            for cid, info in results.items():
                st.success(
                    f"Cluster {cid}: {info['shape'][0]:,} rows × "
                    f"{info['shape'][1]:,} cols → `{info['filename']}`"
                )
        except Exception as e:
            st.error(f"Save failed: {e}")


# ── Shared runner ──────────────────────────────────────────────

def _run_algorithm(algo: str, df, feature_cols, target, **kwargs):
    """Run selected algorithm, store labels in session state."""
    try:
        with st.spinner(f"Running {algo}..."):
            if algo == "kmeans":
                from segmentation.kmeans import preprocess, run_kmeans
                X      = preprocess(df, feature_cols)
                labels = run_kmeans(X, kwargs["k"])

            elif algo == "dbscan":
                from segmentation.dbscan import preprocess, run_dbscan, get_dbscan_summary
                X      = preprocess(df, feature_cols)
                labels = run_dbscan(X, kwargs["eps"], kwargs["min_samples"])
                summary = get_dbscan_summary(labels)
                st.info(
                    f"Found **{summary['n_clusters']}** clusters · "
                    f"Noise: **{summary['n_noise']:,}** points "
                    f"({summary['noise_pct']}%)"
                )

            elif algo == "umap_hdbscan":
                from segmentation.umap_hdbscan import preprocess, run_umap_hdbscan, plot_umap_clusters
                X = preprocess(df, feature_cols)
                labels, embedding, _ = run_umap_hdbscan(
                    X,
                    n_neighbors      = kwargs["n_neighbors"],
                    min_dist         = kwargs["min_dist"],
                    min_cluster_size = kwargs["min_cluster_size"],
                )
                fig = plot_umap_clusters(embedding, labels)
                st.pyplot(fig, use_container_width=True)
                plt.close()

        st.session_state.seg_labels = labels
        st.session_state.seg_algo   = algo
        n_clusters = len(set(labels) - {-1})
        st.success(f"✓ Found **{n_clusters}** clusters across {len(labels):,} records — see Results & Export tab")
        import datetime
        st.session_state.log.append(
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] "
            f"Segmentation: {algo} → {n_clusters} clusters"
        )

    except Exception as e:
        st.error(f"{algo} failed: {e}")
        import traceback
        st.code(traceback.format_exc())
