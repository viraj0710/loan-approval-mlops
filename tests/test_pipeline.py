"""Tests for training pipeline, preprocessor, and evaluation."""
from pathlib import Path
from sklearn.pipeline import Pipeline
from src.data import load_data, split_data
from src.train import build_preprocessor, evaluate_model
from sklearn.linear_model import LogisticRegression

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "sample_loans.csv"


def test_build_preprocessor():
    """Verify preprocessor transforms numerical and categorical features."""
    df = load_data(FIXTURE_PATH)
    X = df.drop(columns=["loan_status"])
    preprocessor = build_preprocessor()

    transformed = preprocessor.fit_transform(X)
    # 9 numerical features + 2 binary categorical features (drop='if_binary') = 11 columns
    assert transformed.shape[0] == len(df)
    assert transformed.shape[1] == 11


def test_pipeline_fit_and_evaluate():
    """Test full pipeline fitting and metric calculation on fixture data."""
    df = load_data(FIXTURE_PATH)
    X_train, X_test, y_train, y_test = split_data(df, test_size=0.4, random_state=42)

    pipeline = Pipeline(steps=[
        ("preprocessor", build_preprocessor()),
        ("classifier", LogisticRegression(random_state=42)),
    ])
    pipeline.fit(X_train, y_train)

    metrics = evaluate_model(pipeline, X_test, y_test)
    assert "accuracy" in metrics
    assert "f1" in metrics
    assert "roc_auc" in metrics
    assert "confusion_matrix" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0
