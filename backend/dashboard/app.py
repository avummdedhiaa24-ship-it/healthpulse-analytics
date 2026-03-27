"""
HealthPulse Analytics Dashboard
────────────────────────────────
Streamlit frontend for the HealthPulse FastAPI backend.
Run from the project root:
    streamlit run dashboard/app.py
"""

import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="HealthPulse Analytics",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');
 
    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }
    .main { background-color: #0a0d12; }
    .stApp { background-color: #0a0d12; color: #e2eaf5; }
 
    /* Metric cards */
    [data-testid="metric-container"] {
        background: #111620;
        border: 1px solid #1f2d42;
        border-radius: 10px;
        padding: 16px;
    }
    [data-testid="metric-container"] label {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase;
        color: #6b7fa3 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif !important;
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #00c2ff !important;
    }
 
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #111620 !important;
        border-right: 1px solid #1f2d42;
    }
    [data-testid="stSidebar"] * { color: #e2eaf5 !important; }
 
    /* Headers */
    h1 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; color: #ffffff !important; }
    h2, h3 { font-family: 'Syne', sans-serif !important; color: #e2eaf5 !important; }
 
    /* Section label style */
    .section-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #00c2ff;
        margin-bottom: 4px;
    }
 
    /* Alert box */
    .drift-alert {
        background: rgba(255,107,53,0.1);
        border: 1px solid rgba(255,107,53,0.4);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        color: #ff6b35;
    }
    .drift-stable {
        background: rgba(0,255,176,0.05);
        border: 1px solid rgba(0,255,176,0.3);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        color: #00ffb0;
    }
 
    /* Divider */
    hr { border-color: #1f2d42; }
 
    /* Button */
    .stButton > button {
        background: #00c2ff !important;
        color: #0a0d12 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 6px !important;
        letter-spacing: 1px !important;
    }
    .stButton > button:hover {
        background: #00ffb0 !important;
    }
 
    /* Dataframe */
    [data-testid="stDataFrame"] { border: 1px solid #1f2d42; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# ── API helpers ─────────────────────────────────────────────────────────────

def get(endpoint: str) -> dict | list | None:
    try:
        r = requests.get(f"{API_BASE}{endpoint}", timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error(
            "⚡ Cannot connect to HealthPulse API. Is the FastAPI server running?")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def post(endpoint: str, json: dict = None) -> dict | None:
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=json, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("⚡ Cannot connect to HealthPulse API.")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


# ── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🫀 HealthPulse")
    st.markdown(
        "<p style='font-family:IBM Plex Mono,monospace;font-size:11px;"
        "color:#6b7fa3;letter-spacing:1px'>ANALYTICS PLATFORM</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["📊 Overview", "🧬 Patients", "🤖 Model Runs",
            "📡 Drift Monitor", "📤 Upload CSV"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # API health check
    health = get("/health")
    if health and health.get("status") == "ok":
        st.markdown(
            "<p style='font-family:IBM Plex Mono,monospace;font-size:11px;"
            "color:#00ffb0'>● API ONLINE</p>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<p style='font-family:IBM Plex Mono,monospace;font-size:11px;"
            "color:#ff6b35'>● API OFFLINE</p>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

if page == "📊 Overview":
    st.markdown("<p class='section-label'>01 — Dashboard</p>",
                unsafe_allow_html=True)
    st.title("HealthPulse Analytics")
    st.markdown("Real-world evidence · ML monitoring · Clinical data pipeline")
    st.markdown("---")

    # ── KPI row ───────────────────────────────────────────────────────────
    patients = get("/patients/") or []
    model_runs = get("/model-runs/") or []
    drift_summary = get("/drift-logs/summary") or {}
    drift_alerts = get("/drift-logs/alerts") or []

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Patients", len(patients))
    col2.metric("Model Runs", len(model_runs))
    col3.metric("Features Tracked", drift_summary.get("total_features", 0))
    col4.metric("Drift Alerts", len(drift_alerts),
                delta=f"{len(drift_alerts)} active", delta_color="inverse")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    # ── Patient condition breakdown ───────────────────────────────────────
    with col_left:
        st.markdown("#### 🧬 Patient Conditions")
        if patients:
            df = pd.DataFrame(patients)
            condition_counts = df["condition"].value_counts().reset_index()
            condition_counts.columns = ["condition", "count"]
            fig = px.pie(
                condition_counts, values="count", names="condition",
                color_discrete_sequence=[
                    "#00c2ff", "#00ffb0", "#ff6b35", "#c792ea", "#ffd580"],
                hole=0.45,
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2eaf5", family="IBM Plex Mono"),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No patient data yet. Upload a CSV to get started.")

    # ── Drift summary ─────────────────────────────────────────────────────
    with col_right:
        st.markdown("#### 📡 Drift Status")
        if drift_summary.get("total_features", 0) > 0:
            drifted = drift_summary.get("drifted_features", [])
            stable = drift_summary.get("stable", 0)

            for f in drifted:
                st.markdown(
                    f"<div class='drift-alert'>⚠️ &nbsp;<b>{f}</b> — DRIFT DETECTED</div>", unsafe_allow_html=True)
            if stable > 0:
                st.markdown(
                    f"<div class='drift-stable'>✅ &nbsp;<b>{stable} feature(s)</b> — STABLE</div>", unsafe_allow_html=True)

            # PSI/KS bar chart
            drift_logs = get("/drift-logs/") or []
            if drift_logs:
                df_drift = pd.DataFrame(drift_logs)
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    name="PSI Score", x=df_drift["feature_name"], y=df_drift["psi_score"],
                    marker_color="#00c2ff", opacity=0.85,
                ))
                fig2.add_trace(go.Bar(
                    name="KS Statistic", x=df_drift["feature_name"], y=df_drift["ks_statistic"],
                    marker_color="#ff6b35", opacity=0.85,
                ))
                fig2.add_hline(y=0.2, line_dash="dash", line_color="#ff6b35",
                               annotation_text="PSI threshold", annotation_font_color="#ff6b35")
                fig2.update_layout(
                    barmode="group",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e2eaf5", family="IBM Plex Mono"),
                    legend=dict(bgcolor="rgba(0,0,0,0)"),
                    xaxis=dict(gridcolor="#1f2d42"),
                    yaxis=dict(gridcolor="#1f2d42"),
                    margin=dict(t=20, b=20),
                )
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No drift data yet. Run drift detection first.")

    # ── Recent model runs ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🤖 Recent Model Performance")
    if model_runs:
        df_runs = pd.DataFrame(model_runs[:10])
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=df_runs["created_at"], y=df_runs["accuracy"],
            name="Accuracy", mode="lines+markers",
            line=dict(color="#00c2ff", width=2),
            marker=dict(size=7),
        ))
        fig3.add_trace(go.Scatter(
            x=df_runs["created_at"], y=df_runs["f1_score"],
            name="F1 Score", mode="lines+markers",
            line=dict(color="#00ffb0", width=2),
            marker=dict(size=7),
        ))
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2eaf5", family="IBM Plex Mono"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(gridcolor="#1f2d42"),
            yaxis=dict(gridcolor="#1f2d42", range=[0, 1.05]),
            margin=dict(t=20, b=20),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No model runs logged yet.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PATIENTS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🧬 Patients":
    st.markdown("<p class='section-label'>02 — Patient Data</p>",
                unsafe_allow_html=True)
    st.title("Patient Records")
    st.markdown("---")

    patients = get("/patients/") or []

    if not patients:
        st.info("No patients found. Upload a CSV to get started.")
    else:
        df = pd.DataFrame(patients)

        # ── Filters ───────────────────────────────────────────────────────
        col1, col2, col3 = st.columns(3)
        with col1:
            conditions = ["All"] + sorted(df["condition"].unique().tolist())
            selected_condition = st.selectbox(
                "Filter by Condition", conditions)
        with col2:
            genders = ["All"] + sorted(df["gender"].unique().tolist())
            selected_gender = st.selectbox("Filter by Gender", genders)
        with col3:
            age_range = st.slider("Age Range", int(df["age"].min()), int(df["age"].max()),
                                  (int(df["age"].min()), int(df["age"].max())))

        filtered = df.copy()
        if selected_condition != "All":
            filtered = filtered[filtered["condition"] == selected_condition]
        if selected_gender != "All":
            filtered = filtered[filtered["gender"] == selected_gender]
        filtered = filtered[(filtered["age"] >= age_range[0])
                            & (filtered["age"] <= age_range[1])]

        st.markdown(f"**{len(filtered)} patients** match your filters")
        st.dataframe(filtered, use_container_width=True, hide_index=True)

        st.markdown("---")

        # ── Charts ────────────────────────────────────────────────────────
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### Age Distribution")
            fig = px.histogram(filtered, x="age", nbins=10,
                               color_discrete_sequence=["#00c2ff"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(color="#e2eaf5"), xaxis=dict(gridcolor="#1f2d42"),
                              yaxis=dict(gridcolor="#1f2d42"), margin=dict(t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown("#### BMI Distribution")
            fig2 = px.histogram(filtered, x="bmi", nbins=10,
                                color_discrete_sequence=["#00ffb0"])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font=dict(color="#e2eaf5"), xaxis=dict(gridcolor="#1f2d42"),
                               yaxis=dict(gridcolor="#1f2d42"), margin=dict(t=20, b=20))
            st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MODEL RUNS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🤖 Model Runs":
    st.markdown("<p class='section-label'>03 — ML Monitoring</p>",
                unsafe_allow_html=True)
    st.title("Model Performance Tracker")
    st.markdown("---")

    # ── Log a new run ─────────────────────────────────────────────────────
    with st.expander("➕ Log New Model Run"):
        with st.form("model_run_form"):
            model_name = st.text_input(
                "Model Name", placeholder="readmission_classifier_v2")
            col1, col2 = st.columns(2)
            accuracy = col1.number_input(
                "Accuracy", min_value=0.0, max_value=1.0, value=0.90, step=0.01)
            f1 = col2.number_input(
                "F1 Score", min_value=0.0, max_value=1.0, value=0.88, step=0.01)
            submitted = st.form_submit_button("Log Run")
            if submitted and model_name:
                result = post(
                    "/model-runs/", {"model_name": model_name, "accuracy": accuracy, "f1_score": f1})
                if result:
                    st.success(
                        f"✅ Run logged for **{model_name}** — accuracy: {accuracy}, F1: {f1}")

    st.markdown("---")

    model_runs = get("/model-runs/") or []
    if not model_runs:
        st.info("No model runs logged yet.")
    else:
        df = pd.DataFrame(model_runs)
        df["created_at"] = pd.to_datetime(df["created_at"])

        # ── Model selector ────────────────────────────────────────────────
        models = df["model_name"].unique().tolist()
        selected_model = st.selectbox("Select Model", ["All"] + models)

        filtered = df if selected_model == "All" else df[df["model_name"]
                                                         == selected_model]

        # ── Performance chart ─────────────────────────────────────────────
        fig = go.Figure()
        for model in filtered["model_name"].unique():
            subset = filtered[filtered["model_name"]
                              == model].sort_values("created_at")
            fig.add_trace(go.Scatter(
                x=subset["created_at"], y=subset["accuracy"],
                name=f"{model} — Accuracy", mode="lines+markers",
                line=dict(width=2), marker=dict(size=8),
            ))
            fig.add_trace(go.Scatter(
                x=subset["created_at"], y=subset["f1_score"],
                name=f"{model} — F1", mode="lines+markers",
                line=dict(width=2, dash="dot"), marker=dict(size=8),
            ))

        fig.add_hline(y=0.8, line_dash="dash", line_color="#ff6b35",
                      annotation_text="Performance floor", annotation_font_color="#ff6b35")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2eaf5", family="IBM Plex Mono"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(gridcolor="#1f2d42"),
            yaxis=dict(gridcolor="#1f2d42", range=[0, 1.05]),
            margin=dict(t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### All Runs")
        st.dataframe(filtered[["model_name", "accuracy", "f1_score", "created_at"]],
                     use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DRIFT MONITOR
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📡 Drift Monitor":
    st.markdown("<p class='section-label'>04 — Data Drift</p>",
                unsafe_allow_html=True)
    st.title("Drift Monitor")
    st.markdown("PSI + KS statistical drift detection across patient features")
    st.markdown("---")

    # ── Run detection button ──────────────────────────────────────────────
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🚀 Run Drift Detection"):
            with st.spinner("Computing PSI + KS statistics..."):
                result = post("/drift-logs/run-detection")
            if result:
                st.success(
                    f"Detection complete — {result.get('features_checked', 0)} features checked")
                st.json(result)

    st.markdown("---")

    # ── Summary KPIs ──────────────────────────────────────────────────────
    summary = get("/drift-logs/summary") or {}
    col1, col2, col3 = st.columns(3)
    col1.metric("Features Tracked", summary.get("total_features", 0))
    col2.metric("Drifted", summary.get("drifted", 0))
    col3.metric("Stable", summary.get("stable", 0))

    st.markdown("---")

    # ── Drift log table + chart ───────────────────────────────────────────
    drift_logs = get("/drift-logs/") or []
    if drift_logs:
        df = pd.DataFrame(drift_logs)

        # Status column
        df["status"] = df["drift_detected"].apply(
            lambda x: "⚠️ DRIFT" if x else "✅ STABLE")

        st.markdown("#### Feature Drift Scores")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="PSI Score", x=df["feature_name"], y=df["psi_score"],
            marker_color="#00c2ff",
        ))
        fig.add_trace(go.Bar(
            name="KS Statistic", x=df["feature_name"], y=df["ks_statistic"],
            marker_color="#ff6b35",
        ))
        fig.add_hline(y=0.20, line_dash="dash", line_color="#ff6b35",
                      annotation_text="PSI threshold (0.20)")
        fig.add_hline(y=0.10, line_dash="dot", line_color="#ffd580",
                      annotation_text="KS threshold (0.10)")
        fig.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2eaf5", family="IBM Plex Mono"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(gridcolor="#1f2d42"),
            yaxis=dict(gridcolor="#1f2d42"),
            margin=dict(t=30, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Drift Log History")
        st.dataframe(
            df[["feature_name", "psi_score", "ks_statistic", "status"]],
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("No drift logs yet. Click **Run Drift Detection** above.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: UPLOAD CSV
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📤 Upload CSV":
    st.markdown("<p class='section-label'>05 — Data Ingestion</p>",
                unsafe_allow_html=True)
    st.title("Upload Patient CSV")
    st.markdown("---")

    st.markdown("""
    **Required columns:** `patient_id`, `age`, `gender`, `bmi`, `condition`
 
    Duplicate `patient_id` values are automatically skipped.
    """)

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file:
        st.markdown("**Preview (first 5 rows):**")
        preview = pd.read_csv(uploaded_file)
        st.dataframe(preview.head(), use_container_width=True, hide_index=True)
        uploaded_file.seek(0)

        if st.button("📤 Upload to Database"):
            with st.spinner("Uploading..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/patients/upload-csv",
                        files={"file": (uploaded_file.name,
                                        uploaded_file, "text/csv")},
                        timeout=30,
                    )
                    result = response.json()
                    if response.status_code == 200:
                        st.success(
                            f"✅ Upload complete — "
                            f"**{result.get('inserted')} inserted**, "
                            f"{result.get('skipped')} skipped, "
                            f"{result.get('total')} total rows"
                        )
                    else:
                        st.error(
                            f"Upload failed: {result.get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error: {e}")
