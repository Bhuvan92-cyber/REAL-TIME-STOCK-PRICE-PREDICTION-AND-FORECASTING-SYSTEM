from __future__ import annotations

import numpy as np

from modules.risk_management.max_drawdown import calculate_max_drawdown
from modules.risk_management.sharpe_ratio import calculate_sharpe_ratio


def backtest_directional(
    prices,
    predictions,
    transaction_cost=0.001,
    slippage=0.0005,
):
    actual = np.asarray(prices, dtype=float)
    forecast = np.asarray(predictions, dtype=float)
    if len(actual) != len(forecast) or len(actual) < 2:
        raise ValueError("prices and predictions must have equal length >= 2")
    signal = np.sign(forecast[:-1] - actual[:-1])
    market_returns = np.diff(actual) / actual[:-1]
    turnover = np.abs(np.diff(np.r_[0.0, signal]))
    strategy_returns = signal * market_returns - turnover * (transaction_cost + slippage)
    cumulative = np.cumprod(1 + strategy_returns)
    wins = int(np.sum(strategy_returns > 0))
    positive = strategy_returns[strategy_returns > 0]
    negative = strategy_returns[strategy_returns < 0]
    downside = strategy_returns[strategy_returns < 0]
    sortino = float(np.mean(strategy_returns) / np.std(downside) * np.sqrt(252)) if len(downside) and np.std(downside) else 0.0
    return {
        "cumulative_return": float(cumulative[-1] - 1),
        "max_drawdown": float(calculate_max_drawdown(cumulative)),
        "sharpe_ratio": float(calculate_sharpe_ratio(strategy_returns) * np.sqrt(252)),
        "win_rate": float(wins / len(strategy_returns) * 100),
        "number_of_trades": int(np.sum(turnover > 0)),
        "sortino_ratio": sortino,
        "profit_factor": float(positive.sum() / abs(negative.sum())) if negative.sum() else None,
        "benchmark_return": float(actual[-1] / actual[0] - 1),
        "methodology": "Signals use the previous close and execute on the next close; costs and slippage are charged on position changes.",
        "returns": strategy_returns.tolist(),
    }


def backtest_long_only(
    prices,
    signals,
    *,
    initial_capital: float = 100_000,
    position_size: float = 1.0,
    transaction_cost: float = 0.001,
    slippage: float = 0.0005,
    stop_loss: float | None = None,
    take_profit: float | None = None,
) -> dict:
    actual = np.asarray(prices, dtype=float)
    desired = np.asarray(signals, dtype=float)
    if len(actual) != len(desired) or len(actual) < 2:
        raise ValueError("prices and signals must have equal length >= 2")
    if initial_capital <= 0 or not 0 < position_size <= 1:
        raise ValueError("initial_capital must be positive and position_size must be in (0, 1]")
    cash = float(initial_capital)
    shares = 0.0
    entry_price = None
    equity = [cash]
    trades = []
    for index in range(1, len(actual)):
        price = actual[index]
        previous = actual[index - 1]
        if not np.isfinite(price) or price <= 0:
            raise ValueError("prices must be finite and positive")
        stop = entry_price is not None and stop_loss is not None and price <= entry_price * (1 - stop_loss)
        target = entry_price is not None and take_profit is not None and price >= entry_price * (1 + take_profit)
        should_hold = desired[index - 1] > 0 and not stop and not target
        if shares == 0 and should_hold:
            allocation = cash * position_size
            execution = price * (1 + slippage)
            shares = allocation / execution
            fee = allocation * transaction_cost
            cash -= allocation + fee
            entry_price = execution
            trades.append({"index": index, "side": "buy", "price": execution, "quantity": shares, "fee": fee})
        elif shares and not should_hold:
            execution = price * (1 - slippage)
            proceeds = shares * execution
            fee = proceeds * transaction_cost
            cash += proceeds - fee
            trades.append({"index": index, "side": "sell", "price": execution, "quantity": shares, "fee": fee})
            shares = 0.0
            entry_price = None
        equity.append(cash + shares * price)
    if shares:
        execution = actual[-1] * (1 - slippage)
        proceeds = shares * execution
        fee = proceeds * transaction_cost
        cash += proceeds - fee
        trades.append({"index": len(actual) - 1, "side": "sell", "price": execution, "quantity": shares, "fee": fee})
        equity[-1] = cash
    curve = np.asarray(equity)
    returns = np.diff(curve) / curve[:-1]
    gains = returns[returns > 0]
    losses = returns[returns < 0]
    years = (len(returns) / 252) if len(returns) else 0
    return {
        "initial_capital": initial_capital,
        "final_value": float(curve[-1]),
        "cumulative_return": float(curve[-1] / initial_capital - 1),
        "benchmark_return": float(actual[-1] / actual[0] - 1),
        "max_drawdown": float(calculate_max_drawdown(curve)),
        "sharpe_ratio": float(calculate_sharpe_ratio(returns) * np.sqrt(252)) if len(returns) else 0.0,
        "sortino_ratio": float(np.mean(returns) / np.std(losses) * np.sqrt(252)) if len(losses) and np.std(losses) else 0.0,
        "profit_factor": float(gains.sum() / abs(losses.sum())) if losses.sum() else None,
        "win_rate": float(np.mean(returns > 0) * 100) if len(returns) else 0.0,
        "cagr": float((curve[-1] / initial_capital) ** (1 / years) - 1) if years > 0 else 0.0,
        "number_of_trades": len(trades),
        "trades": trades,
        "equity_curve": curve.tolist(),
        "methodology": "Signals are observed on the prior bar and executed on the current bar with explicit cost, slippage, long-only sizing, and end-of-period liquidation.",
    }
