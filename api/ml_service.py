from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd

from api.catalog import Stock
from api.services import load_market_data, prepare_features
from api.config import settings
from modules.backtesting.engine import backtest_directional, backtest_long_only
from modules.evaluation.forecast_metrics import evaluate_forecast
from modules.models.registry import create_model, list_models


def _tabular_data(stock: Stock) -> tuple[pd.DataFrame, pd.Series]:
    frame, _ = load_market_data(stock)
    features = prepare_features(frame)
    X = features.drop(columns=["close"], errors="ignore").select_dtypes(include="number")
    y = features["close"]
    if len(X) < 30:
        raise RuntimeError(f"Insufficient feature rows for {stock.symbol}")
    return X, y


def compare_models(stock: Stock) -> list[dict]:
    X, y = _tabular_data(stock)
    split = int(len(X) * 0.8)
    results = []
    for spec in list_models():
        if not spec["available"] or spec["family"] != "regression":
            continue
        try:
            model = create_model(spec["name"])
            model.train(X.iloc[:split], y.iloc[:split])
            predicted = model.predict(X.iloc[split:])
            results.append(
                {
                    "model": spec["name"],
                    "available": True,
                    "trained_at": datetime.now(timezone.utc),
                    "evaluation_period": f"{split}:{len(y)}",
                    **evaluate_forecast(y.iloc[split:], predicted),
                }
            )
        except (RuntimeError, ValueError, ImportError) as exc:
            results.append({"model": spec["name"], "available": False, "reason": str(exc)})
    return results


def forecast_with_model(stock: Stock, model_name: str, horizon: int) -> dict:
    X, y = _tabular_data(stock)
    model = create_model(model_name)
    artifact = settings.model_dir / f"{stock.symbol}_{model_name}.pkl"
    if not artifact.exists():
        raise FileNotFoundError(
            f"No registered artifact for {stock.symbol}/{model_name}; run scripts/train_registered_models.py first"
        )
    model.load(artifact)
    if model_name in {"arima", "sarima"}:
        predictions = np.asarray(model.forecast(steps=horizon), dtype=float).reshape(-1)
    else:
        latest = X.iloc[-1:]
        predictions = np.asarray(model.predict(latest), dtype=float).reshape(-1)
    if predictions.size == 0:
        raise RuntimeError(f"Model {model_name} returned no prediction")
    values = [float(value) for value in predictions[:horizon]]
    if len(values) < horizon:
        values.extend([values[-1]] * (horizon - len(values)))
    return {
        "model": model_name,
        "predictions": values,
        "training_cutoff": datetime.now(timezone.utc),
        "interval_available": False,
        "interval_reason": "No calibrated residual set is registered for this artifact.",
    }


def ensemble_forecast(stock: Stock, horizon: int) -> dict:
    metrics = compare_models(stock)
    available = [item for item in metrics if item.get("available") and item.get("rmse", 0) > 0]
    if not available:
        raise RuntimeError("No validated models are available for an ensemble forecast")
    weights = np.asarray([1 / item["rmse"] for item in available], dtype=float)
    weights /= weights.sum()
    predictions = []
    for item in available:
        predictions.append(forecast_with_model(stock, item["model"], horizon)["predictions"])
    combined = np.average(np.asarray(predictions), axis=0, weights=weights)
    return {
        "model": "ensemble",
        "predictions": combined.tolist(),
        "weights": {item["model"]: float(weight) for item, weight in zip(available, weights)},
        "training_cutoff": datetime.now(timezone.utc),
        "interval_available": False,
        "interval_reason": "No calibrated residual set is registered for this ensemble.",
    }


def backtest_model(
    stock: Stock,
    model_name: str,
    transaction_cost: float,
    slippage: float,
    initial_capital: float = 100000,
    position_size: float = 1.0,
    stop_loss: float | None = None,
    take_profit: float | None = None,
) -> dict:
    X, y = _tabular_data(stock)
    split = int(len(X) * 0.8)
    model = create_model(model_name)
    model.train(X.iloc[:split], y.iloc[:split])
    predictions = model.predict(X.iloc[split:])
    metrics = evaluate_forecast(y.iloc[split:], predictions)
    prices = y.iloc[split:].to_numpy()
    strategy = backtest_directional(prices, predictions, transaction_cost, slippage)
    signals = (predictions > prices).astype(float)
    strategy["long_only"] = backtest_long_only(
        prices,
        signals,
        initial_capital=initial_capital,
        position_size=position_size,
        transaction_cost=transaction_cost,
        slippage=slippage,
        stop_loss=stop_loss,
        take_profit=take_profit,
    )
    return {
        "model": model_name,
        "metrics": metrics,
        "strategy": strategy,
        "evaluation_period": f"{split}:{len(y)}",
        "data_source": "configured market provider",
        "parameters": {
            "initial_capital": initial_capital,
            "position_size": position_size,
            "transaction_cost": transaction_cost,
            "slippage": slippage,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
        },
    }
