import pandas as pd
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handles missing values using forward-fill and backward-fill.
    Suitable for time-series financial data.
    """

    logger.info("Handling missing values")

    df = df.copy()

    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns

    # Forward fill then backward fill (safe for time series)
    df[numeric_cols] = df[numeric_cols].ffill().bfill()

    # Drop remaining rows with missing values (if any)
    df.dropna(inplace=True)

    logger.info("Missing value handling completed")
    return df
