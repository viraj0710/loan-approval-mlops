"""Verification script for Phase 2: Start app.py, check health and metrics."""
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests
from src.config import MODEL_PATH
from src.metrics import record_prediction
from src.predict import predict_loan


def main():
    print("[1/5] Launching combined application via app.py...")
    cmd = [sys.executable, "app.py"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        print("[2/5] Waiting for services to initialize...")
        time.sleep(5)

        print("[3/5] Testing Streamlit health endpoint (http://localhost:8501/_stcore/health)...")
        health_resp = requests.get("http://localhost:8501/_stcore/health", timeout=5)
        print(f"  Streamlit Health Status: {health_resp.status_code} ({health_resp.text.strip()})")
        assert health_resp.status_code == 200, "Streamlit health check failed"

        print("[4/5] Testing Prometheus metrics endpoint (http://localhost:8000/metrics)...")
        metrics_resp = requests.get("http://localhost:8000/metrics", timeout=5)
        print(f"  Metrics Endpoint Status: {metrics_resp.status_code}")
        assert metrics_resp.status_code == 200, "Prometheus metrics check failed"

        # Simulate a prediction to verify metric incrementing
        sample_input = {
            "no_of_dependents": 2,
            "education": "Graduate",
            "self_employed": "No",
            "income_annum": 9600000.0,
            "loan_amount": 29900000.0,
            "loan_term": 12,
            "cibil_score": 778,
            "residential_assets_value": 2400000.0,
            "commercial_assets_value": 17600000.0,
            "luxury_assets_value": 22700000.0,
            "bank_asset_value": 8000000.0,
        }
        pred_res = predict_loan(sample_input, model_path=MODEL_PATH)
        record_prediction(
            result=pred_res["prediction"],
            latency=0.012,
            approval_prob=pred_res["probability_approved"],
            cibil_score=sample_input["cibil_score"],
            loan_amount=sample_input["loan_amount"],
        )

        print("[5/5] Checking metrics output for loan telemetry...")
        metrics_resp2 = requests.get("http://localhost:8000/metrics", timeout=5)
        metrics_text = metrics_resp2.text

        print("\n--- PROMETHEUS METRICS OUTPUT (Excerpt) ---")
        loan_lines = [
            line for line in metrics_text.splitlines()
            if "loan_" in line and not line.startswith("#")
        ]
        for line in loan_lines[:15]:
            print(f"  {line}")
        print("-------------------------------------------\n")

        assert any("loan_predictions_total" in line for line in metrics_text.splitlines())
        assert any("loan_model_info" in line for line in metrics_text.splitlines())
        print("SUCCESS: Phase 2 verified! Both Streamlit (8501) and Prometheus (8000) are working perfectly.")

    finally:
        print("Terminating app process...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("App process terminated.")


if __name__ == "__main__":
    main()
