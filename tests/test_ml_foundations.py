import numpy as np
import pandas as pd

from modules.backtesting.engine import backtest_directional
from modules.evaluation.forecast_metrics import evaluate_forecast
from modules.evaluation.walk_forward import chronological_split
from modules.models.registry import create_model, list_models


def test_metrics_handle_zero_actuals_without_nan():
    metrics = evaluate_forecast([0, 2, 4], [0, 1, 5])
    assert all(np.isfinite(value) for value in metrics.values())
    assert metrics["mape"] == 37.5


def test_chronological_split_preserves_order():
    train, validation, test = chronological_split(np.arange(20))
    assert train[-1] < validation[0] < test[0]


def test_random_forest_registry_model_trains_and_predicts():
    model = create_model("random_forest")
    X = pd.DataFrame({"feature": np.arange(30, dtype=float)})
    y = X["feature"] * 2
    model.train(X, y)
    assert len(model.predict(X.tail(2))) == 2


def test_optional_registry_entries_do_not_break_listing():
    names = {item["name"] for item in list_models()}
    assert {"linear_regression", "random_forest", "xgboost", "lightgbm", "arima", "sarima"} <= names


def test_backtest_applies_costs_and_reports_trades():
    result = backtest_directional([100, 110, 100], [110, 100, 100], transaction_cost=0.01, slippage=0.01)
    assert result["number_of_trades"] >= 1
    assert len(result["returns"]) == 2
