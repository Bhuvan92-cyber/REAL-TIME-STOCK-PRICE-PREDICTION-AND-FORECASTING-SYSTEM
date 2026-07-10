import time
import yfinance as yf
import pandas as pd


def fetch_live_stock_data(ticker, interval="1m", period="1d", max_retries: int = 3, backoff: float = 1.0):
    """Fetch recent price data with retries and a fallback to Ticker.history().

    Returns an empty DataFrame on persistent failure.
    """
    attempt = 0
    while attempt < max_retries:
        try:
            df = yf.download(
                tickers=ticker,
                interval=interval,
                period=period,
                progress=False
            )
        except Exception:
            df = None

        # If we got a valid DataFrame, normalize and return it
        if df is not None and hasattr(df, 'columns') and len(getattr(df, 'columns', [])) > 0:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.columns = [c.lower() for c in df.columns]
            df = df.reset_index()
            return df

        # backoff and retry
        attempt += 1
        time.sleep(backoff * attempt)

    # Final fallback: use Ticker.history() which sometimes succeeds where download() fails
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period, interval=interval)
        if hist is not None and not hist.empty:
            df = hist.copy()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.columns = [c.lower() for c in df.columns]
            df = df.reset_index()
            return df
    except Exception:
        pass

    # Give up — return empty DataFrame
    return pd.DataFrame()