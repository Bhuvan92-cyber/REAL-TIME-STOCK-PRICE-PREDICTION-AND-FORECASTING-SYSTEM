import logging
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def fetch_live_stock_data(
    ticker: str,
    interval: str = "1m",
    period: str = "1d"
) -> pd.DataFrame:
    """
    Fetch live or latest available market data from Yahoo Finance.

    Parameters
    ----------
    ticker : str
        Yahoo Finance ticker.
    interval : str
        e.g. 1m, 2m, 5m, 15m, 1h, 1d
    period : str
        e.g. 1d, 5d, 1mo

    Returns
    -------
    pd.DataFrame
    """

    try:

        stock = yf.Ticker(ticker)

        df = stock.history(
            period=period,
            interval=interval,
            auto_adjust=False,
            prepost=False
        )

        if df.empty:
            logger.warning(f"No market data returned for {ticker}")
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.columns = [c.lower() for c in df.columns]

        df.reset_index(inplace=True)

        return df

    except Exception as e:

        logger.exception(f"Failed to fetch market data for {ticker}")

        return pd.DataFrame()