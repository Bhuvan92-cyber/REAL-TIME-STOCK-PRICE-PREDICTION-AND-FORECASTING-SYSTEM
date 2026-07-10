import yfinance as yf
import pandas as pd


def fetch_live_stock_data(ticker, interval="1m", period="1d"):
    try:
        df = yf.download(
            tickers=ticker,
            interval=interval,
            period=period,
            progress=False
        )
    except Exception:
        # Network / JSON decode / rate-limit errors may occur. Return empty DataFrame.
        return pd.DataFrame()

    # If download returned None or invalid type
    if df is None or not hasattr(df, 'columns'):
        return pd.DataFrame()

    # Fix multi-index columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.columns = [c.lower() for c in df.columns]

    df = df.reset_index()

    return df