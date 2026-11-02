"""Data loading, cleaning, and preprocessing utilities."""
from pathlib import Path
from typing import Tuple, Union
import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import (
    ID_COLUMN,
    NUMERICAL_FEATURES,
    RANDOM_STATE,
    TARGET_COLUMN,
    TEST_SIZE,
)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataframe: strip column names, strip text values, and drop ID column."""
    cleaned = df.copy()

    # Strip column name whitespaces
    cleaned.columns = cleaned.columns.str.strip()

    # Drop ID column if present
    if ID_COLUMN in cleaned.columns:
        cleaned = cleaned.drop(columns=[ID_COLUMN])

    # Strip string values in object columns
    for col in cleaned.select_dtypes(include="object").columns:
        cleaned[col] = cleaned[col].astype(str).str.strip()

    # Cast numerical columns to numeric type
    for col in NUMERICAL_FEATURES:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    # Drop any null rows introduced by bad data
    cleaned = cleaned.dropna()

    return cleaned


def load_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load dataset from CSV and apply cleaning."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found at: {path}")

    raw_df = pd.read_csv(path)
    return clean_data(raw_df)


def split_data(
    df: pd.DataFrame,
    target_column: str = TARGET_COLUMN,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Perform stratified train/test split."""
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' missing from dataset.")

    X = df.drop(columns=[target_column])
    y = df[target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    return X_train, X_test, y_train, y_test
