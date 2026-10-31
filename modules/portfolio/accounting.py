from __future__ import annotations

from collections import defaultdict
from datetime import datetime


def account_transactions(transactions: list[dict]) -> dict:
    holdings: dict[str, dict[str, float]] = defaultdict(lambda: {"quantity": 0.0, "cost": 0.0})
    realized = 0.0
    fees = 0.0
    ordered = sorted(transactions, key=lambda row: row.get("executed_at") or "")
    for transaction in ordered:
        symbol = str(transaction["symbol"]).upper()
        side = transaction["side"]
        quantity = float(transaction["quantity"])
        price = float(transaction["price"])
        fee = float(transaction.get("fee", 0) or 0)
        fees += fee
        position = holdings[symbol]
        if side == "buy":
            position["quantity"] += quantity
            position["cost"] += quantity * price + fee
        elif side == "sell":
            if quantity > position["quantity"] + 1e-9:
                raise ValueError(f"Sell quantity exceeds holdings for {symbol}")
            average_cost = position["cost"] / position["quantity"] if position["quantity"] else 0.0
            realized += quantity * (price - average_cost) - fee
            position["quantity"] -= quantity
            position["cost"] -= quantity * average_cost
        else:
            raise ValueError(f"Unsupported transaction side: {side}")
    assets = [
        {
            "symbol": symbol,
            "quantity": round(values["quantity"], 10),
            "invested": values["cost"],
            "average_cost": values["cost"] / values["quantity"] if values["quantity"] else None,
        }
        for symbol, values in sorted(holdings.items())
        if values["quantity"] > 1e-9
    ]
    return {
        "assets": assets,
        "total_invested": sum(asset["invested"] for asset in assets),
        "realized_pnl": realized,
        "fees": fees,
    }


def value_account(account: dict, prices: dict[str, float | None]) -> dict:
    current_value = 0.0
    available = True
    valued_assets = []
    for asset in account["assets"]:
        price = prices.get(asset["symbol"])
        market_value = None if price is None else asset["quantity"] * float(price)
        if market_value is None:
            available = False
        else:
            current_value += market_value
        valued_assets.append({**asset, "price": price, "market_value": market_value})
    unrealized = None if not available else current_value - account["total_invested"]
    return {
        **account,
        "current_value": current_value if available else None,
        "unrealized_pnl": unrealized,
        "total_return": None if unrealized is None else account["realized_pnl"] + unrealized,
        "prices_available": available,
        "assets": valued_assets,
    }


def daily_valuations(
    transactions: list[dict],
    historical_prices: dict[str, dict[str, float]],
) -> list[dict]:
    dates = sorted({date for prices in historical_prices.values() for date in prices})
    result = []
    for date in dates:
        applicable = [
            row for row in transactions
            if (row.get("executed_at") or "")[:10] <= date
        ]
        account = account_transactions(applicable)
        prices = {symbol: values.get(date) for symbol, values in historical_prices.items()}
        valuation = value_account(account, prices)
        result.append({"date": date, "market_value": valuation["current_value"], "invested": account["total_invested"]})
    previous = None
    for row in result:
        value = row["market_value"]
        row["daily_return"] = None if value is None or previous in (None, 0) else value / previous - 1
        row["cumulative_return"] = None if value is None or row["invested"] == 0 else value / row["invested"] - 1
        if value is not None:
            previous = value
    return result
