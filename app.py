"""Application entrypoint starting both Prometheus metrics server and Streamlit app."""
import logging
from src.metrics import start_metrics_server
from streamlit.web import bootstrap

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app_entrypoint")


def run():
    """Start metrics exporter on port 8000 and run Streamlit UI on port 8501."""
    logger.info("Initializing Prometheus metrics exporter on http://0.0.0.0:8000/metrics")
    start_metrics_server(port=8000, addr="0.0.0.0")

    logger.info("Launching Streamlit application on http://0.0.0.0:8501")
    bootstrap.run(
        "streamlit_app.py",
        is_hello=False,
        args=[],
        flag_options={
            "server.port": 8501,
            "server.address": "0.0.0.0",
            "server.headless": True,
        },
    )


if __name__ == "__main__":
    run()
