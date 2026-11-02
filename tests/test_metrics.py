"""Tests for Prometheus metrics instrumentation."""
from prometheus_client import generate_latest

from src.metrics import (
    is_metrics_server_running,
    record_interaction,
    record_prediction,
    start_metrics_server,
)


def test_metrics_definitions():
    """Verify metrics objects and initial registry output."""
    output = generate_latest().decode("utf-8")
    assert "loan_predictions_total" in output
    assert "loan_prediction_latency_seconds" in output
    assert "loan_model_info" in output


def test_record_prediction():
    """Test recording prediction events properly updates metrics."""
    record_prediction(
        result="Approved",
        latency=0.015,
        approval_prob=0.88,
        cibil_score=750,
        loan_amount=5000000.0,
        model_version="1.0.0",
    )

    new_output = generate_latest().decode("utf-8")
    assert 'loan_predictions_total{model_version="1.0.0",result="Approved"}' in new_output
    assert "loan_prediction_latency_seconds_count" in new_output
    assert "loan_applicant_cibil_score_count" in new_output
    assert "loan_requested_amount_inr_count" in new_output


def test_record_interaction():
    """Test UI interaction counter increments."""
    record_interaction(action="test_click", status="success")
    output = generate_latest().decode("utf-8")
    assert 'loan_app_requests_total{action="test_click",status="success"}' in output


def test_start_metrics_server_idempotency():
    """Server initiation should be idempotent and not raise errors on subsequent calls."""
    # Attempt starting
    success = start_metrics_server(port=8000)
    assert success is True
    assert is_metrics_server_running() is True

    # Repeated call should also safely succeed
    repeat_success = start_metrics_server(port=8000)
    assert repeat_success is True
