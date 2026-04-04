import os
import pandas as pd
from modules.utils.logger import get_logger

logger = get_logger(__name__)


def ensure_directory(path: str):
    """
    Ensures directory exists.
    """
    os.makedirs(path, exist_ok=True)


def save_dataframe(df: pd.DataFrame, path: str):
    """
    Append dataframe to CSV file.
    Creates file if it does not exist.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if not os.path.exists(path):
        df.to_csv(path, index=False)
        logger.info(f"Created new file and saved data to {path}")
    else:
        df.to_csv(path, mode="a", header=False, index=False)
        logger.info(f"Appended new data to {path}")


def load_dataframe(path: str) -> pd.DataFrame:
    """
    Generic CSV loader used across the project.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    df = pd.read_csv(path)

    logger.info(f"DataFrame loaded from {path}")

    return df


def load_stock_dataframe(symbol: str) -> pd.DataFrame:
    """
    Load stock data depending on selected symbol.
    """

    DATA_PATH_MAP = {
        "AAPL": "data/raw/realtime/AAPL_live_stream.csv",
        "TCS": "data/raw/historical/TCS_5Y.csv",
        "NIFTY50": "data/raw/historical/NIFTY50_5Y.csv"
    }

    if symbol not in DATA_PATH_MAP:
        raise ValueError(f"Unsupported stock symbol: {symbol}")

    path = DATA_PATH_MAP[symbol]

    df = load_dataframe(path)

    return df


def get_latest_row(df: pd.DataFrame):
    """
    Returns the latest row (used for real-time prediction).
    """
    if df.empty:
        raise ValueError("DataFrame is empty")

    return df.iloc[-1]