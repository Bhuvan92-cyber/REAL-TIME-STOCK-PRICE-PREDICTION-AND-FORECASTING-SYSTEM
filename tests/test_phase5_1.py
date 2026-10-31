from datetime import datetime, timezone, timedelta

import numpy as np
import pytest

from modules.alerts.engine import evaluate_price_alert
from modules.backtesting.engine import backtest_long_only
from modules.portfolio.accounting import account_transactions, daily_valuations, value_account


def test_transaction_accounting_tracks_average_cost_and_realized_profit():
    account = account_transactions([
        {"symbol": "AAPL", "side": "buy", "quantity": 10, "price": 100, "fee": 2, "executed_at": "2026-01-01"},
        {"symbol": "AAPL", "side": "buy", "quantity": 10, "price": 120, "fee": 2, "executed_at": "2026-01-02"},
        {"symbol": "AAPL", "side": "sell", "quantity": 5, "price": 150, "fee": 1, "executed_at": "2026-01-03"},
    ])
    assert account["assets"][0]["quantity"] == 15
    assert account["assets"][0]["average_cost"] == pytest.approx(110.2)
    assert account["realized_pnl"] == pytest.approx(198)


def test_unavailable_price_is_not_zero():
    account = account_transactions([{"symbol": "AAPL", "side": "buy", "quantity": 2, "price": 100}])
    valued = value_account(account, {"AAPL": None})
    assert valued["current_value"] is None
    assert valued["unrealized_pnl"] is None


def test_daily_valuation_only_uses_available_history():
    result = daily_valuations(
        [{"symbol": "AAPL", "side": "buy", "quantity": 1, "price": 100, "executed_at": "2026-01-01"}],
        {"AAPL": {"2026-01-01": 100, "2026-01-02": 110}},
    )
    assert result[1]["cumulative_return"] == pytest.approx(0.1)


def test_long_only_backtest_uses_next_bar_and_reports_benchmark():
    report = backtest_long_only([100, 110, 120], [1, 1, 0], initial_capital=1000, transaction_cost=0, slippage=0)
    assert report["benchmark_return"] == pytest.approx(0.2)
    assert report["final_value"] == pytest.approx(1200 / 1.1)
    assert report["number_of_trades"] == 2


def test_alert_cooldown_and_inactive_rules():
    now = datetime.now(timezone.utc)
    rule = {"id": "a", "active": True, "condition": "above", "threshold": 100, "cooldown_minutes": 60, "last_triggered_at": now.isoformat()}
    assert not evaluate_price_alert(rule, 101, now + timedelta(minutes=5))
    rule["active"] = False
    assert not evaluate_price_alert(rule, 101, now + timedelta(hours=2))
