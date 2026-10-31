"""Train CPU-friendly registered models and write versioned metadata."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from api.catalog import get_stock
from api.config import settings
from api.ml_service import _tabular_data
from modules.evaluation.forecast_metrics import evaluate_forecast
from modules.models.registry import create_model


def train(symbol: str, model_name: str) -> Path:
    X, y = _tabular_data(get_stock(symbol))
    split = int(len(X) * 0.8)
    model = create_model(model_name)
    model.train(X.iloc[:split], y.iloc[:split])
    predictions = model.predict(X.iloc[split:])
    artifact = settings.model_dir / f"{symbol}_{model_name}.pkl"
    model.save(artifact)
    metadata = {
        "symbol": symbol,
        "model": model_name,
        "version": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "feature_count": int(X.shape[1]),
        "rows": int(len(X)),
        "evaluation": evaluate_forecast(y.iloc[split:], predictions),
    }
    artifact.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="AAPL")
    parser.add_argument("--model", default="random_forest")
    args = parser.parse_args()
    print(train(args.symbol, args.model))
