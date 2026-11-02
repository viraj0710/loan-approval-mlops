"""Script to download the Kaggle Loan Approval Prediction Dataset.

Dataset: https://www.kaggle.com/datasets/architsharma01/loan-approval-prediction-dataset
Target location: data/raw/loan_approval_dataset.csv
"""
import os
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RAW_DATA_DIR, RAW_DATA_FILE

DATASET_SLUG = "architsharma01/loan-approval-prediction-dataset"
MIRROR_URL = (
    "https://raw.githubusercontent.com/AbhishekBiswas-github/AI-Engineer-Projects/"
    "refs/heads/main/Machine-Learning/Loan-Approval-Prediction/loan_approval_dataset.csv"
)


def check_kaggle_credentials() -> bool:
    """Check if Kaggle credentials are configured outside the repository."""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    has_file = kaggle_json.exists()
    has_env = bool(os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"))
    return has_file or has_env


def download_dataset() -> bool:
    """Download dataset from Kaggle or public mirror fallback."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    if RAW_DATA_FILE.exists() and RAW_DATA_FILE.stat().st_size > 0:
        print(f"[OK] Raw dataset already present at {RAW_DATA_FILE} ({RAW_DATA_FILE.stat().st_size} bytes).")
        return True

    if check_kaggle_credentials():
        print(f"Downloading dataset '{DATASET_SLUG}' using official Kaggle API...")
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()
            api.dataset_download_files(DATASET_SLUG, path=str(RAW_DATA_DIR), unzip=True)
            csv_files = list(RAW_DATA_DIR.glob("*.csv"))
            for f in csv_files:
                if f.resolve() != RAW_DATA_FILE.resolve():
                    f.rename(RAW_DATA_FILE)
            if RAW_DATA_FILE.exists():
                print(f"[SUCCESS] Downloaded via Kaggle API to {RAW_DATA_FILE}")
                return True
        except Exception as e:
            print(f"[WARNING] Kaggle API attempt failed: {e}. Falling back to verified dataset mirror...")

    print(f"Downloading dataset from verified public mirror: {MIRROR_URL}...")
    try:
        urllib.request.urlretrieve(MIRROR_URL, str(RAW_DATA_FILE))
        print(f"[SUCCESS] Downloaded dataset to {RAW_DATA_FILE} ({RAW_DATA_FILE.stat().st_size} bytes)")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to download dataset: {e}")
        return False


if __name__ == "__main__":
    success = download_dataset()
    sys.exit(0 if success else 1)
