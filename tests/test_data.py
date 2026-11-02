"""Tests for data loading, cleaning, and splitting."""
from pathlib import Path
import pandas as pd

from src.data import clean_data, load_data, split_data

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "sample_loans.csv"


def test_clean_data_strips_whitespace():
    """Verify clean_data handles leading and trailing whitespaces."""
    dirty_data = {
        " loan_id": [1, 2],
        " no_of_dependents": [2, 0],
        " education": [" Graduate ", " Not Graduate"],
        " self_employed": [" No ", " Yes"],
        " income_annum": [5000000, 3000000],
        " loan_amount": [15000000, 9000000],
        " loan_term": [10, 15],
        " cibil_score": [750, 420],
        " residential_assets_value": [2000000, 1000000],
        " commercial_assets_value": [1000000, 0],
        " luxury_assets_value": [8000000, 3000000],
        " bank_asset_value": [4000000, 1500000],
        " loan_status": [" Approved ", " Rejected"],
    }
    df_dirty = pd.DataFrame(dirty_data)
    cleaned = clean_data(df_dirty)

    assert "loan_id" not in cleaned.columns
    assert "no_of_dependents" in cleaned.columns
    assert cleaned["education"].tolist() == ["Graduate", "Not Graduate"]
    assert cleaned["self_employed"].tolist() == ["No", "Yes"]
    assert cleaned["loan_status"].tolist() == ["Approved", "Rejected"]


def test_load_data_from_fixture():
    """Test loading and cleaning using the sample fixture."""
    df = load_data(FIXTURE_PATH)
    assert len(df) == 10
    assert "loan_status" in df.columns
    assert "loan_id" not in df.columns


def test_split_data():
    """Test stratified splitting on sample data."""
    df = load_data(FIXTURE_PATH)
    X_train, X_test, y_train, y_test = split_data(df, test_size=0.4, random_state=42)

    assert len(X_train) == 6
    assert len(X_test) == 4
    assert len(y_train) == 6
    assert len(y_test) == 4
    # Check that stratify preserved both classes
    assert "Approved" in y_train.values
    assert "Rejected" in y_train.values
