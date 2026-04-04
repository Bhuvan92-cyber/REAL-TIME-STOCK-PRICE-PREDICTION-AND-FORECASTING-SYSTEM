import pandas as pd
from modules.ingestion.live_data_fetcher import fetch_live_stock_data


def load_stock_data(symbol):

    # Apple → live API
    if symbol == "AAPL":
        ticker = "AAPL"
        df = fetch_live_stock_data(ticker)

    # TCS → CSV
    elif symbol == "TCS":
        df = pd.read_csv("data/raw/historical/TCS_5Y.csv")
        df.columns = [c.lower() for c in df.columns]

    # NIFTY → CSV
    elif symbol == "NIFTY50":
        df = pd.read_csv("data/raw/historical/NIFTY50_5Y.csv")
        df.columns = [c.lower() for c in df.columns]

    else:
        raise ValueError("Unsupported stock")

    return df