import yfinance as yf
import pandas as pd


def fetch_live_stock_data(ticker, interval="1m", period="1d"):

    df = yf.download(
        tickers=ticker,
        interval=interval,
        period=period,
        progress=False
    )

    # Fix multi-index columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.columns = [c.lower() for c in df.columns]

    df.reset_index(inplace=True)

    return df