import yfinance as yf
import pandas as pd
from typing import Optional
from modules.utils.config_loader import load_config
from modules.utils.logger import get_logger
from modules.ingestion.mock_provider import MarketDataProvider

logger = get_logger(__name__)

def fetch_historical(
    ticker: str,
    period: str = "5y",
    provider: Optional[MarketDataProvider] = None,
) -> pd.DataFrame:
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
        if provider is not None:
            df = provider.history(ticker, period)
        else:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
        if not isinstance(df, pd.DataFrame):
            logger.error("Market data provider returned a non-DataFrame for %s", ticker)
            return pd.DataFrame()
        required_columns = {"Open", "High", "Low", "Close", "Volume"}
        if not required_columns.issubset(df.columns):
            logger.error("Market data provider returned malformed columns for %s", ticker)
            return pd.DataFrame()
        if df.empty:
            logger.warning(f"No data returned for {ticker} from Yahoo Finance")
        return df
    except Exception as e:
        logger.error(f"Error in fetch_historical: {e}")
        # Return empty DataFrame to allow callers to handle the absence of data
        return pd.DataFrame()
