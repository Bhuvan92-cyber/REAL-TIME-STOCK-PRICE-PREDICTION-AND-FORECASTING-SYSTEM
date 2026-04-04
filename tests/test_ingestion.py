import pandas as pd
from modules.ingestion.yahoo_fetcher import fetch_historical

def test_fetch_historical():
    df = fetch_historical("AAPL", period="1mo")

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Close" in df.columns or "close" in df.columns
