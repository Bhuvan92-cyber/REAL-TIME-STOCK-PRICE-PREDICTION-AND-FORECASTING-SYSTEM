import pandas as pd
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def add_volatility_features(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Adds volatility-based features:
    Rolling volatility, High-Low range
    """

    logger.info("Adding volatility features")
    df = df.copy()

    # Rolling volatility (standard deviation of returns)
    df["volatility"] = df["returns"].rolling(window=window).std()

    # Intraday range
    if "high" in df.columns and "low" in df.columns:
        df["high_low_range"] = (df["high"] - df["low"]) / df["close"]

    logger.info("Volatility features added successfully")
    return df
