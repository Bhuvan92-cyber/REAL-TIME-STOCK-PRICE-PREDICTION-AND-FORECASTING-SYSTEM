import requests
import pandas as pd
from modules.utils.config_loader import load_config
from modules.utils.logger import get_logger

logger = get_logger(__name__)

CONFIG = load_config()

ALPHA_KEY = CONFIG.get("alpha_vantage_api_key", "")
BASE_URL = "https://www.alphavantage.co/query"

def fetch_daily(ticker: str, outputsize: str = "compact") -> pd.DataFrame:
    """
    Uses Alpha Vantage TIME_SERIES_DAILY_ADJUSTED API to fetch OHLC.
    Args:
        ticker (str): Stock symbol
        outputsize (str): 'compact' (latest) or 'full' (entire history)

    Returns:
        pd.DataFrame: OHLC + adjusted close + volume
    """
    try:
        logger.info(f"Fetching Alpha Vantage data for {ticker}")
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": ticker,
            "apikey": ALPHA_KEY,
            "outputsize": outputsize,
            "datatype": "json"
        }
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()

        data = response.json().get("Time Series (Daily)", {})
        if not data:
            logger.error(f"No data from Alpha Vantage for {ticker}")
            return pd.DataFrame()

        df = pd.DataFrame.from_dict(data, orient="index")
        df.columns = [
            "open",
            "high",
            "low",
            "close",
            "adjusted_close",
            "volume",
            "dividend_amount",
            "split_coefficient"
        ]
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df
    except Exception as e:
        logger.error(f"Error fetching Alpha Vantage data: {e}")
        raise
