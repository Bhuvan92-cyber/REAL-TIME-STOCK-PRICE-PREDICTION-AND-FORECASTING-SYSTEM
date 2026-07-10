import time
import logging
import pandas as pd
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_live_stock_data(
    ticker,
    interval="1m",
    period="1d",
    max_retries=3,
    backoff=2
):
    """
    Fetch live stock market data from Yahoo Finance.

    Features:
    ---------
    ✓ Automatic retries
    ✓ Multiple fallback intervals
    ✓ Handles MultiIndex columns
    ✓ Works for US & NSE stocks
    ✓ Production ready
    """

    # Different fallback combinations
    fallback_attempts = [
        ("1m", "1d"),
        ("5m", "5d"),
        ("15m", "5d"),
        ("30m", "1mo"),
        ("1h", "1mo"),
        ("1d", "3mo"),
    ]

    # Try requested interval first
    attempts = [(interval, period)]

    # Add fallback attempts (avoid duplicates)
    for item in fallback_attempts:
        if item not in attempts:
            attempts.append(item)

    for current_interval, current_period in attempts:

        logger.info(
            f"Trying Yahoo Finance: "
            f"{ticker} | "
            f"{current_interval} | "
            f"{current_period}"
        )

        retry = 0

        while retry < max_retries:

            try:

                df = yf.download(
                    tickers=ticker,
                    interval=current_interval,
                    period=current_period,
                    progress=False,
                    auto_adjust=True,
                    threads=False,
                    prepost=False,
                )

                # Empty dataframe
                if df is None or df.empty:
                    logger.warning(
                        f"No data returned "
                        f"({current_interval}, {current_period})"
                    )

                    retry += 1
                    time.sleep(backoff * retry)
                    continue

                # MultiIndex -> Single Index
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                # Lowercase columns
                df.columns = [str(c).lower() for c in df.columns]

                # Reset index
                df = df.reset_index()

                logger.info(
                    f"Successfully downloaded "
                    f"{len(df)} rows for {ticker}"
                )

                return df

            except Exception as e:

                logger.exception(
                    f"Yahoo Finance download failed "
                    f"({current_interval}, {current_period})"
                )

                retry += 1
                time.sleep(backoff * retry)

    # --------------------------------------------------------
    # Final fallback using yf.Ticker().history()
    # --------------------------------------------------------

    logger.info("Trying Ticker.history() fallback...")

    try:

        stock = yf.Ticker(ticker)

        df = stock.history(
            period="3mo",
            interval="1d",
            auto_adjust=True
        )

        if df is not None and not df.empty:

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.columns = [str(c).lower() for c in df.columns]

            df = df.reset_index()

            logger.info(
                f"Ticker.history() returned "
                f"{len(df)} rows."
            )

            return df

    except Exception:

        logger.exception("Ticker.history() also failed.")

    logger.error(f"Unable to fetch any data for {ticker}")

    return pd.DataFrame()