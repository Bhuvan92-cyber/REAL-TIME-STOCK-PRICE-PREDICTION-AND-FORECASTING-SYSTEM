import pandas as pd
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def add_lag_features(
    df: pd.DataFrame,
    column: str = "close",
    lags: int = 5
) -> pd.DataFrame:
    """
    Adds lag features for a given column.
    """

    logger.info(f"Adding lag features for {column}")
    df = df.copy()

    for lag in range(1, lags + 1):
        df[f"{column}_lag_{lag}"] = df[column].shift(lag)

    logger.info("Lag features added successfully")
    return df
