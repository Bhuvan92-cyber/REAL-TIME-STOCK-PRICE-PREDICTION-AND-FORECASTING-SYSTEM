import pandas as pd
import pytest
from modules.ingestion.mock_provider import DeterministicMarketDataProvider
from modules.ingestion.yahoo_fetcher import fetch_historical


@pytest.mark.unit
def test_fetch_historical_uses_deterministic_provider():
    df = fetch_historical("AAPL", period="1mo", provider=DeterministicMarketDataProvider())

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Close" in df.columns or "close" in df.columns


@pytest.mark.unit
def test_fetch_historical_handles_empty_provider():
    class EmptyProvider:
        def history(self, ticker: str, period: str) -> pd.DataFrame:
            return pd.DataFrame()

    assert fetch_historical("AAPL", provider=EmptyProvider()).empty


@pytest.mark.unit
def test_fetch_historical_handles_provider_failure():
    class FailingProvider:
        def history(self, ticker: str, period: str) -> pd.DataFrame:
            raise TimeoutError("provider timeout")

    assert fetch_historical("AAPL", provider=FailingProvider()).empty


@pytest.mark.unit
def test_fetch_historical_rejects_malformed_provider_data():
    class MalformedProvider:
        def history(self, ticker: str, period: str) -> pd.DataFrame:
            return pd.DataFrame({"Close": [100.0]})

    assert fetch_historical("AAPL", provider=MalformedProvider()).empty


@pytest.mark.live_external
def test_live_fetch_historical():
    df = fetch_historical("AAPL", period="1mo")
    assert isinstance(df, pd.DataFrame)
