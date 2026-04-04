import numpy as np   # ← ADD THIS AT THE TOP
import pandas as pd
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def add_trend_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds trend-based features:
    Returns, Log Returns, Trend Direction
    """

    logger.info("Adding trend features")
    df = df.copy()

    # Percentage Returns
    df["returns"] = df["close"].pct_change()

    # Log Returns
    df["log_returns"] = np.log(df["close"] / df["close"].shift(1))

    # Trend Direction (1 = uptrend, -1 = downtrend)
    df["trend_direction"] = df["returns"].apply(
        lambda x: 1 if x > 0 else -1
    )

    logger.info("Trend features added successfully")
    return df
