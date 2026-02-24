"""
pages/export.py
================
Export page — scoring code, model pickle, and summary report.
"""

import streamlit as st
from ui.components import page_header, divider, warn, success


def render():
    page_header("Export", "Export scoring code and generate reports")

    if st.session_state.evaluator is None:
        warn("Evaluate models first on the Evaluation page.")
        return

    trainer   = st.session_state.trainer
    evaluator = st.session_state.evaluator
    client    = st.session_state.client
    winner    = evaluator.get_winner()
    models    = list(trainer.get_trained_models().keys())

    # ── Scoring code export ────────────────────────────────────
    st.markdown("#### Scoring Code")
    st.caption("Exports a standalone Python file with the model embedded — ready for production.")

    col1, col2 = st.columns([2, 1])
    with col1:
        export_choice = st.selectbox(
            "Model to export",
            ["Winner only"] + models,
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📤  Export Scoring Code", type="primary", use_container_width=True):
            _export_scoring(export_choice, trainer, evaluator, client, winner, models)

    divider()

    # ── Report generation ──────────────────────────────────────
    st.markdown("#### Summary Report")
    st.caption("Generates model_summary_report.txt and model_summary_data.xlsx in reports/")

    if st.button("📋  Generate Full Report", use_container_width=True):
        _generate_report(trainer, evaluator, client)

    divider()

    # ── Output file links ──────────────────────────────────────
    st.markdown("#### Output Files")
    client_path = st.session_state.client_path

    if client_path:
        import os
        output_files = [
            ("Scoring code",    os.path.join(client_path, "outputs", "scoring_code")),
            ("Visualizations",  os.path.join(client_path, "outputs", "visualizations")),
            ("Reports",         os.path.join(client_path, "reports")),
            ("Models",          os.path.join(client_path, "models")),
        ]
        for label, path in output_files:
            if os.path.exists(path):
                files = os.listdir(path)
                st.markdown(f"**{label}** — `{path}`")
                for f in sorted(files)[:8]:
                    st.caption(f"  · {f}")
            else:
                st.caption(f"**{label}** — not generated yet")


def _export_scoring(export_choice, trainer, evaluator, client, winner, models):
    try:
        from export import ScoringCodeExporter
        with st.spinner("Exporting..."):
            exporter = ScoringCodeExporter(trainer, client=client)
            if export_choice == "Winner only":
                exporter.export_winner(evaluator)
                exported = [winner]
            else:
                exporter.export_model(export_choice, evaluator=evaluator)
                exported = [export_choice]

        _log(f"Exported scoring code: {', '.join(exported)}")
        success(f"Exported: {', '.join(exported)}")
        st.rerun()
    except Exception as e:
        st.error(f"Export failed: {e}")


def _generate_report(trainer, evaluator, client):
    try:
        from reports import ReportGenerator
        with st.spinner("Generating report..."):
            rg = ReportGenerator(
                trainer, evaluator,
                st.session_state.selector,
                client=client,
            )
            rg.generate_full_report()
        _log("Generated full summary report")
        success("Report saved to reports/")
        st.rerun()
    except Exception as e:
        st.error(f"Report generation failed: {e}")


def _log(msg: str):
    import datetime
    st.session_state.log.append(
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    )
