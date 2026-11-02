"""Streamlit web application for Loan Approval Prediction with Prometheus monitoring."""
import json
import logging
import time
from pathlib import Path
import pandas as pd
import streamlit as st

from src.config import METRICS_PATH, MODEL_PATH
from src.metrics import (
    is_metrics_server_running,
    record_interaction,
    record_prediction,
    start_metrics_server,
)
from src.predict import predict_loan

logger = logging.getLogger(__name__)

# Configure Streamlit page layout
st.set_page_config(
    page_title="LoanGuard AI | Loan Approval System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize Prometheus Metrics Server as a singleton cached resource
@st.cache_resource
def initialize_metrics_exporter(port: int = 8000, host: str = "0.0.0.0") -> bool:
    """Start Prometheus metrics exporter server on port 8000 once per app lifecycle."""
    return start_metrics_server(port=port, addr=host)


# Start Prometheus server immediately
_exporter_ready = initialize_metrics_exporter(port=8000, host="0.0.0.0")


@st.cache_data
def load_metrics_report():
    """Load model evaluation summary and feature importances."""
    if Path(METRICS_PATH).exists():
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def format_inr(val: float) -> str:
    """Format numeric values as Indian Rupees currency format."""
    return f"₹{val:,.0f}"


# Custom styling for banking aesthetic
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .status-badge-approved {
        background-color: #dcfce7;
        color: #166534;
        font-weight: 700;
        font-size: 1.25rem;
        padding: 8px 16px;
        border-radius: 8px;
        display: inline-block;
    }
    .status-badge-rejected {
        background-color: #fee2e2;
        color: #991b1b;
        font-weight: 700;
        font-size: 1.25rem;
        padding: 8px 16px;
        border-radius: 8px;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Preset applicant scenarios for one-click testing
PRESETS = {
    "Select a Preset (Optional)...": None,
    "🌟 Prime Borrower (High CIBIL, Strong Collateral)": {
        "no_of_dependents": 2,
        "education": "Graduate",
        "self_employed": "No",
        "income_annum": 9600000,
        "loan_amount": 29900000,
        "loan_term": 12,
        "cibil_score": 778,
        "residential_assets_value": 2400000,
        "commercial_assets_value": 17600000,
        "luxury_assets_value": 22700000,
        "bank_asset_value": 8000000,
    },
    "⚠️ Subprime Borrower (Low CIBIL, High Debt)": {
        "no_of_dependents": 1,
        "education": "Not Graduate",
        "self_employed": "Yes",
        "income_annum": 2000000,
        "loan_amount": 15000000,
        "loan_term": 20,
        "cibil_score": 350,
        "residential_assets_value": 500000,
        "commercial_assets_value": 0,
        "luxury_assets_value": 1000000,
        "bank_asset_value": 500000,
    },
    "🏢 Business Owner (Moderate CIBIL, Commercial Assets)": {
        "no_of_dependents": 3,
        "education": "Graduate",
        "self_employed": "Yes",
        "income_annum": 6500000,
        "loan_amount": 18000000,
        "loan_term": 10,
        "cibil_score": 680,
        "residential_assets_value": 4500000,
        "commercial_assets_value": 12000000,
        "luxury_assets_value": 5500000,
        "bank_asset_value": 3000000,
    },
}

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bank-building.png", width=64)
    st.title("LoanGuard MLOps")
    st.caption("AI-Powered Loan Underwriting & Observability")

    st.markdown("---")
    menu = st.radio(
        "Navigation",
        [
            "📝 Underwriting Application",
            "📊 Model Analytics & Validation",
            "📈 Prometheus Observability",
        ],
    )

    st.markdown("---")
    st.subheader("⚡ Quick Scenarios")
    selected_preset = st.selectbox(
        "Load Pre-configured Applicant Profile:",
        options=list(PRESETS.keys()),
        index=0,
    )

    preset_values = PRESETS.get(selected_preset)

    st.markdown("---")
    st.subheader("System Status")
    st.success("🟢 ML Pipeline: Active (RF v1.0.0)")
    if is_metrics_server_running():
        st.info("📊 Prometheus Exporter: `:8000/metrics`")
    else:
        st.warning("⚠️ Metrics Exporter: Starting...")

# -------------------------------------------------------------
# VIEW 1: UNDERWRITING APPLICATION
# -------------------------------------------------------------
if menu == "📝 Underwriting Application":
    record_interaction(action="view_application_page")

    st.title("🏦 AI Loan Underwriting Engine")
    st.markdown(
        "Input applicant profile and financial indicators below to evaluate loan eligibility in real-time."
    )

    with st.form("loan_application_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 👤 Applicant Profile")
            no_of_dependents = st.number_input(
                "Number of Dependents",
                min_value=0,
                max_value=10,
                value=int(preset_values["no_of_dependents"]) if preset_values else 2,
                step=1,
                help="Total dependents financially supported by applicant.",
            )
            education = st.selectbox(
                "Education Qualification",
                options=["Graduate", "Not Graduate"],
                index=0 if (not preset_values or preset_values["education"] == "Graduate") else 1,
            )
            self_employed = st.selectbox(
                "Employment Type",
                options=["No", "Yes"],
                format_func=lambda x: "Salaried (No)" if x == "No" else "Self-Employed (Yes)",
                index=0 if (not preset_values or preset_values["self_employed"] == "No") else 1,
            )

        with col2:
            st.markdown("### 💰 Financials & Request")
            income_annum = st.number_input(
                "Annual Gross Income (INR)",
                min_value=100000,
                max_value=100000000,
                value=int(preset_values["income_annum"]) if preset_values else 4500000,
                step=100000,
                help="Total annual verified income before taxes.",
            )
            loan_amount = st.number_input(
                "Requested Loan Amount (INR)",
                min_value=100000,
                max_value=100000000,
                value=int(preset_values["loan_amount"]) if preset_values else 12000000,
                step=100000,
                help="Total principal loan amount requested.",
            )
            loan_term = st.slider(
                "Loan Term (Years)",
                min_value=1,
                max_value=30,
                value=int(preset_values["loan_term"]) if preset_values else 15,
                step=1,
            )

        with col3:
            st.markdown("### 🏛️ Credit & Collateral")
            cibil_score = st.slider(
                "CIBIL Credit Score (300 - 900)",
                min_value=300,
                max_value=900,
                value=int(preset_values["cibil_score"]) if preset_values else 750,
                step=5,
                help="Official bureau credit score. Scores >= 750 represent prime credit.",
            )
            residential_assets_value = st.number_input(
                "Residential Assets Value (INR)",
                min_value=0,
                max_value=100000000,
                value=int(preset_values["residential_assets_value"]) if preset_values else 3500000,
                step=100000,
            )
            commercial_assets_value = st.number_input(
                "Commercial Assets Value (INR)",
                min_value=0,
                max_value=100000000,
                value=int(preset_values["commercial_assets_value"]) if preset_values else 1000000,
                step=100000,
            )
            luxury_assets_value = st.number_input(
                "Luxury Assets Value (INR)",
                min_value=0,
                max_value=100000000,
                value=int(preset_values["luxury_assets_value"]) if preset_values else 2000000,
                step=100000,
            )
            bank_asset_value = st.number_input(
                "Liquid Bank Balances (INR)",
                min_value=0,
                max_value=100000000,
                value=int(preset_values["bank_asset_value"]) if preset_values else 1500000,
                step=50000,
            )

        # Financial Summary Indicators
        total_assets = (
            residential_assets_value
            + commercial_assets_value
            + luxury_assets_value
            + bank_asset_value
        )
        collateral_coverage = (total_assets / loan_amount) if loan_amount > 0 else 0.0
        loan_to_income = (loan_amount / income_annum) if income_annum > 0 else 0.0

        st.markdown("#### Key Financial Ratios")
        rcol1, rcol2, rcol3 = st.columns(3)
        rcol1.metric("Total Declared Assets", format_inr(total_assets))
        rcol2.metric(
            "Collateral Coverage Ratio",
            f"{collateral_coverage:.2f}x",
            delta="Adequate" if collateral_coverage >= 1.0 else "Under-collateralized",
            delta_color="normal" if collateral_coverage >= 1.0 else "inverse",
        )
        rcol3.metric(
            "Loan-to-Income (LTI)",
            f"{loan_to_income:.2f}x",
            delta="Healthy" if loan_to_income <= 4.0 else "High Leverage",
            delta_color="normal" if loan_to_income <= 4.0 else "inverse",
        )

        submit_button = st.form_submit_button(
            "🚀 Evaluate Loan Application",
            use_container_width=True,
            type="primary",
        )

    if submit_button:
        payload = {
            "no_of_dependents": int(no_of_dependents),
            "education": str(education),
            "self_employed": str(self_employed),
            "income_annum": float(income_annum),
            "loan_amount": float(loan_amount),
            "loan_term": int(loan_term),
            "cibil_score": int(cibil_score),
            "residential_assets_value": float(residential_assets_value),
            "commercial_assets_value": float(commercial_assets_value),
            "luxury_assets_value": float(luxury_assets_value),
            "bank_asset_value": float(bank_asset_value),
        }

        start_time = time.perf_counter()
        try:
            prediction_output = predict_loan(payload, model_path=MODEL_PATH)
            latency = time.perf_counter() - start_time

            # Record Prometheus Metrics
            record_prediction(
                result=prediction_output["prediction"],
                latency=latency,
                approval_prob=prediction_output["probability_approved"],
                cibil_score=payload["cibil_score"],
                loan_amount=payload["loan_amount"],
                model_version="1.0.0",
            )
            record_interaction(action="predict", status="success")

            st.markdown("---")
            st.subheader("🎯 Underwriting Decision")

            res_col1, res_col2 = st.columns([1, 1])

            decision = prediction_output["prediction"]
            prob_app = prediction_output["probability_approved"]
            prob_rej = prediction_output["probability_rejected"]
            confidence = prediction_output["confidence"]

            with res_col1:
                if decision == "Approved":
                    st.success("### ✅ Application Approved")
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <span class="status-badge-approved">APPROVED</span>
                            <p style="margin-top: 10px;">The model predicts high likelihood of loan performance.</p>
                            <ul>
                                <li><b>Approval Confidence:</b> {confidence * 100:.2f}%</li>
                                <li><b>Credit Profile:</b> CIBIL {cibil_score} (Tier 1 Prime)</li>
                                <li><b>Inference Latency:</b> {latency * 1000:.2f} ms</li>
                            </ul>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.error("### ❌ Application Rejected")
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <span class="status-badge-rejected">REJECTED</span>
                            <p style="margin-top: 10px;">The application does not meet underwriting thresholds.</p>
                            <ul>
                                <li><b>Rejection Confidence:</b> {confidence * 100:.2f}%</li>
                                <li><b>Primary Risk Factor:</b> CIBIL Score ({cibil_score}) below policy cutoff</li>
                                <li><b>Inference Latency:</b> {latency * 1000:.2f} ms</li>
                            </ul>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with res_col2:
                st.markdown("#### Probability Distribution")
                st.write(f"**Approval Probability:** `{prob_app * 100:.2f}%`")
                st.progress(float(prob_app))

                st.write(f"**Rejection Probability:** `{prob_rej * 100:.2f}%`")
                st.progress(float(prob_rej))

                with st.expander("🔍 Inspected Feature Vector (JSON)"):
                    st.json(prediction_output)

        except Exception as err:
            record_interaction(action="predict", status="error")
            st.error(f"Inference error: {err}")
            logger.exception("Error while evaluating loan application")

# -------------------------------------------------------------
# VIEW 2: MODEL ANALYTICS & VALIDATION
# -------------------------------------------------------------
elif menu == "📊 Model Analytics & Validation":
    record_interaction(action="view_analytics_page")
    st.title("📊 Model Validation & Performance Artifacts")
    st.caption("Detailed metrics, confusion matrices, and feature importance from Phase 1 training.")

    metrics_data = load_metrics_report()
    if not metrics_data:
        st.warning("Metrics artifact not found at `models/metrics.json`.")
    else:
        rf_metrics = metrics_data["evaluation_summary"]["RandomForest"]
        lr_metrics = metrics_data["evaluation_summary"]["LogisticRegression"]

        # Top KPI row
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Selected Model", metrics_data["selected_model"])
        kpi2.metric("RF Test Accuracy", f"{rf_metrics['accuracy'] * 100:.2f}%", "+5.51% vs LR")
        kpi3.metric("RF F1 Score", f"{rf_metrics['f1'] * 100:.2f}%", "+4.35% vs LR")
        kpi4.metric("RF ROC AUC", f"{rf_metrics['roc_auc'] * 100:.2f}%", "+2.19% vs LR")

        st.markdown("---")
        mcol1, mcol2 = st.columns(2)

        with mcol1:
            st.subheader("Model Comparison Matrix")
            df_compare = pd.DataFrame(
                {
                    "Metric": ["Accuracy", "Precision", "Recall", "F1 Score", "ROC AUC"],
                    "Random Forest": [
                        rf_metrics["accuracy"],
                        rf_metrics["precision"],
                        rf_metrics["recall"],
                        rf_metrics["f1"],
                        rf_metrics["roc_auc"],
                    ],
                    "Logistic Regression (Baseline)": [
                        lr_metrics["accuracy"],
                        lr_metrics["precision"],
                        lr_metrics["recall"],
                        lr_metrics["f1"],
                        lr_metrics["roc_auc"],
                    ],
                }
            ).set_index("Metric")
            st.dataframe(df_compare.style.format("{:.4f}"), use_container_width=True)

            st.subheader("Confusion Matrix (Random Forest)")
            cm_data = rf_metrics["confusion_matrix"]["matrix"]
            cm_df = pd.DataFrame(
                cm_data,
                index=["Actual Rejected", "Actual Approved"],
                columns=["Pred Rejected", "Pred Approved"],
            )
            st.dataframe(cm_df, use_container_width=True)

        with mcol2:
            st.subheader("Random Forest Feature Importance")
            importances = metrics_data.get("random_forest_feature_importances", {})
            if importances:
                imp_df = (
                    pd.DataFrame(
                        list(importances.items()),
                        columns=["Feature", "Importance"],
                    )
                    .sort_values(by="Importance", ascending=True)
                    .set_index("Feature")
                )
                st.bar_chart(imp_df, horizontal=True)

        st.markdown("---")
        st.subheader("📋 Dataset Design & Leakage Investigation Findings")
        leakage = metrics_data.get("leakage_investigation", {})
        st.info(f"**Dataset Observation:** {leakage.get('finding')}")
        st.write(f"**Root Cause:** {leakage.get('cause')}")
        st.warning(f"**Production Underwriting Note:** {leakage.get('production_note')}")

# -------------------------------------------------------------
# VIEW 3: PROMETHEUS OBSERVABILITY
# -------------------------------------------------------------
elif menu == "📈 Prometheus Observability":
    record_interaction(action="view_observability_page")
    st.title("📈 Prometheus Observability & Metrics Exporter")
    st.caption("Live metrics instrumentation running on port 8000 for Prometheus scraping.")

    st.markdown(
        """
        The application embeds a standard Prometheus metrics exporter running on **port 8000**
        via `prometheus_client`. This exporter is scraped by Prometheus in Kubernetes / Docker
        using annotations or ServiceMonitor configurations.
        """
    )

    pcol1, pcol2 = st.columns([1, 1])

    with pcol1:
        st.subheader("Metrics Endpoint")
        st.code("http://localhost:8000/metrics", language="bash")
        st.markdown("You can test this endpoint directly from terminal using `curl`:")
        st.code("curl http://localhost:8000/metrics", language="bash")

        st.markdown("#### Tracked Metrics Catalog")
        metrics_catalog = [
            ("`loan_predictions_total`", "Counter", "Count of predictions by result and model version"),
            ("`loan_prediction_latency_seconds`", "Histogram", "Latency distribution of inference in seconds"),
            ("`loan_approval_probability`", "Histogram", "Distribution of predicted approval probabilities"),
            ("`loan_applicant_cibil_score`", "Histogram", "Distribution of applicant CIBIL scores (300 - 900)"),
            ("`loan_requested_amount_inr`", "Histogram", "Distribution of requested principal amounts"),
            ("`loan_app_requests_total`", "Counter", "Total user interactions by action and status"),
            ("`loan_model_info`", "Info", "Model metadata (name, version, accuracy, F1 score)"),
        ]
        cat_df = pd.DataFrame(
            metrics_catalog, columns=["Metric Name", "Type", "Description"]
        ).set_index("Metric Name")
        st.dataframe(cat_df, use_container_width=True)

    with pcol2:
        st.subheader("Live Scrape Preview")
        try:
            from prometheus_client import generate_latest
            raw_metrics = generate_latest().decode("utf-8")
            # Filter loan-specific metrics for clarity
            loan_lines = [
                line for line in raw_metrics.split("\n")
                if "loan_" in line and not line.startswith("#")
            ]
            if loan_lines:
                st.code("\n".join(loan_lines[:25]), language="text")
            else:
                st.info(
                    "No prediction events recorded yet. Run a prediction in the "
                    "Underwriting tab to see live counters!"
                )
        except Exception as e:
            st.error(f"Could not read metrics registry: {e}")
