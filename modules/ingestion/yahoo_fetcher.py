import yfinance as yf
import pandas as pd
from modules.utils.config_loader import load_config
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def fetch_historical(ticker: str, period: str = "5y") -> pd.DataFrame:
    """
    Fetches historical stock data using yfinance.
    Args:
        ticker (str): Stock symbol, e.g., 'AAPL'
        period (str): Time period, default '5y'

    Returns:
        pd.DataFrame: Stock OHLC + Volume data
    """
    try:
        logger.info(f"Fetching Yahoo Finance data for {ticker} for period {period}")
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            logger.warning(f"No data returned for {ticker} from Yahoo Finance")
        return df
    except Exception as e:
        logger.error(f"Error in fetch_historical: {e}")
        raise
