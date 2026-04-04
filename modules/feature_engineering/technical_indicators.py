import pandas as pd
import numpy as np
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds common technical indicators:
    RSI, MACD, Moving Averages, Bollinger Bands
    """

    logger.info("Adding technical indicators")
    df = df.copy()

    # Moving Averages
    df["sma_20"] = df["close"].rolling(window=20).mean()
    df["ema_20"] = df["close"].ewm(span=20, adjust=False).mean()

    # RSI
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    ema_12 = df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema_12 - ema_26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    rolling_std = df["close"].rolling(window=20).std()
    df["bb_upper"] = df["sma_20"] + (2 * rolling_std)
    df["bb_lower"] = df["sma_20"] - (2 * rolling_std)

    logger.info("Technical indicators added successfully")
    return df
