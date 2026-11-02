"""Prediction and input validation module for Loan Approval model."""
from pathlib import Path
from typing import Any, Dict, Literal, Union
import joblib
import pandas as pd
from pydantic import BaseModel, Field

from src.config import ALL_FEATURE_COLUMNS, MODEL_PATH

_MODEL_CACHE = None


class LoanApplicationInput(BaseModel):
    """Pydantic schema to validate loan application inputs."""

    no_of_dependents: int = Field(ge=0, le=10, description="Number of dependents (0-10)")
    education: Literal["Graduate", "Not Graduate"] = Field(description="Educational qualification")
    self_employed: Literal["Yes", "No"] = Field(description="Employment status")
    income_annum: float = Field(ge=0, description="Annual income in INR")
    loan_amount: float = Field(gt=0, description="Loan amount requested in INR")
    loan_term: int = Field(ge=1, le=40, description="Loan term in years")
    cibil_score: int = Field(ge=300, le=900, description="CIBIL credit score (300 to 900)")
    residential_assets_value: float = Field(ge=0, description="Residential assets value in INR")
    commercial_assets_value: float = Field(ge=0, description="Commercial assets value in INR")
    luxury_assets_value: float = Field(ge=0, description="Luxury assets value in INR")
    bank_asset_value: float = Field(ge=0, description="Bank asset value in INR")


def load_model(path: Union[str, Path] = MODEL_PATH):
    """Load trained pipeline from disk with optional module caching."""
    global _MODEL_CACHE
    model_file = Path(path)
    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found at: {model_file}")

    if _MODEL_CACHE is None:
        _MODEL_CACHE = joblib.load(model_file)
    return _MODEL_CACHE


def predict_loan(
    input_data: Union[Dict[str, Any], LoanApplicationInput],
    model_path: Union[str, Path] = MODEL_PATH,
) -> Dict[str, Any]:
    """Validate input, make inference using trained pipeline, and return prediction & probabilities."""
    # 1. Validation
    if isinstance(input_data, dict):
        validated_input = LoanApplicationInput(**input_data)
    elif isinstance(input_data, LoanApplicationInput):
        validated_input = input_data
    else:
        raise TypeError("input_data must be a dict or LoanApplicationInput instance.")

    # 2. DataFrame formatting
    data_dict = validated_input.model_dump()
    df_input = pd.DataFrame([data_dict])[ALL_FEATURE_COLUMNS]

    # 3. Model Inference
    model = load_model(model_path)
    prediction = model.predict(df_input)[0]
    probabilities = model.predict_proba(df_input)[0]

    classes = list(model.classes_)
    appr_idx = classes.index("Approved")
    prob_approved = float(probabilities[appr_idx])
    prob_rejected = float(probabilities[classes.index("Rejected")])

    return {
        "prediction": str(prediction),
        "probability_approved": round(prob_approved, 4),
        "probability_rejected": round(prob_rejected, 4),
        "confidence": round(max(prob_approved, prob_rejected), 4),
        "input_features": data_dict,
    }
