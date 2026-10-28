import pandas as pd
import pytest
from modules.ingestion.yahoo_fetcher import fetch_historical

@pytest.mark.integration
def test_fetch_historical():
    df = fetch_historical("AAPL", period="1mo")

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Close" in df.columns or "close" in df.columns
