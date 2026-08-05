import logging
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

# Fallback intervals
INTERVAL_FALLBACKS = {
    "1m": ["1m", "5m", "15m", "30m", "1h"],
    "5m": ["5m", "15m", "30m", "1h"],
    "15m": ["15m", "30m", "1h"],
    "1h": ["1h", "1d"],
    "1d": ["1d"]
}


def _load_cached_data(ticker: str) -> pd.DataFrame:
    """
    Load cached feature-engineered data if Yahoo fails.
    """

    cache_file = Path(f"data/processed/{ticker}_feature_engineered.csv")

    if cache_file.exists():

        logger.warning(f"Using cached data: {cache_file}")

        df = pd.read_csv(cache_file)

        df.columns = [c.lower() for c in df.columns]

        return df

    return pd.DataFrame()


def fetch_live_stock_data(
    ticker: str,
    interval: str = "1m",
    period: str = "1d",
    retries: int = 3
) -> pd.DataFrame:
    """
    Production-grade Yahoo Finance downloader.

    Features
    --------
    ✓ Uses Ticker.history()
    ✓ Retries failed requests
    ✓ Falls back to larger intervals
    ✓ Uses cached CSV if Yahoo fails
    """

    stock = yf.Ticker(ticker)

    intervals = INTERVAL_FALLBACKS.get(interval, [interval])

    for current_interval in intervals:

        logger.info(
            f"Trying Yahoo Finance: "
            f"{ticker} | {current_interval} | {period}"
        )

        for attempt in range(retries):

            try:

                df = stock.history(
                    period=period,
                    interval=current_interval,
                    auto_adjust=False,
                    prepost=False,
                    actions=False
                )

                if not df.empty:

                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)

                    df.columns = [
                        c.lower()
                        for c in df.columns
                    ]

                    df.reset_index(inplace=True)

                    logger.info(
                        f"Fetched {len(df)} rows "
                        f"using interval={current_interval}"
                    )

                    return df

                logger.warning(
                    f"No data returned "
                    f"({current_interval}, {period})"
                )

            except Exception as e:

                logger.warning(
                    f"Attempt {attempt+1}/{retries} "
                    f"failed ({current_interval}): {e}"
                )

                time.sleep(2)

        logger.info(
            f"Trying fallback interval..."
        )

    logger.error(
        f"Yahoo Finance unavailable for {ticker}"
    )

    cached_df = _load_cached_data(ticker)

    if not cached_df.empty:

        return cached_df

    return pd.DataFrame()
