from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Protocol

import pandas as pd


class MarketDataProvider(Protocol):
    def history(self, ticker: str, period: str) -> pd.DataFrame:
        ...


class DeterministicMarketDataProvider:
    """Small, network-free provider for unit tests and local development."""

    def history(self, ticker: str, period: str = "1mo") -> pd.DataFrame:
        del period
        start = datetime(2024, 1, 2, tzinfo=timezone.utc)
        rows = []
        for index in range(20):
            close = 100.0 + index * 0.5
            rows.append(
                {
                    "Date": start + timedelta(days=index),
                    "Open": close - 1.0,
                    "High": close + 1.0,
                    "Low": close - 2.0,
                    "Close": close,
                    "Adj Close": close,
                    "Volume": 1_000_000 + index * 1_000,
                }
            )
        return pd.DataFrame(rows).set_index("Date")
