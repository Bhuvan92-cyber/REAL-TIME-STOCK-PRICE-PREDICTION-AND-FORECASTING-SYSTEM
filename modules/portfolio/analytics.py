from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_portfolio_analytics(
    holdings: list[dict],
    prices: dict[str, float | None],
    historical_prices: dict[str, pd.Series] | None = None,
) -> dict:
    rows = []
    invested = 0.0
    current = 0.0
    for holding in holdings:
        symbol = str(holding["symbol"]).upper()
        quantity = float(holding["quantity"])
        purchase_price = float(holding["purchase_price"])
        cost = quantity * purchase_price
        price = prices.get(symbol)
        value = None if price is None else quantity * float(price)
        invested += cost
        if value is not None:
            current += value
        rows.append({"symbol": symbol, "cost_basis": cost, "market_value": value, "weight": None})
    valued = [row for row in rows if row["market_value"] is not None]
    denominator = sum(row["market_value"] for row in valued)
    for row in rows:
        if row["market_value"] is not None and denominator:
            row["weight"] = row["market_value"] / denominator
    returns = pd.DataFrame()
    if historical_prices:
        series = []
        for holding in holdings:
            symbol = str(holding["symbol"]).upper()
            if symbol in historical_prices:
                series.append(pd.to_numeric(historical_prices[symbol], errors="coerce").pct_change())
        if series:
            returns = pd.concat(series, axis=1).mean(axis=1).dropna()
    return {
        "invested": invested,
        "current_value": current if valued else None,
        "unrealized_pnl": None if not valued else current - invested,
        "return_pct": None if not valued or invested == 0 else (current - invested) / invested * 100,
        "holdings": rows,
        "daily_returns": returns.tolist(),
        "data_available": bool(valued),
    }
