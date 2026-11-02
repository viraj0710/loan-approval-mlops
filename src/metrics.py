"""Prometheus metrics instrumentation for the Loan Approval Prediction system."""
import logging
import threading
from prometheus_client import (
    Counter,
    Histogram,
    Info,
    start_http_server,
)

logger = logging.getLogger(__name__)

# Prometheus Metrics Definitions
PREDICTION_COUNT = Counter(
    "loan_predictions_total",
    "Total count of loan prediction inferences performed",
    ["result", "model_version"],
)

PREDICTION_LATENCY = Histogram(
    "loan_prediction_latency_seconds",
    "Time spent running loan prediction inference in seconds",
    ["model_version"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)

APPROVAL_PROBABILITY = Histogram(
    "loan_approval_probability",
    "Distribution of predicted loan approval probabilities",
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
)

CIBIL_SCORE_DIST = Histogram(
    "loan_applicant_cibil_score",
    "Distribution of applicant CIBIL scores",
    buckets=(300, 400, 500, 600, 700, 800, 900),
)

LOAN_AMOUNT_DIST = Histogram(
    "loan_requested_amount_inr",
    "Distribution of requested loan amounts in INR",
    buckets=(500000, 1000000, 2500000, 5000000, 10000000, 20000000, 50000000),
)

APP_REQUESTS = Counter(
    "loan_app_requests_total",
    "Total user interactions and page visits on the loan approval platform",
    ["action", "status"],
)

MODEL_INFO = Info(
    "loan_model",
    "Metadata and performance specifications of the deployed model",
)
MODEL_INFO.info(
    {
        "model_name": "RandomForestClassifier",
        "version": "1.0.0",
        "accuracy": "0.9778",
        "f1_score": "0.9822",
        "roc_auc": "0.9964",
    }
)

_SERVER_LOCK = threading.Lock()
_SERVER_STARTED = False


def start_metrics_server(port: int = 8000, addr: str = "0.0.0.0") -> bool:
    """Start the Prometheus metrics exporter HTTP server in a daemon thread.

    Safe against repeated calls and port conflicts.
    """
    global _SERVER_STARTED
    with _SERVER_LOCK:
        if _SERVER_STARTED:
            logger.debug(f"Metrics server already marked running on {addr}:{port}")
            return True

        try:
            start_http_server(port=port, addr=addr)
            _SERVER_STARTED = True
            logger.info(f"Prometheus metrics server started on {addr}:{port}/metrics")
            return True
        except OSError as e:
            # Server might already be active on this port in current process or container
            logger.warning(
                f"Metrics server port {port} already bound or unavailable ({e}). Continuing."
            )
            _SERVER_STARTED = True
            return True
        except Exception as e:
            logger.error(f"Failed to start Prometheus metrics server: {e}")
            return False


def is_metrics_server_running() -> bool:
    """Check if the metrics server has been initiated."""
    return _SERVER_STARTED


def record_prediction(
    result: str,
    latency: float,
    approval_prob: float,
    cibil_score: int,
    loan_amount: float,
    model_version: str = "1.0.0",
) -> None:
    """Record a single loan prediction event across all relevant Prometheus metrics."""
    PREDICTION_COUNT.labels(result=result, model_version=model_version).inc()
    PREDICTION_LATENCY.labels(model_version=model_version).observe(latency)
    APPROVAL_PROBABILITY.observe(approval_prob)
    CIBIL_SCORE_DIST.observe(cibil_score)
    LOAN_AMOUNT_DIST.observe(loan_amount)


def record_interaction(action: str, status: str = "success") -> None:
    """Record a UI action or page interaction."""
    APP_REQUESTS.labels(action=action, status=status).inc()
