"""Configuration constants and paths for Loan Approval Prediction."""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
RAW_DATA_FILE = RAW_DATA_DIR / "loan_approval_dataset.csv"
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "loan_model.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"

# Dataset Specification
TARGET_COLUMN = "loan_status"
ID_COLUMN = "loan_id"

NUMERICAL_FEATURES = [
    "no_of_dependents",
    "income_annum",
    "loan_amount",
    "loan_term",
    "cibil_score",
    "residential_assets_value",
    "commercial_assets_value",
    "luxury_assets_value",
    "bank_asset_value",
]

CATEGORICAL_FEATURES = [
    "education",
    "self_employed",
]

ALL_FEATURE_COLUMNS = NUMERICAL_FEATURES + CATEGORICAL_FEATURES

# Model Parameters
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5
