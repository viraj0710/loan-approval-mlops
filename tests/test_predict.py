"""Tests for prediction service and model inference."""
import pytest
from pydantic import ValidationError

from src.config import MODEL_PATH
from src.predict import load_model, predict_loan


@pytest.fixture
def sample_approved_input():
    return {
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


@pytest.fixture
def sample_rejected_input():
    return {
        "no_of_dependents": 1,
        "education": "Not Graduate",
        "self_employed": "Yes",
        "income_annum": 2000000.0,
        "loan_amount": 15000000.0,
        "loan_term": 20,
        "cibil_score": 350,
        "residential_assets_value": 500000.0,
        "commercial_assets_value": 0.0,
        "luxury_assets_value": 1000000.0,
        "bank_asset_value": 500000.0,
    }


def test_predict_approved(sample_approved_input):
    """Test inference on typical approved applicant profile."""
    result = predict_loan(sample_approved_input, model_path=MODEL_PATH)
    assert result["prediction"] == "Approved"
    assert result["probability_approved"] > 0.5
    assert 0.0 <= result["confidence"] <= 1.0


def test_predict_rejected(sample_rejected_input):
    """Test inference on typical rejected applicant profile."""
    result = predict_loan(sample_rejected_input, model_path=MODEL_PATH)
    assert result["prediction"] == "Rejected"
    assert result["probability_rejected"] > 0.5
    assert 0.0 <= result["confidence"] <= 1.0


def test_invalid_cibil_score_validation(sample_approved_input):
    """CIBIL score outside 300-900 must raise ValidationError."""
    bad_data = sample_approved_input.copy()
    bad_data["cibil_score"] = 999  # Invalid
    with pytest.raises(ValidationError):
        predict_loan(bad_data)


def test_negative_loan_amount_validation(sample_approved_input):
    """Negative or zero loan amount must raise ValidationError."""
    bad_data = sample_approved_input.copy()
    bad_data["loan_amount"] = -50000
    with pytest.raises(ValidationError):
        predict_loan(bad_data)


def test_load_committed_model():
    """Verify saved joblib pipeline loads and is ready for inference."""
    model = load_model(MODEL_PATH)
    assert hasattr(model, "predict")
    assert hasattr(model, "predict_proba")
    assert "Approved" in model.classes_
    assert "Rejected" in model.classes_
