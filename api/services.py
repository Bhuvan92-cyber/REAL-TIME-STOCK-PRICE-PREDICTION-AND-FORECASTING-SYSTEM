from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from api.catalog import Stock
from api.config import settings
from modules.feature_engineering import (
    add_lag_features,
    add_technical_indicators,
    add_trend_features,
    add_volatility_features,
)
from modules.ingestion.live_data_fetcher import fetch_live_stock_data
from modules.risk_management.max_drawdown import calculate_max_drawdown
from modules.risk_management.sharpe_ratio import calculate_sharpe_ratio


def _normalise_columns(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result.columns = [str(column).lower() for column in result.columns]
    if "date" in result.columns and "timestamp" not in result.columns:
        result = result.rename(columns={"date": "timestamp"})
    return result


def load_market_data(stock: Stock, period: str = "1y") -> tuple[pd.DataFrame, str]:
    cached = settings.data_dir / "processed" / f"{stock.symbol}_feature_engineered.csv"
    if cached.exists():
        frame = _normalise_columns(pd.read_csv(cached))
        if "close" in frame.columns and len(frame) > 0:
            return frame, "cache"

    frame = fetch_live_stock_data(stock.ticker, interval="1d", period=period)
    frame = _normalise_columns(frame)
    if frame.empty or "close" not in frame.columns:
        raise RuntimeError(f"No market data is available for {stock.symbol}")
    return frame, "yahoo_finance"


def prepare_features(frame: pd.DataFrame) -> pd.DataFrame:
    result = _normalise_columns(frame)
    result = add_trend_features(result)
    result = add_technical_indicators(result)
    result = add_volatility_features(result)
    result = add_lag_features(result, lags=5)
    return result.replace([np.inf, -np.inf], np.nan).dropna()


def market_response_data(frame: pd.DataFrame) -> list[dict]:
    result = prepare_features(frame)
    if "timestamp" not in result.columns:
        result["timestamp"] = pd.date_range(end=datetime.now(timezone.utc), periods=len(result), freq="D")
    candles = []
    for row in result.tail(365).itertuples(index=False):
        values = row._asdict()
        if not all(name in values for name in ("open", "high", "low", "close")):
            continue
        timestamp = pd.to_datetime(values["timestamp"], utc=True).to_pydatetime()
        def optional(name: str):
            value = values.get(name)
            return None if value is None or pd.isna(value) else float(value)
        candles.append({
                "timestamp": timestamp,
                "open": float(values["open"]),
                "high": float(values["high"]),
                "low": float(values["low"]),
                "close": float(values["close"]),
                "volume": float(values.get("volume", 0) or 0),
                "sma_20": optional("sma_20"),
                "ema_20": optional("ema_20"),
                "rsi": optional("rsi"),
                "macd": optional("macd"),
                "macd_signal": optional("macd_signal"),
                "bb_upper": optional("bb_upper"),
                "bb_lower": optional("bb_lower"),
            })
    if not candles:
        raise RuntimeError("Market data did not contain usable OHLC rows")
    return candles


def forecast(stock: Stock, horizon: int, model_name: str) -> tuple[float, list[float], str]:
    frame, source = load_market_data(stock)
    features = prepare_features(frame)
    model_path = settings.model_dir / f"{stock.symbol}_random_forest.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Trained model not found: {model_path}")
    model = joblib.load(model_path)
    expected = getattr(model, "n_features_in_", None)
    latest = features.drop(columns=["close"], errors="ignore").select_dtypes(include="number").tail(1)
    if latest.empty or expected != latest.shape[1]:
        raise RuntimeError(
            f"Feature mismatch for {stock.symbol}: model expects {expected}, received {latest.shape[1]}"
        )
    current = float(features["close"].iloc[-1])
    predictions = [float(model.predict(latest)[0]) for _ in range(horizon)]
    return current, predictions, source


def calculate_risk(frame: pd.DataFrame) -> dict[str, float | int]:
    close = pd.to_numeric(_normalise_columns(frame)["close"], errors="coerce").dropna()
    returns = close.pct_change().dropna().to_numpy()
    cumulative = (1 + returns).cumprod()
    volatility = float(np.std(returns, ddof=1) * np.sqrt(252)) if len(returns) > 1 else 0.0
    return {
        "observations": int(len(returns)),
        "annualized_volatility": volatility,
        "sharpe_ratio": float(calculate_sharpe_ratio(returns) * np.sqrt(252)),
        "max_drawdown": float(calculate_max_drawdown(cumulative)),
    }
