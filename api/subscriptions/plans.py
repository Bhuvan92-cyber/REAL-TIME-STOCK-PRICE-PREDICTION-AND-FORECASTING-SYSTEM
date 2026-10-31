from __future__ import annotations

from copy import deepcopy


DEFAULT_PLANS = {
    "free": {
        "name": "Free",
        "limits": {
            "forecast_requests": {"period": "day", "value": 20},
            "advanced_model_usage": {"period": "day", "value": 0},
            "backtest_executions": {"period": "day", "value": 5},
            "portfolios": {"period": "total", "value": 1},
            "watchlists": {"period": "total", "value": 2},
            "stock_alerts": {"period": "total", "value": 3},
            "prediction_history": {"period": "total", "value": 50},
            "data_exports": {"period": "month", "value": 0},
            "api_access": {"period": "month", "value": 0},
        },
        "features": ["market_overview", "basic_technical_analysis", "basic_forecasting", "basic_backtesting"],
    },
    "pro": {
        "name": "Pro",
        "limits": {
            "forecast_requests": {"period": "day", "value": 200},
            "advanced_model_usage": {"period": "day", "value": 50},
            "backtest_executions": {"period": "day", "value": 50},
            "portfolios": {"period": "total", "value": 5},
            "watchlists": {"period": "total", "value": 10},
            "stock_alerts": {"period": "total", "value": 25},
            "prediction_history": {"period": "total", "value": 500},
            "data_exports": {"period": "month", "value": 20},
            "api_access": {"period": "month", "value": 0},
        },
        "features": ["advanced_technical_analysis", "advanced_portfolio_analytics", "advanced_backtesting", "exports"],
    },
    "premium": {
        "name": "Premium",
        "limits": {
            "forecast_requests": {"period": "day", "value": 1000},
            "advanced_model_usage": {"period": "day", "value": 500},
            "backtest_executions": {"period": "day", "value": 250},
            "portfolios": {"period": "total", "value": 25},
            "watchlists": {"period": "total", "value": 50},
            "stock_alerts": {"period": "total", "value": 100},
            "prediction_history": {"period": "total", "value": 5000},
            "data_exports": {"period": "month", "value": 100},
            "api_access": {"period": "month", "value": 1000},
        },
        "features": ["ensemble_forecasting", "advanced_model_intelligence", "advanced_portfolio_analytics", "advanced_backtesting", "exports", "api_access"],
    },
}


def default_plans() -> dict:
    return deepcopy(DEFAULT_PLANS)
